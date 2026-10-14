from __future__ import annotations
from typing import Any, TypedDict

class AKSUpgradeState(TypedDict, total=False):
    cluster: dict[str, Any]
    validation: dict[str, Any]
    ai_advisor: dict[str, Any]
    approval: dict[str, Any]
    upgrade: dict[str, Any]
    reports: dict[str, Any]
    notifications: dict[str, Any]
    workflow: dict[str, Any]
    request_text: str
    error: str | None
