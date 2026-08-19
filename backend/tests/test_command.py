import unittest
from unittest.mock import patch
from tools.command import CommandError, SafeCommandRunner
class CommandRunnerTests(unittest.TestCase):
    def test_rejects_non_allowlisted_executable(self):
        with self.assertRaises(CommandError): SafeCommandRunner().run(['bash','-c','echo unsafe'])
    def test_rejects_control_characters(self):
        with self.assertRaises(CommandError): SafeCommandRunner().run(['az','aks\nshow'])
    @patch('tools.command.subprocess.run')
    def test_executes_without_shell(self,run):
        run.return_value.stdout='{}';run.return_value.stderr='';run.return_value.returncode=0;SafeCommandRunner().run_json(['az','account','show']);self.assertFalse(run.call_args.kwargs['shell'])
