from __future__ import annotations

import json
from typing import Any

from config import get_settings


class AIAdvisor:
    def assess(self, state: dict[str, Any]) -> dict[str, Any]:
        settings = get_settings()
        if not settings.ai_enabled:
            return {"enabled": False, "status": "DISABLED", "summary": "Configure Azure OpenAI to enable AI-assisted analysis.", "risks": [], "recommendations": [], "questions": []}
        from openai import AzureOpenAI
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        kwargs: dict[str, Any] = {"azure_endpoint": settings.azure_openai_endpoint, "api_version": settings.azure_openai_api_version, "timeout": 45.0, "max_retries": 2}
        if settings.azure_openai_api_key:
            kwargs["api_key"] = settings.azure_openai_api_key
        else:
            kwargs["azure_ad_token_provider"] = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
        client = AzureOpenAI(**kwargs)
        cluster, upgrade = state.get("cluster", {}), state.get("upgrade", {})
        facts = {"request": state.get("request_text") or "Review this AKS upgrade request.", "cluster": cluster.get("cluster_name"), "resource_group": cluster.get("resource_group"), "current_version": (cluster.get("details") or {}).get("kubernetesVersion"), "target_version": upgrade.get("target_version"), "available_upgrades": cluster.get("available_upgrades"), "nodepools": cluster.get("nodepools"), "dry_run": upgrade.get("dry_run", True)}
        response = client.chat.completions.create(model=settings.azure_openai_deployment, temperature=0.1, max_tokens=900, messages=[{"role": "system", "content": "You are an AKS reliability advisor. Analyze only supplied facts. Return JSON with summary (string), risks (array), recommendations (array), questions (array). Identify missing facts; do not guess. This is advisory only: do not approve or perform upgrades, invent Azure facts, or provide commands. Deterministic validation and human approval remain authoritative."}, {"role": "user", "content": json.dumps(facts, default=str)}])
        content = response.choices[0].message.content or "{}"
        try:
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError("Expected JSON object")
        except (json.JSONDecodeError, ValueError):
            result = {"summary": content[:4000], "risks": [], "recommendations": [], "questions": []}
        return {"enabled": True, "status": "COMPLETED", "provider": "Azure OpenAI", "deployment": settings.azure_openai_deployment, "summary": str(result.get("summary", ""))[:4000], "risks": [str(x)[:1000] for x in result.get("risks", [])[:12]], "recommendations": [str(x)[:1000] for x in result.get("recommendations", [])[:12]], "questions": [str(x)[:1000] for x in result.get("questions", [])[:12]], "advisory_only": True}
