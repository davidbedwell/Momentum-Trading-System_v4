from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Mapping, Sequence

from .openai_compatible_provider import ResearchDirectorTransportError
from .subject_scientific_context import SubjectContextSolBatchResearchDirector


class OpenRouterBudgetExceeded(RuntimeError):
    pass


class SubjectContextOpenRouterBatchResearchDirector(SubjectContextSolBatchResearchDirector):
    """Use the frozen successful batch-RD scientific contract through OpenRouter.

    Only model transport and cost accounting differ from the Direct-Sol provider.
    The inherited batch prompts, Research Package semantics, Analysis method
    visibility, phase contract, and scientific closure behavior remain unchanged.
    """

    def __init__(
        self,
        *args,
        max_model_calls: int,
        max_model_spend_usd: float,
        **kwargs,
    ) -> None:
        if max_model_calls < 1:
            raise ValueError("max_model_calls must be positive")
        if max_model_spend_usd <= 0:
            raise ValueError("max_model_spend_usd must be positive")
        self._openrouter_max_calls = int(max_model_calls)
        self._openrouter_max_spend = float(max_model_spend_usd)
        self._openrouter_calls = 0
        self._openrouter_spend = 0.0
        super().__init__(*args, **kwargs)

    # SolBatchResearchDirector invokes this in __init__. Candidate transport must
    # not use Sol token prices or Sol projection semantics.
    def configure_sol_spend_guard(self, *, authorized_spend_usd: float, authorization_callback=None) -> None:
        self._sol_spend_guard = None

    def openrouter_usage(self) -> Mapping[str, object]:
        return {
            "model": self._model,
            "completed_calls": self._openrouter_calls,
            "actual_spend_usd": self._openrouter_spend,
            "authorized_calls": self._openrouter_max_calls,
            "authorized_spend_usd": self._openrouter_max_spend,
        }

    @classmethod
    def _telemetry_path(cls) -> Path | None:
        raw = os.getenv("MTS_OPENROUTER_RD_TELEMETRY_PATH", "").strip()
        return Path(raw).expanduser() if raw else None

    def _chat_completion(self, messages: Sequence[Mapping[str, str]]) -> str:
        if self._openrouter_calls >= self._openrouter_max_calls:
            raise OpenRouterBudgetExceeded("OpenRouter RD call budget exhausted")
        if self._openrouter_spend >= self._openrouter_max_spend:
            raise OpenRouterBudgetExceeded("OpenRouter RD spend budget exhausted")

        body = json.dumps(
            {
                "model": self._model,
                "messages": list(messages),
                "response_format": {"type": "json_object"},
                "reasoning": {"effort": "high"},
                "usage": {"include": True},
            },
            separators=(",", ":"),
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/davidbedwell/Momentum-Trading-System_v4",
            "X-Title": "MTS V4 Gemini-Sol Virgin Equivalence",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        request = urllib.request.Request(
            f"{self._base_url}/v1/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                document = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ResearchDirectorTransportError(
                f"OpenRouter RD transport failed: HTTP {exc.code}: {detail}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ResearchDirectorTransportError(
                f"OpenRouter RD transport failed: {type(exc).__name__}: {exc}"
            ) from exc

        try:
            content = document["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ResearchDirectorTransportError(
                "OpenRouter response is missing choices[0].message.content"
            ) from exc
        if not isinstance(content, str) or not content.strip():
            raise ResearchDirectorTransportError("OpenRouter RD returned no textual decision")

        usage = document.get("usage")
        if not isinstance(usage, Mapping):
            raise ResearchDirectorTransportError("OpenRouter RD response omitted usage")
        direct_cost = usage.get("cost")
        if not isinstance(direct_cost, (int, float)) or float(direct_cost) < 0:
            raise ResearchDirectorTransportError("OpenRouter RD response omitted actual usage.cost")
        call_cost = float(direct_cost)
        self._openrouter_calls += 1
        self._openrouter_spend += call_cost
        self._write_telemetry(
            {
                "event": "OPENROUTER_RD_CALL_COMPLETE",
                "operation": self._operation(messages),
                "model": self._model,
                "elapsed_seconds": time.monotonic() - started,
                "usage": dict(usage),
                "actual_call_cost_usd": call_cost,
                "actual_cumulative_spend_usd": self._openrouter_spend,
                "completed_calls": self._openrouter_calls,
                "response_id": document.get("id"),
                "resolved_model": document.get("model"),
                "provider": document.get("provider"),
            }
        )
        return content
