from __future__ import annotations

from typing import Any

from config import get_settings
from tools.azure_cli import AzureCLI
from upgrade.versioning import validate_target_version


class UpgradeAgent:
    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        settings = get_settings()
        cluster, upgrade = state['cluster'], state['upgrade']
        dry_run = bool(upgrade.get('dry_run', settings.default_dry_run))
        if not dry_run and not settings.allow_real_upgrades:
            raise PermissionError('Real upgrades are disabled. Set ALLOW_REAL_UPGRADES=true and submit dry_run=false explicitly.')
        if state.get('validation', {}).get('status') not in {'PASS', 'WARNING'}:
            raise RuntimeError('Upgrade cannot start without a successful pre-upgrade validation.')
        if state.get('validation', {}).get('status') == 'WARNING' and not state.get('approval', {}).get('approved'):
            raise PermissionError('Human approval is required when validation has warnings.')

        current = cluster.get('details', {}).get('kubernetesVersion')
        target = upgrade['target_version']
        validate_target_version(current, target, cluster.get('available_upgrades', {}))

        cli = AzureCLI(subscription_id=cluster.get('subscription_id'))
        rg, name = cluster['resource_group'], cluster['cluster_name']
        steps: list[dict[str, Any]] = []
        control = cli.upgrade_control_plane(rg, name, target, dry_run=dry_run)
        steps.append({'name': 'Control plane', 'status': 'DRY_RUN' if dry_run else 'SUCCEEDED', 'details': control})

        pools = []
        for pool in cluster.get('nodepools', []):
            pool_name = pool.get('name')
            if not pool_name:
                continue
            details = cli.upgrade_nodepool(rg, name, pool_name, target, upgrade.get('max_surge', '33%'), dry_run=dry_run)
            item = {'name': pool_name, 'status': 'DRY_RUN' if dry_run else 'SUCCEEDED', 'details': details}
            pools.append(item)
            steps.append(item)

        status = 'DRY_RUN_COMPLETED' if dry_run else 'SUCCEEDED'
        return {'upgrade': {**upgrade, 'dry_run': dry_run, 'status': status, 'steps': steps, 'nodepool_results': pools}}
