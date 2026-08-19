from __future__ import annotations
from typing import Any
from config import get_settings
from tools.command import SafeCommandRunner
class AzureCLI:
    def __init__(self,runner:SafeCommandRunner|None=None,subscription_id:str|None=None):self.runner=runner or SafeCommandRunner();self.subscription_id=subscription_id or get_settings().azure_subscription_id
    def _global(self)->list[str]:return ['--subscription',self.subscription_id] if self.subscription_id else []
    def _json(self,command:list[str],*,timeout:int|None=None)->Any:return self.runner.run_json(['az',*command,*self._global(),'--only-show-errors','--output','json'],timeout=timeout or get_settings().command_timeout_seconds)
    def login_with_managed_identity(self,client_id:str|None=None)->Any:
        command=['login','--identity'];command += ['--client-id',client_id] if client_id else [];return self._json(command)
    def account(self):return self._json(['account','show'])
    def discover_cluster(self,resource_group,cluster_name):return self._json(['aks','show','--resource-group',resource_group,'--name',cluster_name])
    def get_nodepools(self,resource_group,cluster_name):return self._json(['aks','nodepool','list','--resource-group',resource_group,'--cluster-name',cluster_name])
    def get_available_upgrades(self,resource_group,cluster_name):return self._json(['aks','get-upgrades','--resource-group',resource_group,'--name',cluster_name])
    def get_credentials(self,resource_group,cluster_name,kubeconfig_path):self.runner.run(['az','aks','get-credentials','--resource-group',resource_group,'--name',cluster_name,'--file',kubeconfig_path,'--overwrite-existing',*self._global(),'--only-show-errors'],timeout=get_settings().command_timeout_seconds)
    def upgrade_control_plane(self,resource_group,cluster_name,version,*,dry_run):
        if dry_run:return {'status':'DRY_RUN','operation':'control_plane_upgrade','target_version':version}
        return self._json(['aks','upgrade','--resource-group',resource_group,'--name',cluster_name,'--kubernetes-version',version,'--control-plane-only','--yes'],timeout=get_settings().upgrade_timeout_seconds)
    def upgrade_nodepool(self,resource_group,cluster_name,pool_name,version,max_surge,*,dry_run):
        if dry_run:return {'status':'DRY_RUN','operation':'nodepool_upgrade','nodepool':pool_name,'target_version':version,'max_surge':max_surge}
        return self._json(['aks','nodepool','upgrade','--resource-group',resource_group,'--cluster-name',cluster_name,'--name',pool_name,'--kubernetes-version',version,'--max-surge',max_surge,'--yes'],timeout=get_settings().upgrade_timeout_seconds)
