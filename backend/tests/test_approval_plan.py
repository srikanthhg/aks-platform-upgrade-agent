from graph.approval import approval_plan_hash


def test_plan_hash_is_stable_for_same_plan():
    state = {'cluster': {'resource_group': 'rg', 'cluster_name': 'aks', 'subscription_id': 'sub', 'details': {'kubernetesVersion': '1.31.1'}, 'nodepools': [{'name': 'system'}]}, 'upgrade': {'target_version': '1.32.1', 'dry_run': False, 'max_surge': '33%'}, 'validation': {'status': 'PASS', 'warnings': []}}
    assert approval_plan_hash(state) == approval_plan_hash(state)


def test_plan_hash_changes_when_target_or_pool_changes():
    state = {'cluster': {'resource_group': 'rg', 'cluster_name': 'aks', 'subscription_id': 'sub', 'details': {'kubernetesVersion': '1.31.1'}, 'nodepools': [{'name': 'system'}]}, 'upgrade': {'target_version': '1.32.1', 'dry_run': False, 'max_surge': '33%'}, 'validation': {'status': 'PASS', 'warnings': []}}
    original = approval_plan_hash(state)
    state['upgrade']['target_version'] = '1.33.0'
    assert approval_plan_hash(state) != original
