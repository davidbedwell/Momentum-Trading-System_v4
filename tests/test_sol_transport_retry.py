from __future__ import annotations

import io
import json
import urllib.error

import pytest

from MTS_V4.openai_compatible_provider import ResearchDirectorTransportError
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_provider import SolResearchPackageAwareResearchDirector


class _FakeResponse:
    def __init__(self, document: dict[str, object]) -> None:
        self._payload = json.dumps(document).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._payload


def _http_error(code: int, body: bytes = b'{"error":{"type":"server_error"}}') -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="https://api.openai.com/v1/chat/completions",
        code=code,
        msg="error",
        hdrs=None,
        fp=io.BytesIO(body),
    )


def _director(tmp_path) -> SolResearchPackageAwareResearchDirector:
    return SolResearchPackageAwareResearchDirector(
        research_package_store=JsonResearchPackageStore(tmp_path / "rps"),
        base_url="https://api.openai.com",
        model="gpt-5.6-sol",
        api_key="test-key",
        timeout_seconds=1,
    )


def test_sol_transport_retries_transient_500_then_succeeds(monkeypatch, tmp_path, capsys):
    calls = 0

    def fake_urlopen(request, timeout):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise _http_error(500)
        return _FakeResponse({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr("MTS_V4.sol_provider.urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("MTS_V4.sol_provider.time.sleep", lambda _seconds: None)

    result = _director(tmp_path)._chat_completion([{"role": "user", "content": "test"}])

    assert result == "ok"
    assert calls == 2
    assert "Sol transport transient HTTP 500; retry 1/6 in 2s" in capsys.readouterr().err


def test_sol_transport_exhausts_bounded_retries_for_repeated_500(monkeypatch, tmp_path, capsys):
    calls = 0

    def fake_urlopen(request, timeout):
        nonlocal calls
        calls += 1
        raise _http_error(500)

    monkeypatch.setattr("MTS_V4.sol_provider.urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("MTS_V4.sol_provider.time.sleep", lambda _seconds: None)

    with pytest.raises(ResearchDirectorTransportError, match="HTTPError"):
        _director(tmp_path)._chat_completion([{"role": "user", "content": "test"}])

    assert calls == 7
    stderr = capsys.readouterr().err
    assert "retry 1/6 in 2s" in stderr
    assert "retry 6/6 in 60s" in stderr


def test_sol_transport_does_not_retry_nontransient_400(monkeypatch, tmp_path, capsys):
    calls = 0

    def fake_urlopen(request, timeout):
        nonlocal calls
        calls += 1
        raise _http_error(400, b'{"error":{"type":"invalid_request_error"}}')

    monkeypatch.setattr("MTS_V4.sol_provider.urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("MTS_V4.sol_provider.time.sleep", lambda _seconds: None)

    with pytest.raises(ResearchDirectorTransportError, match="HTTPError"):
        _director(tmp_path)._chat_completion([{"role": "user", "content": "test"}])

    assert calls == 1
    assert capsys.readouterr().err == ""
