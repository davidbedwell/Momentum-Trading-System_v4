from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import ResearchDecision


class ResearchDecisionJournalError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_FORBIDDEN_DURABLE_KEYS = frozenset({"payload", "rows", "cache_key", "derived_datasets"})


def _durable_projection(value: Any) -> Any:
    """Remove temporary/raw data keys from an RD decision journal projection.

    The live ResearchDecision remains unchanged for execution. This projection is
    only for the append-only durable audit journal, whose contract forbids raw or
    cache-local evidence while preserving AI-authored scientific structure,
    lineage, parameters, and interpretation.
    """
    if isinstance(value, Mapping):
        return {
            str(key): _durable_projection(item)
            for key, item in value.items()
            if str(key) not in _FORBIDDEN_DURABLE_KEYS
        }
    if isinstance(value, tuple):
        return [_durable_projection(item) for item in value]
    if isinstance(value, list):
        return [_durable_projection(item) for item in value]
    return value


class JsonResearchDecisionJournal:
    """Append-only campaign audit record of unique AI RD decisions.

    This is an operational/scientific audit artifact, not Nexus scientific
    memory. Repeated checkpoint writes for the same RD decision sequence do not
    create duplicate journal entries.
    """

    FORMAT = "MTS_V4_RD_DECISION_JOURNAL_V1"

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def append(
        self,
        *,
        campaign_id: str,
        decision_sequence: int,
        analyses_executed: int,
        decision: ResearchDecision,
    ) -> None:
        if decision_sequence <= 0:
            raise ResearchDecisionJournalError("decision_sequence must be positive")
        existing = self._read_sequences(campaign_id)
        if decision_sequence in existing:
            return
        decision_projection = _durable_projection(asdict(decision))
        record = {
            "format": self.FORMAT,
            "recorded_at_utc": _utc_now(),
            "campaign_id": campaign_id,
            "decision_sequence": decision_sequence,
            "analyses_executed": analyses_executed,
            "decision": decision_projection,
        }
        serialized = json.dumps(record, sort_keys=True, default=str, separators=(",", ":"))
        forbidden = ('"payload"', '"rows"', '"cache_key"', '"derived_datasets"')
        if any(token in serialized for token in forbidden):
            raise ResearchDecisionJournalError(
                "RD decision journal attempted to persist raw/cache evidence data"
            )
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(serialized + "\n")

    def records(self, campaign_id: str | None = None) -> tuple[dict[str, Any], ...]:
        if not self._path.exists():
            return ()
        result: list[dict[str, Any]] = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            raw = json.loads(line)
            if raw.get("format") != self.FORMAT:
                raise ResearchDecisionJournalError("unsupported RD decision journal format")
            if campaign_id is None or raw.get("campaign_id") == campaign_id:
                result.append(raw)
        return tuple(result)

    def _read_sequences(self, campaign_id: str) -> set[int]:
        return {
            int(item["decision_sequence"])
            for item in self.records(campaign_id)
        }
