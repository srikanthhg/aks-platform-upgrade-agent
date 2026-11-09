from graph.state import AKSUpgradeState


def after_discovery(state: AKSUpgradeState) -> str:
    return 'stop' if state.get('error') else 'validation'


def after_validation_notification(state: AKSUpgradeState) -> str:
    if state.get('error'):
        return 'stop'
    validation = state.get('validation', {})
    status = validation.get('status')
    if status not in {'PASS', 'WARNING'}:
        return 'stop'
    # Dry runs with clean validation can proceed directly. Warnings always
    # require review; every real upgrade requires explicit operator approval.
    if status == 'WARNING' or not state.get('upgrade', {}).get('dry_run', True):
        return 'approval_notice'
    return 'started'


def after_approval(state: AKSUpgradeState) -> str:
    return 'started' if state.get('approval', {}).get('approved') else 'stop'


def after_upgrade(state: AKSUpgradeState) -> str:
    return 'post_report'


def after_final(state: AKSUpgradeState) -> str:
    return 'complete' if state.get('upgrade', {}).get('status') in {'SUCCEEDED', 'DRY_RUN_COMPLETED'} else 'stop'
