from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Literal
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
    database_url: str = 'postgresql://postgres:postgres@localhost:5432/aks_upgrade_agent'
    log_level: str='INFO'
    applicationinsights_connection_string: str | None = None
    azure_subscription_id: str | None=None
    azure_managed_identity_client_id: str | None=None
    azure_auth_mode: Literal['existing','managed_identity']='existing'
    allow_real_upgrades: bool=False
    default_dry_run: bool=True
    teams_webhook_url: str | None=None
    teams_notifications_enabled: bool=False
    reports_directory: Path=Path('/tmp/aks-agent/reports')
    kubeconfig_directory: Path=Path('/tmp/aks-agent/kubeconfigs')
    cluster_lock_ttl_minutes: int=Field(default=360,ge=30,le=1440)
    command_timeout_seconds: int=Field(default=300,ge=10,le=3600)
    upgrade_timeout_seconds: int=Field(default=7200,ge=300,le=21600)
    @model_validator(mode='after')
    def validate_prod(self):
        if self.app_environment=='production':
            if self.auth_mode!='entra_id': raise ValueError('Production requires AUTH_MODE=entra_id')
            if not self.entra_tenant_id or not self.entra_audience: raise ValueError('ENTRA_TENANT_ID and ENTRA_AUDIENCE are required')
            if not self.database_url.startswith(('postgresql://','postgresql+psycopg://')): raise ValueError('Production requires PostgreSQL DATABASE_URL')
        return self
    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.cors_allowed_origins.split(',') if x.strip()]
    def ensure_directories(self):
        self.reports_directory.mkdir(parents=True,exist_ok=True)
        self.kubeconfig_directory.mkdir(parents=True,exist_ok=True)
@lru_cache
def get_settings():
    s=Settings(); s.ensure_directories(); return s
