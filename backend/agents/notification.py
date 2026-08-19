from __future__ import annotations
from typing import Any
from tools.teams import TeamsNotifier


class NotificationAgent:
    def __init__(self): self.notifier = TeamsNotifier()
    def send(self, kind: str, state: dict[str, Any]) -> dict[str, Any]:
        cluster = state.get('cluster', {})
        facts = {'Cluster': cluster.get('cluster_name'), 'Resource group': cluster.get('resource_group'), 'Validation': state.get('validation', {}).get('status'), 'Upgrade': state.get('upgrade', {}).get('status')}
        titles = {'validation': 'AKS validation result', 'approval': 'AKS approval required', 'started': 'AKS upgrade started', 'final': 'AKS upgrade result'}
        return self.notifier.send(titles[kind], f'Workflow event: {kind}', facts)
