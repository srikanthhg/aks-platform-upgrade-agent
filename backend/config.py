from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    app_environment: Literal['development','test','staging','production']='development'
    auth_mode: Literal['api_key','entra_id']='api_key'
    app_api_key: str | None = None
    entra_tenant_id: str | None = None
    entra_audience: str | None = None
    entra_required_role: str = 'AKS.Upgrade.Operator'
    cors_allowed_origins: str = 'http://localhost:5173'
    # Prefer separate PostgreSQL settings in ACA. DATABASE_URL remains as a migration fallback.
    database_url: str | None = None
    postgres_host: str | None = None
    postgres_port: int = 5432
    postgres_db: str | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_sslmode: str = 'require'
    log_level: str='INFO'
    applicationinsights_connection_string: str | None = None
    azure_subscription_id: str | None=None
    azure_managed_identity_client_id: str | None=None
    azure_auth_mode: Literal['existing','managed_identity']='existing'
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = '2024-10-21'
    azure_openai_api_key: str | None = None
    ai_advisor_enabled: bool = True
    allow_real_upgrades: bool=False
    default_dry_run: bool=True
    teams_webhook_url: str | None=None
    teams_notifications_enabled: bool=False
    reports_directory: Path=Path('/tmp/aks-agent/reports')
    kubeconfig_directory: Path=Path('/tmp/aks-agent/kubeconfigs')
    approval_ttl_minutes: int=Field(default=30,ge=1,le=240)
    cluster_lock_ttl_minutes: int=Field(default=360,ge=30,le=1440)
    command_timeout_seconds: int=Field(default=300,ge=10,le=3600)
    upgrade_timeout_seconds: int=Field(default=7200,ge=300,le=21600)
    @model_validator(mode='after')
    def configure_database(self):
        postgres_parts = {
            'POSTGRES_HOST': self.postgres_host,
            'POSTGRES_DB': self.postgres_db,
            'POSTGRES_USER': self.postgres_user,
            'POSTGRES_PASSWORD': self.postgres_password,
        }
        supplied = [name for name, value in postgres_parts.items() if value is not None and value != '']
        if supplied and len(supplied) != len(postgres_parts):
            missing = [name for name, value in postgres_parts.items() if value is None or value == '']
            raise ValueError(f"PostgreSQL configuration is incomplete; missing: {', '.join(missing)}")

        if len(supplied) == len(postgres_parts):
            if not self.postgres_host or '://' in self.postgres_host or '/' in self.postgres_host:
                raise ValueError('POSTGRES_HOST must be a hostname only')
            if not 1 <= self.postgres_port <= 65535:
                raise ValueError('POSTGRES_PORT must be between 1 and 65535')
            # Percent-encode credentials/database components so special characters
            # such as @, :, /, # and ? cannot corrupt the connection URI.
            user = quote(self.postgres_user or '', safe='')
            password = quote(self.postgres_password or '', safe='')
            database = quote(self.postgres_db or '', safe='')
            sslmode = quote(self.postgres_sslmode, safe='')
            self.database_url = (
                f"postgresql://{user}:{password}@{self.postgres_host}:"
                f"{self.postgres_port}/{database}?sslmode={sslmode}"
            )
        elif not self.database_url:
            if self.app_environment == 'production':
                raise ValueError(
                    'Production requires POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, '
                    'POSTGRES_PASSWORD (and optional POSTGRES_PORT/POSTGRES_SSLMODE), '
                    'or DATABASE_URL'
                )
            self.database_url = 'postgresql://postgres:postgres@localhost:5432/aks_upgrade_agent'

        if self.app_environment == 'production':
            if self.auth_mode != 'entra_id':
                raise ValueError('Production requires AUTH_MODE=entra_id')
            if not self.entra_tenant_id or not self.entra_audience:
                raise ValueError('ENTRA_TENANT_ID and ENTRA_AUDIENCE are required')
            if not self.database_url.startswith(('postgresql://', 'postgresql+psycopg://')):
                raise ValueError('Production requires PostgreSQL connection settings')
        return self
    @property
    def ai_enabled(self) -> bool:
        return self.ai_advisor_enabled and bool(self.azure_openai_endpoint and self.azure_openai_deployment)
    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.cors_allowed_origins.split(',') if x.strip()]
    def ensure_directories(self):
        self.reports_directory.mkdir(parents=True,exist_ok=True)
        self.kubeconfig_directory.mkdir(parents=True,exist_ok=True)
@lru_cache
def get_settings():
    s=Settings(); s.ensure_directories(); return s
