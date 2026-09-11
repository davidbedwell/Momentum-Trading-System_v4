from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Mapping, Sequence

from .openai_compatible_provider import ResearchDirectorTransportError
from .research_package_provider import ResearchPackageAwareResearchDirector


class SolResearchPackageAwareResearchDirector(ResearchPackageAwareResearchDirector):
    """Research-package-aware Sol transport using supported Chat Completions parameters.

    The local/Qwen provider retains its existing transport unchanged. Sol currently
    rejects the non-default temperature used by that provider, so the appellate
    transport omits temperature and lets the model use its supported default.

    Optional transport telemetry is written when ``MTS_SOL_TELEMETRY_PATH`` is set.
    Telemetry contains operational metadata and provider-reported usage only; prompt
    and response content are intentionally excluded.
    """

    _TRANSIENT_HTTP_CODES = frozenset({408, 429, 500, 502, 503, 504})
    _MAX_TRANSIENT_RETRIES = 6
    _TRANSIENT_RETRY_DELAYS_SECONDS = (2.0, 4.0, 8.0, 16.0, 32.0, 60.0)

    @staticmethod
    def _operation(messages: Sequence[Mapping[str, str]]) -> str | None:
        for message in reversed(messages):
            if message.get("role") != "user":
                continue
            try:
                payload = json.loads(message.get("content", ""))
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(payload, Mapping):
                operation = payload.get("operation")
                if isinstance(operation, str) and operation.strip():
                    return operation
        return None

    @staticmethod
    def _retry_after_seconds(headers: object) -> float | None:
        try:
            raw = headers.get("Retry-After")  # type: ignore[attr-defined]
        except Exception:
            return None
        if raw is None:
            return None
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return None
        return value if value >= 0 else None

    @staticmethod
    def _header(headers: object, name: str) -> str | None:
        try:
            value = headers.get(name)  # type: ignore[attr-defined]
        except Exception:
            return None
        return str(value) if value is not None else None

    @classmethod
    def _telemetry_path(cls) -> Path | None:
        raw = os.getenv("MTS_SOL_TELEMETRY_PATH", "").strip()
        return Path(raw).expanduser() if raw else None

    @classmethod
    def _write_telemetry(cls, payload: Mapping[str, Any]) -> None:
        path = cls._telemetry_path()
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            **dict(payload),
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, default=str, separators=(",", ":")) + "\n")

    @classmethod
    def _retry_delay(cls, *, attempt: int, headers: object = None) -> float:
        base = cls._TRANSIENT_RETRY_DELAYS_SECONDS[attempt]
        retry_after = cls._retry_after_seconds(headers)
        if retry_after is not None:
            base = max(base, retry_after)
        jitter = random.uniform(0.0, min(1.0, base * 0.10))
        return base + jitter

    def _chat_completion(self, messages: Sequence[Mapping[str, str]]) -> str:
        body = json.dumps(
            {
                "model": self._model,
                "messages": list(messages),
            },
            separators=(",", ":"),
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        operation = self._operation(messages)
        call_started = time.monotonic()
        document = None
        response_headers = None
        transient_failures = 0

        for attempt in range(self._MAX_TRANSIENT_RETRIES + 1):
            request = urllib.request.Request(
                f"{self._base_url}/v1/chat/completions",
                data=body,
                headers=headers,
                method="POST",
            )
            attempt_started = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                    response_headers = response.headers
                    document = json.loads(response.read().decode("utf-8"))
                    status = getattr(response, "status", 200)
                self._write_telemetry(
                    {
                        "event": "HTTP_ATTEMPT",
                        "operation": operation,
                        "model": self._model,
                        "attempt": attempt + 1,
                        "http_status": status,
                        "elapsed_seconds": time.monotonic() - attempt_started,
                        "request_id": self._header(response_headers, "x-request-id"),
                        "retry_after": self._header(response_headers, "Retry-After"),
                    }
                )
                break
            except urllib.error.HTTPError as exc:
                try:
                    response_body = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    response_body = ""
                detail = f"; response_body={response_body}" if response_body else ""
                retryable = exc.code in self._TRANSIENT_HTTP_CODES
                self._write_telemetry(
                    {
                        "event": "HTTP_ATTEMPT",
                        "operation": operation,
                        "model": self._model,
                        "attempt": attempt + 1,
                        "http_status": exc.code,
                        "retryable": retryable,
                        "elapsed_seconds": time.monotonic() - attempt_started,
                        "request_id": self._header(exc.headers, "x-request-id"),
                        "retry_after": self._header(exc.headers, "Retry-After"),
                    }
                )
                if retryable and attempt < self._MAX_TRANSIENT_RETRIES:
                    transient_failures += 1
                    delay = self._retry_delay(attempt=attempt, headers=exc.headers)
                    print(
                        f"Sol transport transient HTTP {exc.code}; retry "
                        f"{attempt + 1}/{self._MAX_TRANSIENT_RETRIES} in {delay:.1f}s",
                        file=sys.stderr,
                        flush=True,
                    )
                    time.sleep(delay)
                    continue
                raise ResearchDirectorTransportError(
                    f"AI Research Director transport failed: HTTPError: {exc}{detail}"
                ) from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                self._write_telemetry(
                    {
                        "event": "HTTP_ATTEMPT",
                        "operation": operation,
                        "model": self._model,
                        "attempt": attempt + 1,
                        "transport_error": type(exc).__name__,
                        "retryable": attempt < self._MAX_TRANSIENT_RETRIES,
                        "elapsed_seconds": time.monotonic() - attempt_started,
                    }
                )
                if attempt < self._MAX_TRANSIENT_RETRIES:
                    transient_failures += 1
                    delay = self._retry_delay(attempt=attempt)
                    print(
                        f"Sol transport transient {type(exc).__name__}; retry "
                        f"{attempt + 1}/{self._MAX_TRANSIENT_RETRIES} in {delay:.1f}s",
                        file=sys.stderr,
                        flush=True,
                    )
                    time.sleep(delay)
                    continue
                raise ResearchDirectorTransportError(
                    f"AI Research Director transport failed: {type(exc).__name__}: {exc}"
                ) from exc
            except json.JSONDecodeError as exc:
                raise ResearchDirectorTransportError(
                    f"AI Research Director transport failed: {type(exc).__name__}: {exc}"
                ) from exc

        if document is None:
            raise ResearchDirectorTransportError(
                "AI Research Director transport failed without a response document"
            )

        try:
            message = document["choices"][0]["message"]
            content = message.get("content")
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise ResearchDirectorTransportError(
                "OpenAI-compatible response is missing choices[0].message"
            ) from exc
        if not isinstance(content, str) or not content.strip():
            reasoning_content = message.get("reasoning_content") if isinstance(message, Mapping) else None
            if isinstance(reasoning_content, str) and reasoning_content.strip():
                content = reasoning_content
            else:
                raise ResearchDirectorTransportError(
                    "AI Research Director returned no textual decision"
                )

        usage = document.get("usage") if isinstance(document, Mapping) else None
        self._write_telemetry(
            {
                "event": "SOL_CALL_COMPLETE",
                "operation": operation,
                "model": self._model,
                "elapsed_seconds": time.monotonic() - call_started,
                "http_attempts": transient_failures + 1,
                "transient_failures": transient_failures,
                "request_id": self._header(response_headers, "x-request-id"),
                "usage": dict(usage) if isinstance(usage, Mapping) else None,
                "response_id": document.get("id") if isinstance(document, Mapping) else None,
            }
        )
        return content
