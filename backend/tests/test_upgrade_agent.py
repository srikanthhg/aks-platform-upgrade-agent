from unittest.mock import patch

import pytest

from agents.upgrade import UpgradeAgent
from graph.approval import approval_plan_hash


class FakeCLI:
    def __init__(self, *args, **kwargs):
        pass

    def upgrade_control_plane(self, *args, **kwargs):
        return {'status': 'DRY_RUN' if kwargs['dry_run'] else 'SUCCEEDED'}

    def upgrade_nodepool(self, *args, **kwargs):
        return {'status': 'DRY_RUN' if kwargs['dry_run'] else 'SUCCEEDED'}


def valid_state(*, dry_run=True, validation='PASS'):
    return {
        'cluster': {
            'resource_group': 'rg',
            'cluster_name': 'aks',
            'subscription_id': 'sub',
            'details': {'kubernetesVersion': '1.31.1'},
            'available_upgrades': {},
            'nodepools': [{'name': 'systempool'}],
        },
        'validation': {'status': validation, 'warnings': []},
        'approval': {'approved': False},
        'upgrade': {'target_version': '1.32.1', 'dry_run': dry_run, 'max_surge': '33%'},
    }


@patch('agents.upgrade.validate_target_version')
@patch('agents.upgrade.AzureCLI', FakeCLI)
def test_dry_run_never_executes_real_upgrade(validate):
    result = UpgradeAgent().run(valid_state())
    assert result['upgrade']['status'] == 'DRY_RUN_COMPLETED'
    assert result['upgrade']['dry_run'] is True


def test_warning_requires_approval_even_for_dry_run():
    with pytest.raises(PermissionError, match='approval'):
        UpgradeAgent().run(valid_state(validation='WARNING'))


def test_real_upgrade_requires_approval_even_when_validation_passes(monkeypatch):
    from agents import upgrade
    monkeypatch.setattr(upgrade, 'get_settings', lambda: type('Settings', (), {'allow_real_upgrades': True, 'default_dry_run': True})())
    with pytest.raises(PermissionError, match='every real AKS upgrade'):
        UpgradeAgent().run(valid_state(dry_run=False))


def test_real_upgrade_requires_approval_plan_hash(monkeypatch):
    from agents import upgrade
    monkeypatch.setattr(upgrade, 'get_settings', lambda: type('Settings', (), {'allow_real_upgrades': True, 'default_dry_run': True})())
    state = valid_state(dry_run=False)
    state['approval'] = {'approved': True, 'approved_by': 'operator@example.com', 'plan_hash': 'wrong'}
    with pytest.raises(PermissionError, match='plan has changed'):
        UpgradeAgent().run(state)


@patch('agents.upgrade.validate_target_version')
@patch('agents.upgrade.AzureCLI', FakeCLI)
def test_real_upgrade_with_matching_approval_can_execute(validate, monkeypatch):
    from agents import upgrade
    monkeypatch.setattr(upgrade, 'get_settings', lambda: type('Settings', (), {'allow_real_upgrades': True, 'default_dry_run': True})())
    state = valid_state(dry_run=False)
    state['approval'] = {'approved': True, 'approved_by': 'operator@example.com'}
    state['approval']['plan_hash'] = approval_plan_hash(state)
    result = UpgradeAgent().run(state)
    assert result['upgrade']['status'] == 'SUCCEEDED'
