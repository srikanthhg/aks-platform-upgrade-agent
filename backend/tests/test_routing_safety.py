from graph.routing import after_validation_notification


def test_clean_dry_run_does_not_pause_for_approval():
    assert after_validation_notification({'validation': {'status': 'PASS'}, 'upgrade': {'dry_run': True}}) == 'started'


def test_warning_requires_approval_even_for_dry_run():
    assert after_validation_notification({'validation': {'status': 'WARNING'}, 'upgrade': {'dry_run': True}}) == 'approval_notice'


def test_every_real_upgrade_requires_approval_even_with_pass():
    assert after_validation_notification({'validation': {'status': 'PASS'}, 'upgrade': {'dry_run': False}}) == 'approval_notice'


def test_failed_validation_stops():
    assert after_validation_notification({'validation': {'status': 'FAIL'}, 'upgrade': {'dry_run': False}}) == 'stop'
