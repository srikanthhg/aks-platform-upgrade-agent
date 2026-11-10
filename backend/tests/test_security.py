from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import jwt
import pytest
from fastapi import HTTPException

import api.security as security


TENANT_ID = "51abec8d-04c7-4d2b-8c58-b08ddefed419"
AUDIENCE = "api://c7a0ebcc-a736-4a29-ac73-8afa1ca0"
ROLE = "AKS.Upgrade.Operator"


@pytest.mark.parametrize(
    ("version", "issuer", "jwks_uri"),
    [
        (
            "1.0",
            f"https://sts.windows.net/{TENANT_ID}/",
            f"https://login.microsoftonline.com/{TENANT_ID}/discovery/keys",
        ),
        (
            "2.0",
            f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
            f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys",
        ),
    ],
)
def test_current_identity_accepts_supported_entra_token_versions(
    monkeypatch, version, issuer, jwks_uri
):
    settings = SimpleNamespace(
        auth_mode="entra_id",
        entra_tenant_id=TENANT_ID,
        entra_audience=AUDIENCE,
        entra_required_role=ROLE,
    )
    monkeypatch.setattr(security, "get_settings", lambda: settings)

    validated_claims = {
        "iss": issuer,
        "ver": version,
        "tid": TENANT_ID,
        "aud": AUDIENCE,
        "exp": 2_000_000_000,
        "iat": 1_900_000_000,
        "roles": [ROLE],
        "preferred_username": "operator@example.com",
        "oid": "object-id",
    }

    decode = Mock(
        side_effect=[
            {"iss": issuer, "ver": version},
            validated_claims,
        ]
    )
    monkeypatch.setattr(security.jwt, "decode", decode)

    signing_key = object()
    jwks_client = Mock()
    jwks_client.get_signing_key_from_jwt.return_value = SimpleNamespace(key=signing_key)
    client_factory = Mock(return_value=jwks_client)
    monkeypatch.setattr(security, "PyJWKClient", client_factory)

    identity = security.current_identity("Bearer test-token", None)

    assert identity == {
        "actor": "operator@example.com",
        "roles": [ROLE],
        "oid": "object-id",
    }
    client_factory.assert_called_once_with(jwks_uri)
    jwks_client.get_signing_key_from_jwt.assert_called_once_with("test-token")
    assert decode.call_args_list[1].kwargs["audience"] == AUDIENCE
    assert decode.call_args_list[1].kwargs["issuer"] == issuer
    assert decode.call_args_list[1].kwargs["algorithms"] == ["RS256"]


def test_current_identity_rejects_unknown_issuer_before_fetching_keys(monkeypatch):
    settings = SimpleNamespace(
        auth_mode="entra_id",
        entra_tenant_id=TENANT_ID,
        entra_audience=AUDIENCE,
        entra_required_role=ROLE,
    )
    monkeypatch.setattr(security, "get_settings", lambda: settings)
    monkeypatch.setattr(
        security.jwt,
        "decode",
        Mock(return_value={"iss": "https://attacker.example/", "ver": "1.0"}),
    )
    client_factory = Mock()
    monkeypatch.setattr(security, "PyJWKClient", client_factory)

    with pytest.raises(HTTPException) as error:
        security.current_identity("Bearer test-token", None)

    assert error.value.status_code == 401
    assert error.value.detail == "Invalid access token"
    client_factory.assert_not_called()


def test_current_identity_rejects_token_from_different_tenant(monkeypatch):
    settings = SimpleNamespace(
        auth_mode="entra_id",
        entra_tenant_id=TENANT_ID,
        entra_audience=AUDIENCE,
        entra_required_role=ROLE,
    )
    monkeypatch.setattr(security, "get_settings", lambda: settings)
    issuer = f"https://sts.windows.net/{TENANT_ID}/"
    monkeypatch.setattr(
        security.jwt,
        "decode",
        Mock(
            side_effect=[
                {"iss": issuer, "ver": "1.0"},
                {
                    "iss": issuer,
                    "ver": "1.0",
                    "tid": "different-tenant",
                    "aud": AUDIENCE,
                    "roles": [ROLE],
                },
            ]
        ),
    )
    jwks_client = Mock()
    jwks_client.get_signing_key_from_jwt.return_value = SimpleNamespace(key=object())
    monkeypatch.setattr(security, "PyJWKClient", Mock(return_value=jwks_client))

    with pytest.raises(HTTPException) as error:
        security.current_identity("Bearer test-token", None)

    assert error.value.status_code == 401


def test_current_identity_returns_forbidden_when_required_role_is_missing(monkeypatch):
    settings = SimpleNamespace(
        auth_mode="entra_id",
        entra_tenant_id=TENANT_ID,
        entra_audience=AUDIENCE,
        entra_required_role=ROLE,
    )
    monkeypatch.setattr(security, "get_settings", lambda: settings)
    issuer = f"https://sts.windows.net/{TENANT_ID}/"
    monkeypatch.setattr(
        security.jwt,
        "decode",
        Mock(
            side_effect=[
                {"iss": issuer, "ver": "1.0"},
                {
                    "iss": issuer,
                    "ver": "1.0",
                    "tid": TENANT_ID,
                    "aud": AUDIENCE,
                    "roles": [],
                },
            ]
        ),
    )
    jwks_client = Mock()
    jwks_client.get_signing_key_from_jwt.return_value = SimpleNamespace(key=object())
    monkeypatch.setattr(security, "PyJWKClient", Mock(return_value=jwks_client))

    with pytest.raises(HTTPException) as error:
        security.current_identity("Bearer test-token", None)

    assert error.value.status_code == 403
    assert error.value.detail == "Required application role is missing"
