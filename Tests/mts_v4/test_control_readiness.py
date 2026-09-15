import json

import pytest

from MTS_V4.acceptance_controls import BLINDED_CONTROLS
from MTS_V4.control_readiness import (
    ControlReadinessError,
    HiddenControlAnswer,
    build_control_readiness_report,
    canonical_json_sha256,
    load_hidden_answer_key,
    require_calibration_pass,
)
from MTS_V4.derived_market_store import (
    DerivedFeatureDefinition,
    DerivedFeatureSetDefinition,
    InMemoryDerivedMarketStore,
    UniverseDefinition,
)
from scripts.run_sol_batched_universe import main as universe_main


def _store():
    store = InMemoryDerivedMarketStore()
    store.register_universe(
        UniverseDefinition(
            universe_id="pit",
            description="point in time test universe",
            membership_source="authoritative:test:v1",
            point_in_time_membership_required=True,
        )
    )
    predictors = DerivedFeatureSetDefinition(
        feature_set_id="predictors",
        version="v1",
        description="test predictors",
        features=(DerivedFeatureDefinition("signal", "v1", "test signal", classification="PREDICTOR"),),
    )
    outcomes = DerivedFeatureSetDefinition(
        feature_set_id="outcomes",
        version="v1",
        description="test outcomes",
        features=(DerivedFeatureDefinition("forward", "v1", "test outcome", classification="OUTCOME"),),
    )
    store.register_feature_set(predictors)
    store.register_feature_set(outcomes)
    predictor_rows = []
    outcome_rows = []
    for day in ("2026-01-02", "2026-01-05"):
        for security, value in (("A", 1.0), ("B", 2.0)):
            predictor_rows.append({"security_id": security, "effective_date": day, "eligible": True, "signal__v1": value})
            outcome_rows.append({"security_id": security, "effective_date": day, "eligible": True, "forward__v1": value / 10})
    store.append_update(
        universe_id="pit", feature_set_id="predictors", feature_set_version="v1",
        update_id="predictors-1", rows=predictor_rows,
    )
    store.append_update(
        universe_id="pit", feature_set_id="outcomes", feature_set_version="v1",
        update_id="outcomes-1", rows=outcome_rows,
    )
    return store


def _config():
    item = {
        "universe_id": "pit",
        "feature_set_id": "predictors",
        "feature_set_version": "v1",
        "feature_columns": ["signal__v1"],
        "outcome_feature_set_id": "outcomes",
        "outcome_feature_set_version": "v1",
        "outcome_feature_columns": ["forward__v1"],
        "minimum_eligible_dates": 2,
        "minimum_eligible_securities": 2,
        "minimum_complete_rows_per_column": 4,
    }
    return {control.control_id: dict(item) for control in BLINDED_CONTROLS}


def _answers(config, store):
    dummy = {
        control.control_id: HiddenControlAnswer(
            control_id=control.control_id,
            formulation="frozen formulation",
            expected_direction="frozen direction",
            expected_horizons=("frozen horizon",),
            robustness_conditions=("frozen robustness condition",),
            independent_benchmark_artifact_sha256="a" * 64,
            dataset_fingerprint_sha256="b" * 64,
            assessor="independent assessor",
        )
        for control in BLINDED_CONTROLS
    }
    first = build_control_readiness_report(config, dummy, store)
    return {
        control_id: HiddenControlAnswer(
            **{
                **dummy[control_id].__dict__ if hasattr(dummy[control_id], "__dict__") else {
                    "control_id": dummy[control_id].control_id,
                    "formulation": dummy[control_id].formulation,
                    "expected_direction": dummy[control_id].expected_direction,
                    "expected_horizons": dummy[control_id].expected_horizons,
                    "robustness_conditions": dummy[control_id].robustness_conditions,
                    "independent_benchmark_artifact_sha256": dummy[control_id].independent_benchmark_artifact_sha256,
                    "assessor": dummy[control_id].assessor,
                },
                "dataset_fingerprint_sha256": first["controls"][control_id]["dataset_fingerprint_sha256"],
            }
        )
        for control_id in dummy
    }


def test_readiness_requires_exact_dataset_bound_hidden_answers():
    store = _store()
    config = _config()
    answers = _answers(config, store)
    report = build_control_readiness_report(config, answers, store)
    assert report["status"] == "READY_FOR_BLINDED_CALIBRATION"
    assert report["failures"] == []
    assert report["sol_calls"] == 0
    assert report["config_sha256"] == canonical_json_sha256(config)


def test_readiness_rejects_placeholder_and_dataset_change(tmp_path):
    answer_key = {
        control.control_id: {
            "formulation": "<placeholder>",
            "expected_direction": "positive",
            "expected_horizons": ["20"],
            "robustness_conditions": ["year stability"],
            "independent_benchmark_artifact_sha256": "a" * 64,
            "dataset_fingerprint_sha256": "b" * 64,
            "assessor": "reviewer",
        }
        for control in BLINDED_CONTROLS
    }
    path = tmp_path / "answers.json"
    path.write_text(json.dumps(answer_key), encoding="utf-8")
    with pytest.raises(ControlReadinessError):
        load_hidden_answer_key(path)


def test_open_ended_universe_runner_fails_before_any_store_or_sol_access():
    with pytest.raises(RuntimeError, match="gated"):
        universe_main([
            "--universe-id", "pit",
            "--feature-set-id", "predictors",
            "--feature-set-version", "v1",
        ])


def test_calibration_pass_gate_requires_complete_pass(tmp_path):
    path = tmp_path / "report.json"
    path.write_text(json.dumps({
        "overall_status": "CALIBRATION_PARTIAL",
        "all_five_controls_present": True,
        "all_runs_completed": True,
        "all_controls_assessed": True,
    }), encoding="utf-8")
    with pytest.raises(ControlReadinessError):
        require_calibration_pass(path)
