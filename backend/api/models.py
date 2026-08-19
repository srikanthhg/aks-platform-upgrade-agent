from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator


SAFE_AZURE_NAME = re.compile(r'^[A-Za-z0-9_.()-]{1,90}$')
VERSION = re.compile(r'^\d+\.\d+(?:\.\d+)?$')
MAX_SURGE = re.compile(r'^(?:[1-9]\d*|100)%?$')


class StartWorkflowRequest(BaseModel):
    resource_group: str = Field(min_length=1, max_length=90)
    cluster_name: str = Field(min_length=1, max_length=63)
    target_version: str = Field(min_length=3, max_length=20)
    subscription_id: str | None = Field(default=None, max_length=64)
    dry_run: bool = True
    max_surge: str = Field(default='33%', max_length=8)

    @field_validator('resource_group', 'cluster_name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not SAFE_AZURE_NAME.fullmatch(value):
            raise ValueError('Only letters, numbers, underscores, periods, parentheses and hyphens are allowed.')
        return value

    @field_validator('target_version')
    @classmethod
    def validate_version(cls, value: str) -> str:
        if not VERSION.fullmatch(value):
            raise ValueError('Expected Kubernetes version such as 1.32.7.')
        return value

    @field_validator('max_surge')
    @classmethod
    def validate_max_surge(cls, value: str) -> str:
        if not MAX_SURGE.fullmatch(value):
            raise ValueError('max_surge must be a positive integer or percentage.')
        return value


class DecisionRequest(BaseModel):
    comment: str | None = Field(default=None, max_length=1000)


class WorkflowResponse(BaseModel):
    thread_id: str
    status: str
    paused: bool = False
    next_nodes: list[str] = Field(default_factory=list)
    interrupt: list[Any] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)
