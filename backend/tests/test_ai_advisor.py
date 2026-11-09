from types import SimpleNamespace

from agents.ai_advisor import AIAdvisor


def test_advisor_reports_disabled_when_endpoint_not_configured(monkeypatch):
    monkeypatch.setattr(
        "agents.ai_advisor.get_settings",
        lambda: SimpleNamespace(ai_enabled=False),
    )

    result = AIAdvisor().assess({"cluster": {"cluster_name": "test-aks"}})

    assert result["enabled"] is False
    assert result["status"] == "DISABLED"
    assert "Configure Azure OpenAI" in result["summary"]


def test_advisor_uses_azure_openai_and_returns_structured_analysis(monkeypatch):
    from agents import ai_advisor

    monkeypatch.setattr(
        ai_advisor,
        "get_settings",
        lambda: SimpleNamespace(
            ai_enabled=True,
            azure_openai_endpoint="https://example.openai.azure.com/",
            azure_openai_api_version="2024-10-21",
            azure_openai_api_key="test-key",
            azure_openai_deployment="test-deployment",
        ),
    )

    class FakeMessage:
        content = '{"summary":"Review required","risks":["Version jump"],"recommendations":["Use dry run"],"questions":[]}'

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        @staticmethod
        def create(**kwargs):
            assert kwargs["model"] == "test-deployment"
            assert "current_version" in kwargs["messages"][1]["content"]
            return FakeResponse()

    class FakeClient:
        def __init__(self, **kwargs):
            assert kwargs["api_key"] == "test-key"
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("openai.AzureOpenAI", FakeClient)
    result = AIAdvisor().assess({"cluster": {"cluster_name": "test-aks", "details": {"kubernetesVersion": "1.31.4"}}, "upgrade": {"target_version": "1.32.2", "dry_run": True}})

    assert result["enabled"] is True
    assert result["status"] == "COMPLETED"
    assert result["risks"] == ["Version jump"]
    assert result["advisory_only"] is True



def test_advisor_read_only_tools_expose_only_discovered_state():
    from agents.ai_advisor import _tool_result

    state = {
        'cluster': {
            'details': {'kubernetesVersion': '1.31.4'},
            'available_upgrades': {'controlPlaneProfile': {'upgrades': [{'kubernetesVersion': '1.32.2'}]}},
            'nodepools': [{'name': 'systempool'}],
        },
        'upgrade': {'target_version': '1.32.2'},
        'validation': {'status': 'PASS', 'warnings': []},
    }
    assert _tool_result('get_upgrade_facts', state)['current_version'] == '1.31.4'
    assert _tool_result('get_nodepool_facts', state)['nodepools'][0]['name'] == 'systempool'
    assert _tool_result('get_validation_facts', state)['status'] == 'PASS'


def test_advisor_rejects_unknown_tool():
    import pytest
    from agents.ai_advisor import _tool_result

    with pytest.raises(ValueError, match='not allowlisted'):
        _tool_result('run_shell', {})
