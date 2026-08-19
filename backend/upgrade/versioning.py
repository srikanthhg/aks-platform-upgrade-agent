from __future__ import annotations
import re
_VERSION=re.compile(r'^(\d+)\.(\d+)(?:\.(\d+))?$')
def normalize_version(value:str)->tuple[int,int,int]:
    match=_VERSION.fullmatch(value.strip().lstrip('v'))
    if not match:raise ValueError(f'Invalid Kubernetes version: {value}')
    major,minor,patch=match.groups();return int(major),int(minor),int(patch or 0)
def is_version_greater(target:str,current:str)->bool:return normalize_version(target)>normalize_version(current)
def extract_allowed_versions(payload:dict)->set[str]:
    allowed=set()
    for upgrade in payload.get('controlPlaneProfile',{}).get('upgrades',[]) or []:
        if upgrade.get('kubernetesVersion'):allowed.add(upgrade['kubernetesVersion'])
    return allowed
def validate_target_version(current:str,target:str,upgrades:dict)->None:
    if not is_version_greater(target,current):raise ValueError('Target version must be greater than current version.')
    allowed=extract_allowed_versions(upgrades)
    if allowed and target not in allowed:raise ValueError(f'Target version {target} is not in Azure supported upgrades: {sorted(allowed)}')
