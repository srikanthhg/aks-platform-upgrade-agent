from __future__ import annotations
from typing import Any
from tools.command import SafeCommandRunner
from config import get_settings
class Kubectl:
    def __init__(self,runner:SafeCommandRunner|None=None,kubeconfig_path:str|None=None):self.runner=runner or SafeCommandRunner();self.kubeconfig_path=kubeconfig_path
    def get_json(self,*args:str)->Any:
        command=['kubectl'];command += ['--kubeconfig',self.kubeconfig_path] if self.kubeconfig_path else [];command += [*args,'--output','json','--request-timeout=60s'];return self.runner.run_json(command,timeout=get_settings().command_timeout_seconds)
    def version(self):return self.get_json('version')
    def nodes(self):return self.get_json('get','nodes')
    def pods(self):return self.get_json('get','pods','--all-namespaces')
    def pdbs(self):return self.get_json('get','poddisruptionbudgets','--all-namespaces')
    def pvcs(self):return self.get_json('get','persistentvolumeclaims','--all-namespaces')
    def events(self):return self.get_json('get','events','--all-namespaces')
