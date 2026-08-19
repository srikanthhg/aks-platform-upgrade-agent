from __future__ import annotations
import json,os,subprocess
from dataclasses import dataclass
from typing import Any,Mapping,Sequence
@dataclass(frozen=True)
class CommandResult:stdout:str;stderr:str;returncode:int
class CommandError(RuntimeError):pass
class SafeCommandRunner:
    ALLOWED_EXECUTABLES={'az','kubectl'}
    def run(self,command:Sequence[str],*,timeout:int=300,env:Mapping[str,str]|None=None)->CommandResult:
        if not command or command[0] not in self.ALLOWED_EXECUTABLES:raise CommandError('Executable is not allowlisted.')
        if any('\n' in value or '\r' in value or '\x00' in value for value in command):raise CommandError('Command contains an invalid control character.')
        merged_env=os.environ.copy();merged_env.update(env or {})
        try:completed=subprocess.run(list(command),capture_output=True,text=True,timeout=timeout,check=False,shell=False,env=merged_env)
        except subprocess.TimeoutExpired as exc:raise CommandError(f'Command timed out after {timeout} seconds.') from exc
        except OSError as exc:raise CommandError(f'Unable to execute {command[0]}: {exc}') from exc
        result=CommandResult(completed.stdout.strip(),completed.stderr.strip(),completed.returncode)
        if result.returncode!=0:raise CommandError(f'Command failed ({result.returncode}): {(result.stderr or result.stdout or "No error output.")[:4000]}')
        return result
    def run_json(self,command:Sequence[str],*,timeout:int=300,env:Mapping[str,str]|None=None)->Any:
        result=self.run(command,timeout=timeout,env=env)
        if not result.stdout:return {}
        try:return json.loads(result.stdout)
        except json.JSONDecodeError as exc:raise CommandError('Command did not return valid JSON.') from exc
