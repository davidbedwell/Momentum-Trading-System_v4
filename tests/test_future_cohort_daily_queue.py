from __future__ import annotations

import json
from types import SimpleNamespace

from MTS_V4 import future_cohort_waiting as waiting


def _entry(subject_id: str, suffix: str) -> dict[str, object]:
    return {
        "subject_id": subject_id,
        "status": waiting.WAITING_FOR_FUTURE_COHORTS,
        "validation_state": f"validation-{suffix}",
        "research_package_dir": f"packages-{suffix}",
        "rp_id": f"RP-{suffix}",
        "authoritative_snapshot": f"snapshot-{suffix}.json",
        "public_condition_feed": f"feed-{suffix}.json",
    }


def test_daily_queue_keeps_unresolved_tickers_waiting_and_resolves_only_complete(
    tmp_path, monkeypatch
):
    manifest_path = tmp_path / "waiting.json"
    manifest_path.write_text(
        json.dumps(
            {
                "format": "MTS_V4_FUTURE_COHORT_WAITING_V1",
                "entries": [
                    _entry("equity:XOM", "XOM"),
                    _entry("equity:AAPL", "AAPL"),
                ],
            }
        ),
        encoding="utf-8",
    )

    class FakeProtocol:
        def __init__(self, subject_id: str) -> None:
            self.source_subject_id = subject_id
            self.protocol_id = "protocol:" + subject_id
            self.fingerprint = "fingerprint:" + subject_id

    class FakeValidationStore:
        def __init__(self, path: str) -> None:
            self.path = path

        def load(self):
            subject_id = "equity:XOM" if self.path.endswith("XOM") else "equity:AAPL"
            return FakeProtocol(subject_id), object()

    monkeypatch.setattr(waiting, "JsonProspectiveValidationStore", FakeValidationStore)
    monkeypatch.setattr(waiting, "JsonResearchPackageStore", lambda path: object())
    monkeypatch.setattr(waiting, "load_authoritative_sessions", lambda path: [object()])
    monkeypatch.setattr(waiting, "build_public_condition_feed", lambda **kwargs: [object()])
    monkeypatch.setattr(waiting, "save_public_condition_feed", lambda *args, **kwargs: None)

    def fake_advance(*, protocol_store, **kwargs):
        complete = protocol_store.path.endswith("AAPL")
        return SimpleNamespace(
            frontier_state="COMPLETE" if complete else "IN_PROGRESS",
            newly_locked_trials=("trial:1",) if not complete else (),
            next_trial_id=None if complete else "trial:2",
            gate_closed_through_session_index=100,
        )

    monkeypatch.setattr(waiting, "advance_matching_runtime", fake_advance)

    result = waiting.evaluate_waiting_manifest(
        manifest_path,
        as_of_utc="2026-09-14T23:59:59+00:00",
    )

    assert result.evaluated == 2
    assert result.still_waiting == 1
    assert result.resolved == 1
    assert result.objective_defects == 0

    saved = json.loads(manifest_path.read_text(encoding="utf-8"))
    statuses = {entry["subject_id"]: entry["status"] for entry in saved["entries"]}
    assert statuses == {
        "equity:XOM": waiting.WAITING_FOR_FUTURE_COHORTS,
        "equity:AAPL": waiting.RESOLVED,
    }


def test_objective_runtime_defect_leaves_ticker_waiting(tmp_path, monkeypatch):
    manifest_path = tmp_path / "waiting.json"
    manifest_path.write_text(
        json.dumps(
            {
                "format": "MTS_V4_FUTURE_COHORT_WAITING_V1",
                "entries": [_entry("equity:XOM", "XOM")],
            }
        ),
        encoding="utf-8",
    )

    class BrokenValidationStore:
        def __init__(self, path: str) -> None:
            self.path = path

        def load(self):
            raise waiting.ProspectiveValidationError("future cohort is not mechanically evaluable yet")

    monkeypatch.setattr(waiting, "JsonProspectiveValidationStore", BrokenValidationStore)

    result = waiting.evaluate_waiting_manifest(
        manifest_path,
        as_of_utc="2026-09-14T23:59:59+00:00",
    )

    assert result.evaluated == 1
    assert result.still_waiting == 1
    assert result.resolved == 0
    assert result.objective_defects == 1

    saved = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry = saved["entries"][0]
    assert entry["status"] == waiting.WAITING_FOR_FUTURE_COHORTS
    assert "future cohort is not mechanically evaluable yet" in entry["objective_defect"]
