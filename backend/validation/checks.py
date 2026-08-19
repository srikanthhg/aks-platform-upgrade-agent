from __future__ import annotations
from datetime import datetime,timedelta,timezone
from typing import Any
def result(name,status,message,details=None):return {'name':name,'status':status,'message':message,'details':details or []}
def check_nodes(payload):
    bad=[]
    for node in payload.get('items',[]):
        ready=next((c for c in node.get('status',{}).get('conditions',[]) if c.get('type')=='Ready'),{})
        if ready.get('status')!='True' or node.get('spec',{}).get('unschedulable',False):bad.append({'node':node.get('metadata',{}).get('name'),'ready':ready.get('status'),'unschedulable':node.get('spec',{}).get('unschedulable',False)})
    return result('Nodes Ready','FAIL' if bad else 'PASS','All nodes are Ready and schedulable.' if not bad else 'One or more nodes are not Ready or are unschedulable.',bad)
def check_pods(payload):
    bad=[];blocked={'CrashLoopBackOff','ImagePullBackOff','ErrImagePull','CreateContainerError','RunContainerError'}
    for pod in payload.get('items',[]):
        if pod.get('status',{}).get('phase')=='Failed':bad.append({'namespace':pod.get('metadata',{}).get('namespace'),'pod':pod.get('metadata',{}).get('name'),'reason':pod.get('status',{}).get('reason') or 'Failed'})
        for container in pod.get('status',{}).get('containerStatuses',[]) or []:
            reason=container.get('state',{}).get('waiting',{}).get('reason')
            if reason in blocked:bad.append({'namespace':pod.get('metadata',{}).get('namespace'),'pod':pod.get('metadata',{}).get('name'),'container':container.get('name'),'reason':reason})
    return result('Pod Health','FAIL' if bad else 'PASS','No blocking pod states found.' if not bad else 'Blocking pod states detected.',bad)
def check_system_pods(payload):
    bad=[{'pod':p.get('metadata',{}).get('name'),'phase':p.get('status',{}).get('phase')} for p in payload.get('items',[]) if p.get('metadata',{}).get('namespace')=='kube-system' and p.get('status',{}).get('phase') not in {'Running','Succeeded'}];return result('kube-system Health','FAIL' if bad else 'PASS','All kube-system pods are healthy.' if not bad else 'Unhealthy kube-system pods detected.',bad)
def check_pvcs(payload):
    bad=[{'namespace':x.get('metadata',{}).get('namespace'),'pvc':x.get('metadata',{}).get('name'),'phase':x.get('status',{}).get('phase')} for x in payload.get('items',[]) if x.get('status',{}).get('phase')!='Bound'];return result('PVC Health','WARNING' if bad else 'PASS','All PVCs are Bound.' if not bad else 'Some PVCs are not Bound.',bad)
def check_pdbs(payload):
    bad=[]
    for pdb in payload.get('items',[]):
        status=pdb.get('status',{});expected=int(status.get('expectedPods') or 0);disruptions=int(status.get('disruptionsAllowed') or 0)
        if expected>0 and disruptions<1:bad.append({'namespace':pdb.get('metadata',{}).get('namespace'),'pdb':pdb.get('metadata',{}).get('name'),'expectedPods':expected,'disruptionsAllowed':disruptions})
    return result('Pod Disruption Budgets','WARNING' if bad else 'PASS','PDBs allow at least one disruption or match no pods.' if not bad else 'Some PDBs may block node draining.',bad)
def check_warning_events(payload,lookback_hours=1):
    cutoff=datetime.now(timezone.utc)-timedelta(hours=lookback_hours);bad=[]
    for event in payload.get('items',[]):
        if event.get('type')!='Warning':continue
        raw=event.get('eventTime') or event.get('lastTimestamp')
        if raw:
            try:
                if datetime.fromisoformat(raw.replace('Z','+00:00'))<cutoff:continue
            except ValueError:pass
        bad.append({'namespace':event.get('metadata',{}).get('namespace'),'reason':event.get('reason'),'message':(event.get('message') or '')[:300]})
    return result('Recent Warning Events','WARNING' if bad else 'PASS',f'No warning events found in the last {lookback_hours} hour(s).' if not bad else 'Recent Kubernetes warning events were found.',bad[:100])
