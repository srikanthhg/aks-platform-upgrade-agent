import unittest
from validation.checks import check_pdbs,check_system_pods,check_warning_events
class ExtendedValidationTests(unittest.TestCase):
    def test_pdb_without_disruption_is_warning(self):self.assertEqual(check_pdbs({'items':[{'metadata':{'name':'api','namespace':'prod'},'status':{'expectedPods':2,'disruptionsAllowed':0}}]})['status'],'WARNING')
    def test_unhealthy_system_pod_fails(self):self.assertEqual(check_system_pods({'items':[{'metadata':{'name':'coredns','namespace':'kube-system'},'status':{'phase':'Pending'}}]})['status'],'FAIL')
    def test_no_warning_events_passes(self):self.assertEqual(check_warning_events({'items':[]})['status'],'PASS')
