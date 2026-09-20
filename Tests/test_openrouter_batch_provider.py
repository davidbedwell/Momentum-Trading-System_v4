from __future__ import annotations

import io
import json

import pytest

from MTS_V4.openrouter_batch_provider import (
    OpenRouterBudgetExceeded,
    SubjectContextOpenRouterBatchResearchDirector,
)


class _Response:
    status = 200
    headers = {}

    def __init__(self, document):
        self._payload = json.dumps(document).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._payload


def _provider():
    provider = object.__new__(SubjectContextOpenRouterBatchResearchDirector)
    provider._model = "google/gemini-3.7-flash"
    provider._base_url = "https://openrouter.ai/api"
    provider._api_key = "test"
    provider._timeout_seconds = 1
    provider._openrouter_max_calls = 2
    provider._openrouter_max_spend = 1.0
    provider._openrouter_calls = 0
    provider._openrouter_spend = 0.0
    return provider


def test_openrouter_transport_records_actual_provider_cost(monkeypatch, tmp_path):
    provider = _provider()
    monkeypatch.setenv("MTS_OPENROUTER_RD_TELEMETRY_PATH", str(tmp_path / "telemetry.jsonl"))
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *args, **kwargs: _Response({
            "id": "r1",
            "model": "google/gemini-3.7-flash",
            "provider": "test-provider",
            "choices": [{"message": {"content": '{"continue_research":false}'}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "cost": 0.125},
        }),
    )
    result = provider._chat_completion([
        {"role": "user", "content": '{"operation":"BEGIN_BATCH_RESEARCH"}'}
    ])
    assert result == '{"continue_research":false}'
    assert provider.openrouter_usage()["actual_spend_usd"] == pytest.approx(0.125)
    telemetry = json.loads((tmp_path / "telemetry.jsonl").read_text().strip())
    assert telemetry["actual_call_cost_usd"] == pytest.approx(0.125)


def test_openrouter_transport_enforces_call_budget_before_request(monkeypatch):
    provider = _provider()
    provider._openrouter_calls = 2
    called = False

    def _urlopen(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("network must not be called")

    monkeypatch.setattr("urllib.request.urlopen", _urlopen)
    with pytest.raises(OpenRouterBudgetExceeded, match="call budget"):
        provider._chat_completion([
            {"role": "user", "content": '{"operation":"BEGIN_BATCH_RESEARCH"}'}
        ])
    assert called is False


def test_openrouter_transport_fails_closed_without_actual_cost(monkeypatch):
    provider = _provider()
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *args, **kwargs: _Response({
            "choices": [{"message": {"content": "{}"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }),
    )
    with pytest.raises(Exception, match="actual usage.cost"):
        provider._chat_completion([
            {"role": "user", "content": '{"operation":"BEGIN_BATCH_RESEARCH"}'}
        ])
