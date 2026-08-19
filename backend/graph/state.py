from __future__ import annotations
from typing import Any, TypedDict

class AKSUpgradeState(TypedDict, total=False):
    cluster: dict[str, Any]
    validation: dict[str, Any]
    approval: dict[str, Any]
    upgrade: dict[str, Any]
    reports: dict[str, Any]
    notifications: dict[str, Any]
    workflow: dict[str, Any]
    error: str | None
