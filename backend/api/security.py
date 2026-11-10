from __future__ import annotations

import hmac
import logging
from typing import Any

import jwt
from fastapi import Header, HTTPException
from jwt import PyJWKClient

from config import get_settings


logger = logging.getLogger(__name__)


def _entra_token_metadata(token: str, tenant_id: str) -> tuple[str, str]:
    """Return the trusted issuer and JWKS URL for a supported Entra token version.

    The unverified claims are used only to select between the two known Entra
    issuer formats. The selected issuer, signature, audience, and tenant are
    all validated again by jwt.decode below.
    """
    unverified_claims = jwt.decode(
        token,
        options={
            "verify_signature": False,
            "verify_aud": False,
            "verify_iss": False,
        },
    )
    token_issuer = unverified_claims.get("iss")
    token_version = unverified_claims.get("ver")

    v1_issuer = f"https://sts.windows.net/{tenant_id}/"
    v2_issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"

    if token_version == "1.0" and token_issuer == v1_issuer:
        return v1_issuer, f"https://login.microsoftonline.com/{tenant_id}/discovery/keys"

    if token_version == "2.0" and token_issuer == v2_issuer:
        return v2_issuer, f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"

    raise ValueError("Unsupported Microsoft Entra token issuer or version")


def current_identity(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> dict[str, Any]:
    settings = get_settings()

    if settings.auth_mode == "api_key":
        if (
            not settings.app_api_key
            or not x_api_key
            or not hmac.compare_digest(x_api_key, settings.app_api_key)
        ):
            raise HTTPException(status_code=401, detail="Invalid API key")
        return {"actor": "api-key-user", "roles": [settings.entra_required_role]}

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Bearer token required")

    stage = "configuration"
    try:
        if not settings.entra_tenant_id or not settings.entra_audience:
            raise ValueError("Microsoft Entra tenant and audience must be configured")

        stage = "token_metadata"
        expected_issuer, jwks_uri = _entra_token_metadata(token, settings.entra_tenant_id)

        stage = "signing_key_retrieval"
        signing_key = PyJWKClient(jwks_uri).get_signing_key_from_jwt(token).key

        stage = "jwt_validation"
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.entra_audience,
            issuer=expected_issuer,
            options={"require": ["exp", "iat", "iss", "aud", "tid"]},
        )

        stage = "tenant_validation"
        # The issuer is tenant-specific, and this additional check ensures the
        # token's tenant claim agrees with the configured tenant as well.
        if str(claims.get("tid", "")).lower() != settings.entra_tenant_id.lower():
            raise ValueError("Token tenant does not match configured tenant")
    except Exception as exc:
        # Deliberately log only the validation stage and exception details.
        # Never log the bearer token, authorization header, or decoded claims.
        logger.warning(
            "Microsoft Entra authentication failed: stage=%s error_type=%s error=%s",
            stage,
            type(exc).__name__,
            str(exc),
        )
        raise HTTPException(status_code=401, detail="Invalid access token") from exc

    roles = list(claims.get("roles", []))
    if settings.entra_required_role and settings.entra_required_role not in roles:
        logger.info("Microsoft Entra authorization denied: required application role is missing")
        raise HTTPException(status_code=403, detail="Required application role is missing")

    return {
        "actor": claims.get("preferred_username") or claims.get("oid") or "entra-user",
        "roles": roles,
        "oid": claims.get("oid"),
    }


def require_api_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> str:
    return str(current_identity(authorization, x_api_key)["actor"])
