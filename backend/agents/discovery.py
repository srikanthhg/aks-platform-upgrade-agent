from __future__ import annotations

from typing import Any
from config import get_settings
from tools.azure_cli import AzureCLI


class DiscoveryAgent:
    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        cluster = state['cluster']
        cli = AzureCLI(subscription_id=cluster.get('subscription_id'))
        settings = get_settings()
        if settings.azure_auth_mode == 'managed_identity':
            cli.login_with_managed_identity(settings.azure_managed_identity_client_id)
        rg, name = cluster['resource_group'], cluster['cluster_name']
        details = cli.discover_cluster(rg, name)
        nodepools = cli.get_nodepools(rg, name)
        upgrades = cli.get_available_upgrades(rg, name)
        return {'cluster': {**cluster, 'details': details, 'nodepools': nodepools, 'available_upgrades': upgrades}}
