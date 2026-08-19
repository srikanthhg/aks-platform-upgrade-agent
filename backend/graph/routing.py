from graph.state import AKSUpgradeState


def after_discovery(state: AKSUpgradeState) -> str: return 'stop' if state.get('error') else 'validation'
def after_validation_notification(state: AKSUpgradeState) -> str:
    if state.get('error'): return 'stop'
    status = state.get('validation', {}).get('status')
    return 'started' if status == 'PASS' else 'approval_notice' if status == 'WARNING' else 'stop'
def after_approval(state: AKSUpgradeState) -> str: return 'started' if state.get('approval', {}).get('approved') else 'stop'
def after_upgrade(state: AKSUpgradeState) -> str: return 'post_report'
def after_final(state: AKSUpgradeState) -> str: return 'complete' if state.get('upgrade', {}).get('status') in {'SUCCEEDED', 'DRY_RUN_COMPLETED'} else 'stop'
