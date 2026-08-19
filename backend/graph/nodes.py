from __future__ import annotations

from typing import Any
from langgraph.types import interrupt
from agents.discovery import DiscoveryAgent
from agents.validation import ValidationAgent
from agents.upgrade import UpgradeAgent
from agents.reporting import ReportingAgent
from agents.notification import NotificationAgent
from graph.state import AKSUpgradeState
from tools.logger import logger

_discovery, _validation, _upgrade = DiscoveryAgent(), ValidationAgent(), UpgradeAgent()
_reporting, _notification = ReportingAgent(), NotificationAgent()


def _safe(name: str, fn, state: AKSUpgradeState) -> dict[str, Any]:
    try:
        logger.info('Executing node %s', name)
        return fn(dict(state))
    except Exception as exc:
        logger.exception('Node %s failed', name)
        return {'error': str(exc), 'workflow': {**state.get('workflow', {}), 'status': 'FAILED', 'current_step': name}}


def discovery_node(state): return _safe('discovery', _discovery.run, state)
def validation_node(state): return _safe('validation', _validation.run, state)
def upgrade_node(state): return _safe('upgrade', _upgrade.run, state)


def pre_report_node(state):
    report = _reporting.pre(dict(state))
    return {'reports': {**state.get('reports', {}), 'pre_upgrade_report': report}}


def post_report_node(state):
    report = _reporting.post(dict(state))
    return {'reports': {**state.get('reports', {}), 'post_upgrade_report': report}}


def validation_notification_node(state): return {'notifications': {**state.get('notifications', {}), 'validation': _notification.send('validation', dict(state))}}
def approval_notification_node(state): return {'notifications': {**state.get('notifications', {}), 'approval': _notification.send('approval', dict(state))}}
def started_notification_node(state): return {'notifications': {**state.get('notifications', {}), 'started': _notification.send('started', dict(state))}}
def final_notification_node(state): return {'notifications': {**state.get('notifications', {}), 'final': _notification.send('final', dict(state))}}


def approval_node(state):
    response = interrupt({'type': 'aks_upgrade_approval', 'cluster_name': state.get('cluster', {}).get('cluster_name'), 'target_version': state.get('upgrade', {}).get('target_version'), 'warnings': state.get('validation', {}).get('warnings', [])})
    approved = bool(response.get('approved', False))
    return {'approval': {'approved': approved, 'approved_by': response.get('approved_by'), 'comment': response.get('comment'), 'status': 'APPROVED' if approved else 'REJECTED'}}


def stop_node(state):
    status = 'REJECTED' if state.get('approval', {}).get('status') == 'REJECTED' else 'FAILED' if state.get('error') else 'STOPPED'
    return {'workflow': {**state.get('workflow', {}), 'status': status, 'current_step': 'stop'}}


def complete_node(state): return {'workflow': {**state.get('workflow', {}), 'status': state.get('upgrade', {}).get('status', 'COMPLETED'), 'current_step': 'complete'}}
