from __future__ import annotations

import copy
import json
import os
import urllib.error
import urllib.request
from datetime import date as date_type, datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

from MTS_V4.bootstrap import build_runtime
from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.campaign import CheckpointedCampaignRunner
from MTS_V4.checkpoint import JsonCampaignCheckpointStore
from MTS_V4.decision_journal import JsonResearchDecisionJournal
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import (
    CompositeEvidenceSource,
    FinraWeeklyOffExchangeSource,
    UnusualWhalesDarkPoolPriceLevelsSource,
    UnusualWhalesFlowAlertsSource,
    UnusualWhalesFlowByExpirySource,
    UnusualWhalesGreekExposureByExpirySource,
    YFinanceDailyOhlcvSource,
)
from MTS_V4.openai_compatible_provider import ResearchDirectorTransportError
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.research_recording import CampaignResearchRecorder
from MTS_V4.sol_provider import SolResearchPackageAwareResearchDirector
from MTS_V4.contracts import SubjectMetadata


MODELS = (
    ("terra", "gpt-5.6-terra"),
    ("sol", "gpt-5.6-sol"),
)
DEFAULT_EVIDENCE_AS_OF = "2026-09-10"


class MeteredOpenAIResearchDirector(SolResearchPackageAwareResearchDirector):
    """OpenAI RD transport that journals provider-reported token usage for this experiment."""

    def __init__(
        self,
        *,
        usage_path: Path,
        reasoning_effort: str,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self._usage_path = usage_path
        self._reasoning_effort = reasoning_effort
        self._call_sequence = 0

    def _chat_completion(self, messages: Sequence[Mapping[str, str]]) -> str:
        self._call_sequence += 1
        body_document = {
            "model": self._model,
            "messages": list(messages),
            "reasoning_effort": self._reasoning_effort,
        }
        body = json.dumps(body_document, separators=(",", ":")).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        request = urllib.request.Request(
            f"{self._base_url}/v1/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                document = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                response_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                response_body = ""
            detail = f"; response_body={response_body}" if response_body else ""
            raise ResearchDirectorTransportError(
                f"AI Research Director transport failed: HTTPError: {exc}{detail}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ResearchDirectorTransportError(
                f"AI Research Director transport failed: {type(exc).__name__}: {exc}"
            ) from exc

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

        usage_record = {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "call_sequence": self._call_sequence,
            "model": document.get("model", self._model),
            "reasoning_effort": self._reasoning_effort,
            "response_id": document.get("id"),
            "prompt_character_count": sum(len(str(item.get("content", ""))) for item in messages),
            "response_character_count": len(content),
            "usage": document.get("usage", {}),
        }
        self._usage_path.parent.mkdir(parents=True, exist_ok=True)
        with self._usage_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(usage_record, sort_keys=True, default=str) + "\n")

        return content


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _comparison_live_market_source(as_of_date: date_type) -> CompositeEvidenceSource:
    """Acquire one controlled AAPL evidence snapshot for both model arms.

    The Unusual Whales dark-pool price-level endpoint rejects future market dates.
    Pinning its end date prevents a UTC-midnight rollover from requesting the next
    calendar date while the U.S. market/source still considers the prior session current.
    All acquired evidence is staged once and deep-copied to both model runtimes.
    """
    return CompositeEvidenceSource(
        YFinanceDailyOhlcvSource(),
        UnusualWhalesDarkPoolPriceLevelsSource(end_date=as_of_date),
        UnusualWhalesFlowAlertsSource(),
        UnusualWhalesGreekExposureByExpirySource(),
        UnusualWhalesFlowByExpirySource(),
        FinraWeeklyOffExchangeSource(),
    )


def _copy_staged_evidence(source_cache: TemporaryResearchCache, destination_cache: TemporaryResearchCache) -> None:
    for cache_key in source_cache.active_keys():
        destination_cache.put(cache_key, copy.deepcopy(source_cache.get(cache_key)))


def _usage_summary(path: Path) -> dict[str, int]:
    totals = {
        "calls": 0,
        "prompt_tokens": 0,
        "cached_tokens": 0,
        "completion_tokens": 0,
        "reasoning_tokens": 0,
        "total_tokens": 0,
    }
    if not path.exists():
        return totals
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            usage = row.get("usage") or {}
            prompt_details = usage.get("prompt_tokens_details") or {}
            completion_details = usage.get("completion_tokens_details") or {}
            totals["calls"] += 1
            totals["prompt_tokens"] += int(usage.get("prompt_tokens") or 0)
            totals["cached_tokens"] += int(prompt_details.get("cached_tokens") or 0)
            totals["completion_tokens"] += int(usage.get("completion_tokens") or 0)
            totals["reasoning_tokens"] += int(completion_details.get("reasoning_tokens") or 0)
            totals["total_tokens"] += int(usage.get("total_tokens") or 0)
    return totals


def _run_arm(
    *,
    label: str,
    model: str,
    root_dir: Path,
    staged_cache: TemporaryResearchCache,
    evidence: tuple,
    subject: SubjectMetadata,
    max_analyses: int,
    timeout_seconds: int,
    reasoning_effort: str,
) -> None:
    state_dir = root_dir / label
    state_dir.mkdir(parents=True, exist_ok=False)
    usage_path = state_dir / "api_usage.jsonl"
    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    rd = MeteredOpenAIResearchDirector(
        usage_path=usage_path,
        reasoning_effort=reasoning_effort,
        research_package_store=package_store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=model,
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=timeout_seconds,
    )
    runtime = build_runtime(
        rd=rd,
        nexus_path=state_dir / "research_nexus.json",
        max_contract_repairs=4,
    )
    _copy_staged_evidence(staged_cache, runtime.cache)

    checkpoint_store = JsonCampaignCheckpointStore(state_dir / "checkpoint.json")
    recorder = CampaignResearchRecorder(
        package_store=package_store,
        decision_journal=JsonResearchDecisionJournal(state_dir / "rd_decisions.jsonl"),
    )
    runner = CheckpointedCampaignRunner(
        orchestrator=runtime.orchestrator,
        cache=runtime.cache,
        checkpoint_store=checkpoint_store,
        research_recorder=recorder,
    )
    campaign_id = f"mts-v4-aapl-{label}-rd-comparison-{root_dir.name}"

    print(f"=== {label.upper()} ARM START ===", flush=True)
    print(f"MODEL={model}", flush=True)
    print(f"REASONING_EFFORT={reasoning_effort}", flush=True)
    print(f"STATE_DIR={state_dir}", flush=True)
    try:
        outcome = runner.run_new(
            campaign_id=campaign_id,
            subject=subject,
            evidence=evidence,
            max_analyses=max_analyses,
        )
        print(f"OUTCOME_DECISIONS={outcome.decisions}", flush=True)
        print(f"OUTCOME_ANALYSES={outcome.analyses_executed}", flush=True)
        print(f"OUTCOME_FINDINGS_PROMOTED={outcome.findings_promoted}", flush=True)
        print(f"OUTCOME_CLOSED={outcome.closed}", flush=True)
        print(f"OUTCOME_CLOSE_REASON={outcome.close_reason}", flush=True)
        print(
            "FINAL_DECISION="
            + json.dumps(
                {
                    "continue_research": outcome.final_decision.continue_research,
                    "rp_id": outcome.final_decision.rp_id,
                    "close_reason": outcome.final_decision.close_reason,
                    "research_state": outcome.final_decision.research_state,
                },
                sort_keys=True,
                default=str,
            ),
            flush=True,
        )
    except Exception as exc:
        print(f"ARM_EXCEPTION={type(exc).__name__}: {exc}", flush=True)
    finally:
        print("API_USAGE=" + json.dumps(_usage_summary(usage_path), sort_keys=True), flush=True)
        print(f"=== {label.upper()} ARM END ===", flush=True)


def main() -> None:
    max_analyses = int(os.getenv("MTS_E2E_MAX_ANALYSES", "500"))
    timeout_seconds = int(os.getenv("MTS_RD_TIMEOUT_SECONDS", "600"))
    reasoning_effort = os.getenv("MTS_OPENAI_REASONING_EFFORT", "medium").strip() or "medium"
    evidence_as_of_text = os.getenv("MTS_COMPARISON_EVIDENCE_AS_OF", DEFAULT_EVIDENCE_AS_OF).strip()
    evidence_as_of = date_type.fromisoformat(evidence_as_of_text)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    root_dir = Path(f"/home/ubuntu/mts-v4-aapl-terra-sol-comparison-{stamp}")
    root_dir.mkdir(parents=True, exist_ok=False)

    subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")
    staged_cache = TemporaryResearchCache()
    evidence = tuple(
        IntakeEngine(staged_cache).ingest(
            subject=subject,
            source=_comparison_live_market_source(evidence_as_of),
        )
    )

    print(f"COMPARISON_ROOT={root_dir}", flush=True)
    print(f"EVIDENCE_AS_OF={evidence_as_of.isoformat()}", flush=True)
    print(f"EVIDENCE_COUNT={len(evidence)}", flush=True)
    for item in evidence:
        print(
            "EVIDENCE="
            + json.dumps(
                {
                    "evidence_id": item.evidence_id,
                    "evidence_type": item.evidence_type,
                    "source_identity": item.source_identity,
                    "coverage_start": item.coverage_start,
                    "coverage_end": item.coverage_end,
                    "row_count": item.row_count,
                    "schema": list(item.schema),
                },
                sort_keys=True,
                default=str,
            ),
            flush=True,
        )

    for label, model in MODELS:
        _run_arm(
            label=label,
            model=model,
            root_dir=root_dir,
            staged_cache=staged_cache,
            evidence=evidence,
            subject=subject,
            max_analyses=max_analyses,
            timeout_seconds=timeout_seconds,
            reasoning_effort=reasoning_effort,
        )

    print(f"COMPARISON_COMPLETE={root_dir}", flush=True)


if __name__ == "__main__":
    main()
