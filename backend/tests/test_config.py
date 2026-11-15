from __future__ import annotations

from urllib.parse import urlsplit

import pytest
from pydantic import ValidationError

from config import Settings


def test_builds_database_url_from_separate_postgres_settings():
    settings = Settings(
        _env_file=None,
        app_environment="production",
        auth_mode="entra_id",
        entra_tenant_id="tenant-id",
        entra_audience="api://api-client-id",
        postgres_host="my-postgres.postgres.database.azure.com",
        postgres_port=5432,
        postgres_db="aks_upgrade_agent",
        postgres_user="agent@user",
        postgres_password="p@ss:/word#?",
        postgres_sslmode="require",
    )

    parsed = urlsplit(settings.database_url)

    assert parsed.scheme == "postgresql"
    assert parsed.hostname == "my-postgres.postgres.database.azure.com"
    assert parsed.port == 5432
    assert parsed.path == "/aks_upgrade_agent"
    assert parsed.query == "sslmode=require"
    assert parsed.username == "agent%40user"
    assert parsed.password == "p%40ss%3A%2Fword%23%3F"


def test_database_url_remains_supported_as_backward_compatible_fallback():
    database_url = "postgresql://legacy:secret@db.example.com:5432/agent?sslmode=require"
    settings = Settings(
        _env_file=None,
        app_environment="production",
        auth_mode="entra_id",
        entra_tenant_id="tenant-id",
        entra_audience="api://api-client-id",
        database_url=database_url,
    )

    assert settings.database_url == database_url


def test_partial_postgres_configuration_fails_fast():
    with pytest.raises(ValidationError, match="PostgreSQL configuration is incomplete"):
        Settings(
            _env_file=None,
            app_environment="production",
            auth_mode="entra_id",
            entra_tenant_id="tenant-id",
            entra_audience="api://api-client-id",
            postgres_host="my-postgres.postgres.database.azure.com",
            postgres_db="aks_upgrade_agent",
            postgres_user="agent",
        )


def test_production_requires_database_configuration():
    with pytest.raises(ValidationError, match="Production requires POSTGRES_HOST"):
        Settings(
            _env_file=None,
            app_environment="production",
            auth_mode="entra_id",
            entra_tenant_id="tenant-id",
            entra_audience="api://api-client-id",
        )


def test_local_development_keeps_local_postgres_default():
    settings = Settings(_env_file=None)

    assert settings.database_url == "postgresql://postgres:postgres@localhost:5432/aks_upgrade_agent"
