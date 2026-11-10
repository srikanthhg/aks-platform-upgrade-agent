from __future__ import annotations

import hashlib
import json
from typing import Any


def approval_plan_payload(state: dict[str, Any]) -> dict[str, Any]:
    """Return the exact, stable subset of workflow state an operator approves."""
    cluster = state.get("cluster", {})
    upgrade = state.get("upgrade", {})
    details = cluster.get("details") or {}
    pools = cluster.get("nodepools") or []
    return {
        "subscription_id": cluster.get("subscription_id"),
        "resource_group": cluster.get("resource_group"),
        "cluster_name": cluster.get("cluster_name"),
        "current_version": details.get("kubernetesVersion"),
        "target_version": upgrade.get("target_version"),
        "dry_run": bool(upgrade.get("dry_run", True)),
        "max_surge": upgrade.get("max_surge", "33%"),
        "nodepools": sorted(
            str(pool.get("name")) for pool in pools
            if isinstance(pool, dict) and pool.get("name")
        ),
        "validation_status": (state.get("validation") or {}).get("status"),
        "validation_warnings": (state.get("validation") or {}).get("warnings", []),
    }


def approval_plan_hash(state: dict[str, Any]) -> str:
    canonical = json.dumps(
        approval_plan_payload(state), sort_keys=True, separators=(",", ":"), default=str
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
