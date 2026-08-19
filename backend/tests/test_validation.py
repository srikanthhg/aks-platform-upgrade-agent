import unittest
from validation.checks import check_nodes,check_pods
class ValidationTests(unittest.TestCase):
    def test_ready_node(self):self.assertEqual(check_nodes({'items':[{'metadata':{'name':'n1'},'status':{'conditions':[{'type':'Ready','status':'True'}]}}]})['status'],'PASS')
    def test_crashloop(self):self.assertEqual(check_pods({'items':[{'metadata':{'name':'p1','namespace':'default'},'status':{'containerStatuses':[{'state':{'waiting':{'reason':'CrashLoopBackOff'}}}]}}]})['status'],'FAIL')
