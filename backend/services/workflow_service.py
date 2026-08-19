from __future__ import annotations
import uuid
from typing import Any
from langgraph.types import Command
from graph.runtime import graph_mutex
from graph.workflow import aks_upgrade_graph
from services.job_queue import JobQueue
from services.locks import ClusterLockConflict, ClusterLockStore
from tools.audit import write_audit
class WorkflowNotFoundError(RuntimeError): pass
class WorkflowConflictError(RuntimeError): pass
class WorkflowService:
    def __init__(self,lock_store:ClusterLockStore|None=None,queue:JobQueue|None=None): self.lock_store=lock_store or ClusterLockStore(); self.queue=queue or JobQueue()
    @staticmethod
    def config(thread_id:str)->dict[str,Any]: return {'configurable':{'thread_id':thread_id}}
    @staticmethod
    def _cluster_key(payload:dict[str,Any])->str:return f"{payload.get('subscription_id') or 'default'}:{payload['resource_group']}:{payload['cluster_name']}".lower()
    def start(self,payload:dict[str,Any],actor:str)->dict[str,Any]:
        thread_id=str(uuid.uuid4()); cluster_key=self._cluster_key(payload)
        try:self.lock_store.acquire(cluster_key,thread_id)
        except ClusterLockConflict as exc:raise WorkflowConflictError(str(exc)) from exc
        state={'cluster':{'resource_group':payload['resource_group'],'cluster_name':payload['cluster_name'],'subscription_id':payload.get('subscription_id')},'validation':{},'approval':{'status':'NOT_REQUESTED','approved':False},'upgrade':{'target_version':payload['target_version'],'dry_run':payload.get('dry_run',True),'max_surge':payload.get('max_surge','33%')},'reports':{},'notifications':{},'workflow':{'status':'QUEUED','current_step':'queued','thread_id':thread_id},'error':None}
        try:
            self.queue.enqueue(thread_id,'start',{'state':state,'actor':actor,'cluster_key':cluster_key}); write_audit('workflow_queued',actor=actor,details={'thread_id':thread_id,'cluster_key':cluster_key,'dry_run':state['upgrade']['dry_run'],'status':'QUEUED'}); return {'thread_id':thread_id,'status':'QUEUED','paused':False,'next_nodes':['worker'],'interrupt':[],'state':state}
        except Exception:self.lock_store.release(thread_id);raise
    def get(self,thread_id:str)->dict[str,Any]:
        with graph_mutex:snapshot=aks_upgrade_graph.get_state(self.config(thread_id))
        job=self.queue.latest(thread_id)
        if not snapshot.values:
            if not job:raise WorkflowNotFoundError(thread_id)
            status={'queued':'QUEUED','running':'RUNNING','failed':'FAILED','completed':'STARTING'}.get(job['status'],job['status'].upper()); return {'thread_id':thread_id,'status':status,'paused':False,'next_nodes':['worker'] if job['status'] in ('queued','running') else [],'interrupt':[],'state':{'workflow':{'status':status,'current_step':'worker_queue'},'error':job.get('error')}}
        state=dict(snapshot.values);paused='approval' in snapshot.next; status='WAITING_FOR_APPROVAL' if paused else state.get('workflow',{}).get('status','UNKNOWN')
        if job and job['status'] in ('queued','running') and job['job_type']=='resume':status='APPROVAL_QUEUED'
        return {'thread_id':thread_id,'status':status,'paused':paused,'next_nodes':list(snapshot.next),'interrupt':[],'state':state}
    def resume(self,thread_id:str,approved:bool,operator:str,comment:str|None)->dict[str,Any]:
        current=self.get(thread_id)
        if not current['paused']:raise WorkflowConflictError('Workflow is not waiting for approval.')
        latest=self.queue.latest(thread_id)
        if latest and latest['job_type']=='resume' and latest['status'] in ('queued','running'):raise WorkflowConflictError('An approval decision is already queued.')
        self.lock_store.refresh(thread_id);self.queue.enqueue(thread_id,'resume',{'approved':approved,'operator':operator,'comment':comment});write_audit('workflow_approval_queued',actor=operator,details={'thread_id':thread_id,'approved':approved,'comment':comment,'status':'APPROVAL_QUEUED'});current['status']='APPROVAL_QUEUED';return current
    def execute_job(self,job:dict[str,Any]):
        thread_id=job['thread_id'];payload=job['payload'];job_type=job['job_type']
        if job_type=='start':
            with graph_mutex:result=aks_upgrade_graph.invoke(payload['state'],config=self.config(thread_id))
        elif job_type=='resume':
            self.lock_store.refresh(thread_id)
            with graph_mutex:result=aks_upgrade_graph.invoke(Command(resume={'approved':payload['approved'],'approved_by':payload['operator'],'comment':payload.get('comment')}),config=self.config(thread_id))
        else:raise ValueError(f'Unsupported job type: {job_type}')
        response=self._response(thread_id,result);self._release_if_terminal(thread_id,response);write_audit('workflow_job_completed',actor=payload.get('actor') or payload.get('operator') or 'worker',details={'thread_id':thread_id,'job_type':job_type,'status':response['status']})
    def fail_job(self,job:dict[str,Any],error:str): self.lock_store.release(job['thread_id']);write_audit('workflow_job_failed',actor='worker',details={'thread_id':job['thread_id'],'job_type':job['job_type'],'error':error,'status':'FAILED'})
    def _release_if_terminal(self,thread_id:str,response:dict[str,Any]):
        if not response['paused'] and not response['next_nodes']:self.lock_store.release(thread_id)
    def _response(self,thread_id:str,result:dict[str,Any])->dict[str,Any]:
        interrupts=[getattr(item,'value',item) for item in result.get('__interrupt__',[])];paused=bool(interrupts);status='WAITING_FOR_APPROVAL' if paused else result.get('workflow',{}).get('status',result.get('upgrade',{}).get('status','UNKNOWN'))
        with graph_mutex:snapshot=aks_upgrade_graph.get_state(self.config(thread_id))
        return {'thread_id':thread_id,'status':status,'paused':paused,'next_nodes':list(snapshot.next),'interrupt':interrupts,'state':result}
