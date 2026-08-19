import unittest
from pydantic import ValidationError
from api.models import StartWorkflowRequest
class RequestModelTests(unittest.TestCase):
    def test_accepts_safe_payload(self): self.assertTrue(StartWorkflowRequest(resource_group='rg-test',cluster_name='aks-test',target_version='1.32.7').dry_run)
    def test_rejects_invalid_version(self):
        with self.assertRaises(ValidationError):StartWorkflowRequest(resource_group='rg-test',cluster_name='aks-test',target_version='latest')
    def test_rejects_command_like_cluster_name(self):
        with self.assertRaises(ValidationError):StartWorkflowRequest(resource_group='rg-test',cluster_name='aks;rm',target_version='1.32.7')
