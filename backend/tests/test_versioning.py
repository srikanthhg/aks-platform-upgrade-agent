import unittest
from upgrade.versioning import normalize_version,is_version_greater,extract_allowed_versions
class VersioningTests(unittest.TestCase):
    def test_normalize(self):self.assertEqual(normalize_version('v1.32.7'),(1,32,7))
    def test_greater(self):self.assertTrue(is_version_greater('1.32.1','1.31.9'))
    def test_extract(self):self.assertEqual(extract_allowed_versions({'controlPlaneProfile':{'upgrades':[{'kubernetesVersion':'1.32.7'}]}}),{'1.32.7'})
