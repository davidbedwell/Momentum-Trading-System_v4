from __future__ import annotations

import json

import pytest

from MTS_V4.equivalence_appeal import collect_complete_hybrid_record, create_blinded_packet
from MTS_V4.virgin_equivalence import freeze_arm_manifest


def test_complete_hybrid_record_includes_gemini_work_and_analysis(tmp_path):
    root = tmp_path / "gemini"
    (root / "research_packages").mkdir(parents=True)
    (root / "decisions.json").write_text(json.dumps({"decisions": [{"x": 1}]}))
    (root / "reports.json").write_text(json.dumps({"reports": [{"records": [{"analysis_id": "a2", "result": {"result_id": "r2", "value": 7}}]}]}))
    (root / "outcome.json").write_text(json.dumps({"outcome": {"closed": True}, "precomputed_results": {"a1": {"z": 3}}}))
    (root / "research_packages" / "rp.json").write_text(json.dumps({"research_package": {"subject_id": "ABC"}}))
    work, analyses = collect_complete_hybrid_record(root)
    assert len(work) == 4
    assert analyses == [{"analysis_id": "a2", "result": {"result_id": "r2", "value": 7}}, {"analysis_id": "a1", "result": {"z": 3}}]


def test_missing_hybrid_artifact_fails_closed(tmp_path):
    root = tmp_path / "gemini"
    root.mkdir()
    with pytest.raises(Exception, match="hybrid record missing"):
        collect_complete_hybrid_record(root)


def test_blinded_packet_contains_neither_identity_nor_usage(tmp_path):
    direct = freeze_arm_manifest(subject_id="ABC", arm="DIRECT_SOL", starting_sha256="s", artifacts=[{"path": "/tmp/DIRECT_SOL/a.json"}], usage=[{"cost": 10}], complete=True, scientific_record={"finding": "direct"})
    hybrid = freeze_arm_manifest(subject_id="ABC", arm="GEMINI_SOL_HYBRID", starting_sha256="s", artifacts=[{"path": "/tmp/GEMINI_SOL_HYBRID/b.json"}], usage=[{"cost": 5}], complete=True, scientific_record={"finding": "hybrid"})
    packet = create_blinded_packet(direct_manifest=direct, hybrid_manifest=hybrid, output=tmp_path / "blind.json", salt="secret")
    rendered = json.dumps(packet)
    assert "DIRECT_SOL" not in rendered
    assert "GEMINI_SOL_HYBRID" not in rendered
    assert '"usage"' not in rendered
    assert "/tmp/DIRECT_SOL" not in rendered
    assert "/tmp/GEMINI_SOL_HYBRID" not in rendered
    assert '"scientific_record"' in rendered
    assert "direct" in rendered and "hybrid" in rendered


def test_waiting_for_future_cohorts_is_valid_complete_arm_state():
    manifest = freeze_arm_manifest(
        subject_id="ABC",
        arm="DIRECT_SOL",
        starting_sha256="s",
        artifacts=[{"a": 1}],
        usage=[{"actual_spend_usd": 1.0}],
        complete=True,
        terminal_state="WAITING_FOR_FUTURE_COHORTS",
        scientific_record={"outcome": {"waiting_for_future_cohorts": True}},
    )
    assert manifest["complete"] is True
    assert manifest["terminal_state"] == "WAITING_FOR_FUTURE_COHORTS"


def test_invalid_complete_arm_terminal_state_fails_closed():
    with pytest.raises(Exception, match="invalid complete-arm terminal state"):
        freeze_arm_manifest(
            subject_id="ABC",
            arm="DIRECT_SOL",
            starting_sha256="s",
            artifacts=[{"a": 1}],
            usage=[{"actual_spend_usd": 1.0}],
            complete=True,
            terminal_state="PARTIAL",
        )
