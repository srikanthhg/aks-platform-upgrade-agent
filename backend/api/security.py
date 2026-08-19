from __future__ import annotations
import hmac
from typing import Any
import jwt
from jwt import PyJWKClient
from fastapi import Header, HTTPException
from config import get_settings

def current_identity(authorization: str|None=Header(default=None), x_api_key: str|None=Header(default=None)) -> dict[str,Any]:
    s=get_settings()
    if s.auth_mode=='api_key':
        if not s.app_api_key or not x_api_key or not hmac.compare_digest(x_api_key,s.app_api_key): raise HTTPException(401,'Invalid API key')
        return {'actor':'api-key-user','roles':[s.entra_required_role]}
    if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401,'Bearer token required')
    token=authorization.split(' ',1)[1]
    issuer=f'https://login.microsoftonline.com/{s.entra_tenant_id}/v2.0'
    jwks=PyJWKClient(f'https://login.microsoftonline.com/{s.entra_tenant_id}/discovery/v2.0/keys')
    try:
        key=jwks.get_signing_key_from_jwt(token).key
        claims=jwt.decode(token,key,algorithms=['RS256'],audience=s.entra_audience,issuer=issuer)
    except Exception as exc: raise HTTPException(401,'Invalid access token') from exc
    roles=list(claims.get('roles',[]))
    if s.entra_required_role and s.entra_required_role not in roles: raise HTTPException(403,'Required application role is missing')
    return {'actor':claims.get('preferred_username') or claims.get('oid') or 'entra-user','roles':roles,'oid':claims.get('oid')}

def require_api_key(authorization: str|None=Header(default=None), x_api_key: str|None=Header(default=None)) -> str:
    return str(current_identity(authorization,x_api_key)['actor'])
