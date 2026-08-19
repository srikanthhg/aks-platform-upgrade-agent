from __future__ import annotations
from typing import Any
from config import get_settings
from tools.azure_cli import AzureCLI
from tools.kubectl import Kubectl
from validation.checks import check_nodes,check_pdbs,check_pods,check_pvcs,check_system_pods,check_warning_events
class ValidationAgent:
    def run(self,state:dict[str,Any])->dict[str,Any]:
        cluster=state['cluster']; settings=get_settings(); thread_id=state.get('workflow',{}).get('thread_id','unknown')
        kubeconfig=settings.kubeconfig_directory/f'{thread_id}.yaml'
        cli=AzureCLI(subscription_id=cluster.get('subscription_id')); cli.get_credentials(cluster['resource_group'],cluster['cluster_name'],str(kubeconfig))
        kubectl=Kubectl(kubeconfig_path=str(kubeconfig)); pods=kubectl.pods()
        checks=[check_nodes(kubectl.nodes()),check_pods(pods),check_system_pods(pods),check_pdbs(kubectl.pdbs()),check_pvcs(kubectl.pvcs()),check_warning_events(kubectl.events())]
        statuses={c['status'] for c in checks}; status='FAIL' if 'FAIL' in statuses else 'WARNING' if 'WARNING' in statuses else 'PASS'
        return {'validation':{'status':status,'healthy':status!='FAIL','checks':checks,'warnings':[c for c in checks if c['status']=='WARNING'],'errors':[c for c in checks if c['status']=='FAIL']}}
