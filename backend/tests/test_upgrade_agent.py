import unittest
from unittest.mock import patch
from agents.upgrade import UpgradeAgent
class FakeCLI:
    def __init__(self,*args,**kwargs):pass
    def upgrade_control_plane(self,*args,**kwargs):return {'status':'DRY_RUN'}
    def upgrade_nodepool(self,*args,**kwargs):return {'status':'DRY_RUN'}
class UpgradeAgentTests(unittest.TestCase):
    @patch('agents.upgrade.validate_target_version')
    @patch('agents.upgrade.AzureCLI',FakeCLI)
    def test_dry_run_never_executes_real_upgrade(self,validate):
        state={'cluster':{'resource_group':'rg','cluster_name':'aks','details':{'kubernetesVersion':'1.31.1'},'available_upgrades':{},'nodepools':[{'name':'systempool'}]},'validation':{'status':'PASS'},'approval':{'approved':False},'upgrade':{'target_version':'1.32.1','dry_run':True,'max_surge':'33%'}};result=UpgradeAgent().run(state);self.assertEqual(result['upgrade']['status'],'DRY_RUN_COMPLETED');self.assertTrue(result['upgrade']['dry_run'])
    def test_warning_requires_approval(self):
        with self.assertRaises(PermissionError):UpgradeAgent().run({'cluster':{},'validation':{'status':'WARNING'},'approval':{'approved':False},'upgrade':{'target_version':'1.32.1','dry_run':True}})
