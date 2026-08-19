#!/usr/bin/env python3
from pathlib import Path
import sys,argparse,json,shutil
BACKEND_DIR=Path(__file__).resolve().parents[1]/'backend';sys.path.insert(0,str(BACKEND_DIR))
from config import get_settings
from tools.azure_cli import AzureCLI
from tools.kubectl import Kubectl
def main():
 p=argparse.ArgumentParser();p.add_argument('--resource-group',required=True);p.add_argument('--cluster-name',required=True);p.add_argument('--subscription-id');p.add_argument('--managed-identity',action='store_true');a=p.parse_args();checks=[]
 for e in ('az','kubectl'):checks.append({'check':f'{e}_installed','passed':bool(shutil.which(e))})
 if not all(x['passed'] for x in checks):print(json.dumps(checks,indent=2));return 2
 s=get_settings();cli=AzureCLI(subscription_id=a.subscription_id)
 if a.managed_identity:cli.login_with_managed_identity(s.azure_managed_identity_client_id)
 cluster=cli.discover_cluster(a.resource_group,a.cluster_name);cli.get_credentials(a.resource_group,a.cluster_name,str(s.kubeconfig_directory/'preflight.yaml'));nodes=Kubectl(kubeconfig_path=str(s.kubeconfig_directory/'preflight.yaml')).nodes();checks.append({'check':'aks','passed':True,'details':{'version':cluster.get('kubernetesVersion'),'nodes':len(nodes.get('items',[]))}});print(json.dumps(checks,indent=2));return 0
if __name__=='__main__':sys.exit(main())
