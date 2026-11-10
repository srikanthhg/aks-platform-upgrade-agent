from __future__ import annotations

import json
from typing import Any

from config import get_settings


# These are deliberately read-only, bounded tools. The model can inspect only
# facts already collected by deterministic discovery; it cannot run commands.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_upgrade_facts",
            "description": "Return the discovered AKS Kubernetes versions and available upgrade targets.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_nodepool_facts",
            "description": "Return the discovered node pool names and their collected properties.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_validation_facts",
            "description": "Return deterministic pre-upgrade validation status, checks, and warnings.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
]


def _tool_result(name: str, state: dict[str, Any]) -> dict[str, Any]:
    cluster = state.get("cluster") or {}
    if name == "get_upgrade_facts":
        return {"current_version": (cluster.get("details") or {}).get("kubernetesVersion"), "available_upgrades": cluster.get("available_upgrades") or {}, "requested_target": (state.get("upgrade") or {}).get("target_version")}
    if name == "get_nodepool_facts":
        return {"nodepools": cluster.get("nodepools") or []}
    if name == "get_validation_facts":
        validation = state.get("validation") or {}
        return {"status": validation.get("status"), "checks": validation.get("checks") or [], "warnings": validation.get("warnings") or []}
    raise ValueError(f"Tool is not allowlisted: {name}")


class AIAdvisor:
    def assess(self, state: dict[str, Any]) -> dict[str, Any]:
        settings = get_settings()
        if not settings.ai_enabled:
            return {"enabled": False, "status": "DISABLED", "summary": "Configure Azure OpenAI to enable AI-assisted analysis.", "risks": [], "recommendations": [], "questions": [], "advisory_only": True}

        from openai import AzureOpenAI
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider

        kwargs: dict[str, Any] = {
            "azure_endpoint": settings.azure_openai_endpoint,
            "api_version": settings.azure_openai_api_version,
            "timeout": 45.0,
            "max_retries": 2,
        }
        if settings.azure_openai_api_key:
            kwargs["api_key"] = settings.azure_openai_api_key
        else:
            kwargs["azure_ad_token_provider"] = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
        client = AzureOpenAI(**kwargs)
        cluster = state.get("cluster") or {}
        upgrade = state.get("upgrade") or {}
        facts = {
            "request": state.get("request_text") or "Review this AKS upgrade request.",
            "cluster_name": cluster.get("cluster_name"),
            "resource_group": cluster.get("resource_group"),
            "subscription_id": cluster.get("subscription_id"),
            "current_version": (cluster.get("details") or {}).get("kubernetesVersion"),
            "target_version": upgrade.get("target_version"),
            "available_upgrades": cluster.get("available_upgrades") or {},
            "nodepools": cluster.get("nodepools") or [],
            "validation": state.get("validation") or {},
            "dry_run": upgrade.get("dry_run", True),
        }
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are an AKS reliability advisor using a GPT-4.1-class deployment. "
                    "Analyze only supplied facts. You may call the three read-only fact tools "
                    "to inspect already-discovered data. Never invent Azure facts, provide "
                    "executable commands, approve an upgrade, or initiate changes. Identify "
                    "unknowns. Return a JSON object with summary (string), risks (array), "
                    "recommendations (array), questions (array), and proposed_checks (array). "
                    "All advice is advisory; deterministic validation and an authenticated "
                    "human approval gate are authoritative."
                ),
            },
            {"role": "user", "content": json.dumps(facts, default=str)},
        ]

        # Bound the model/tool loop. Tool functions read only the workflow state.
        tool_calls_used = 0
        for _ in range(4):
            response = client.chat.completions.create(
                model=settings.azure_openai_deployment,
                temperature=0.1,
                max_tokens=1400,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            message = response.choices[0].message
            if not getattr(message, 'tool_calls', None):
                content = message.content or "{}"
                break
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {"name": call.function.name, "arguments": call.function.arguments},
                    }
                    for call in message.tool_calls
                ],
            })
            for call in message.tool_calls:
                tool_calls_used += 1
                if tool_calls_used > 8:
                    raise RuntimeError("Azure OpenAI exceeded the read-only tool-call limit.")
                name = call.function.name
                # Reject unknown names and malformed arguments rather than dispatching
                # arbitrary functions or accepting model-generated command strings.
                if name not in {"get_upgrade_facts", "get_nodepool_facts", "get_validation_facts"}:
                    raise ValueError(f"Azure OpenAI requested a non-allowlisted tool: {name}")
                arguments = json.loads(call.function.arguments or "{}")
                if arguments:
                    raise ValueError("Read-only advisor tools do not accept arguments.")
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(_tool_result(name, state), default=str),
                })
        else:
            raise RuntimeError("Azure OpenAI did not complete within the bounded tool-call loop.")

        try:
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError("Expected JSON object")
        except (json.JSONDecodeError, ValueError):
            result = {"summary": content[:4000], "risks": [], "recommendations": [], "questions": [], "proposed_checks": []}

        def items(key: str) -> list[str]:
            value = result.get(key, [])
            if not isinstance(value, list):
                return []
            return [str(item)[:1000] for item in value[:12]]

        return {
            "enabled": True,
            "status": "COMPLETED",
            "provider": "Azure OpenAI",
            "deployment": settings.azure_openai_deployment,
            "model_class": "GPT-4.1-class (configured deployment)",
            "tool_calls": tool_calls_used,
            "summary": str(result.get("summary", ""))[:4000],
            "risks": items("risks"),
            "recommendations": items("recommendations"),
            "questions": items("questions"),
            "proposed_checks": items("proposed_checks"),
            "advisory_only": True,
        }
