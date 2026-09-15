from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .acceptance_controls import BLINDED_CONTROLS
from .derived_market_store import DerivedMarketQuery, DerivedMarketStore


class ControlReadinessError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class HiddenControlAnswer:
    control_id: str
    formulation: str
    expected_direction: str
    expected_horizons: tuple[str, ...]
    robustness_conditions: tuple[str, ...]
    independent_benchmark_artifact_sha256: str
    dataset_fingerprint_sha256: str
    assessor: str


def canonical_json_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _placeholder(value: object) -> bool:
    if isinstance(value, str):
        text = value.strip().lower()
        return not text or "<" in text or "placeholder" in text or "todo" in text or "tbd" in text
    if isinstance(value, Mapping):
        return any(_placeholder(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return not value or any(_placeholder(item) for item in value)
    return value is None


def load_hidden_answer_key(path: str | Path) -> Mapping[str, HiddenControlAnswer]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ControlReadinessError("hidden control answer key must be a JSON object")
    expected = {item.control_id for item in BLINDED_CONTROLS}
    if set(raw) != expected:
        raise ControlReadinessError("hidden answer key must contain exactly the five blinded controls")
    output: dict[str, HiddenControlAnswer] = {}
    for control_id in sorted(expected):
        item = raw[control_id]
        if not isinstance(item, Mapping):
            raise ControlReadinessError(f"hidden answer for {control_id} must be an object")
        answer = HiddenControlAnswer(
            control_id=control_id,
            formulation=str(item.get("formulation", "")).strip(),
            expected_direction=str(item.get("expected_direction", "")).strip(),
            expected_horizons=tuple(str(value).strip() for value in item.get("expected_horizons", ())),
            robustness_conditions=tuple(str(value).strip() for value in item.get("robustness_conditions", ())),
            independent_benchmark_artifact_sha256=str(item.get("independent_benchmark_artifact_sha256", "")).strip().lower(),
            dataset_fingerprint_sha256=str(item.get("dataset_fingerprint_sha256", "")).strip().lower(),
            assessor=str(item.get("assessor", "")).strip(),
        )
        if (
            _placeholder(answer.formulation)
            or _placeholder(answer.expected_direction)
            or _placeholder(answer.expected_horizons)
            or _placeholder(answer.robustness_conditions)
            or _placeholder(answer.assessor)
            or len(answer.independent_benchmark_artifact_sha256) != 64
            or len(answer.dataset_fingerprint_sha256) != 64
            or any(character not in "0123456789abcdef" for character in answer.independent_benchmark_artifact_sha256 + answer.dataset_fingerprint_sha256)
        ):
            raise ControlReadinessError(f"hidden answer for {control_id} is incomplete or not SHA-256 bound")
        output[control_id] = answer
    return output


def _finite(value: object) -> bool:
    if isinstance(value, bool):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _surface(store: DerivedMarketStore, query: DerivedMarketQuery, columns: Sequence[str]) -> Mapping[str, Any]:
    rows = store.query(query)
    identities: set[tuple[str, str]] = set()
    dates: set[str] = set()
    securities: set[str] = set()
    complete = {column: 0 for column in columns}
    fingerprint_rows = []
    duplicates = 0
    for row in rows:
        security_id = str(row.get("security_id", "")).strip()
        effective_date = str(row.get("effective_date", "")).strip()
        key = (security_id, effective_date)
        if key in identities:
            duplicates += 1
        identities.add(key)
        if row.get("eligible", True):
            dates.add(effective_date)
            securities.add(security_id)
            for column in columns:
                if _finite(row.get(column)):
                    complete[column] += 1
        fingerprint_rows.append({key: row.get(key) for key in ("security_id", "effective_date", "eligible", *columns)})
    return {
        "rows": len(rows),
        "eligible_dates": len(dates),
        "eligible_securities": len(securities),
        "duplicate_identities": duplicates,
        "complete_numeric_rows": complete,
        "fingerprint_sha256": canonical_json_sha256(fingerprint_rows),
    }


def build_control_readiness_report(
    config: Mapping[str, object],
    answer_key: Mapping[str, HiddenControlAnswer],
    store: DerivedMarketStore,
) -> Mapping[str, Any]:
    expected = tuple(item.control_id for item in BLINDED_CONTROLS)
    failures: list[str] = []
    controls: dict[str, Any] = {}
    if set(config) != set(expected):
        failures.append("control config must contain exactly the five blinded controls")
    if set(answer_key) != set(expected):
        failures.append("hidden answer key must contain exactly the five blinded controls")

    for control_id in expected:
        item = config.get(control_id)
        if not isinstance(item, Mapping):
            failures.append(f"{control_id}: configuration missing")
            continue
        required = (
            "universe_id", "feature_set_id", "feature_set_version", "feature_columns",
            "outcome_feature_set_id", "outcome_feature_set_version", "outcome_feature_columns",
            "minimum_eligible_dates", "minimum_eligible_securities", "minimum_complete_rows_per_column",
            "historical_membership_classification",
        )
        missing = [key for key in required if key not in item or _placeholder(item[key])]
        if missing:
            failures.append(f"{control_id}: missing or placeholder fields {missing}")
            continue
        universe_id = str(item["universe_id"])
        universe = store.get_universe(universe_id)
        if universe is None:
            failures.append(f"{control_id}: unknown universe {universe_id}")
            continue
        if _placeholder(universe.membership_source):
            failures.append(f"{control_id}: universe membership source is not identified")
        membership_classification = str(item["historical_membership_classification"])
        allowed_membership_classifications = {
            "AUTHORITATIVE_HISTORICAL_POINT_IN_TIME",
            "CURRENT_MEMBER_CONDITIONED",
        }
        if membership_classification not in allowed_membership_classifications:
            failures.append(
                f"{control_id}: historical_membership_classification must be one of "
                f"{sorted(allowed_membership_classifications)}"
            )
        predictor_columns = tuple(str(value) for value in item["feature_columns"])
        outcome_columns = tuple(str(value) for value in item["outcome_feature_columns"])
        predictor_set = store.get_feature_set(str(item["feature_set_id"]), str(item["feature_set_version"]))
        outcome_set = store.get_feature_set(str(item["outcome_feature_set_id"]), str(item["outcome_feature_set_version"]))
        if predictor_set is None or not set(predictor_columns).issubset(predictor_set.feature_columns):
            failures.append(f"{control_id}: predictor feature set/columns unavailable")
            continue
        if outcome_set is None or not set(outcome_columns).issubset(outcome_set.feature_columns):
            failures.append(f"{control_id}: outcome feature set/columns unavailable")
            continue
        predictor_query = DerivedMarketQuery(
            universe_id=universe_id,
            feature_set_id=str(item["feature_set_id"]),
            feature_set_version=str(item["feature_set_version"]),
            start_date=str(item.get("start_date")) if item.get("start_date") else None,
            end_date=str(item.get("end_date")) if item.get("end_date") else None,
            security_ids=tuple(str(value) for value in item.get("security_ids", ())),
            feature_columns=predictor_columns,
        )
        outcome_query = DerivedMarketQuery(
            universe_id=universe_id,
            feature_set_id=str(item["outcome_feature_set_id"]),
            feature_set_version=str(item["outcome_feature_set_version"]),
            start_date=predictor_query.start_date,
            end_date=predictor_query.end_date,
            security_ids=predictor_query.security_ids,
            feature_columns=outcome_columns,
        )
        predictor = _surface(store, predictor_query, predictor_columns)
        outcome = _surface(store, outcome_query, outcome_columns)
        minimum_dates = int(item["minimum_eligible_dates"])
        minimum_securities = int(item["minimum_eligible_securities"])
        minimum_complete = int(item["minimum_complete_rows_per_column"])
        for name, surface in (("predictor", predictor), ("outcome", outcome)):
            if surface["duplicate_identities"]:
                failures.append(f"{control_id}: {name} surface contains duplicate identities")
            if surface["eligible_dates"] < minimum_dates:
                failures.append(f"{control_id}: {name} surface has insufficient eligible dates")
            if surface["eligible_securities"] < minimum_securities:
                failures.append(f"{control_id}: {name} surface has insufficient eligible securities")
            if any(count < minimum_complete for count in surface["complete_numeric_rows"].values()):
                failures.append(f"{control_id}: {name} surface has insufficient complete numeric observations")
        dataset_fingerprint = canonical_json_sha256({
            "control_id": control_id,
            "config": item,
            "predictor": predictor["fingerprint_sha256"],
            "outcome": outcome["fingerprint_sha256"],
        })
        answer = answer_key.get(control_id)
        if answer is None or answer.dataset_fingerprint_sha256 != dataset_fingerprint:
            failures.append(f"{control_id}: hidden answer key is not bound to this exact dataset")
        controls[control_id] = {
            "universe_membership": {
                "source": universe.membership_source,
                "classification": membership_classification,
                "point_in_time_membership_required_by_store_definition": universe.point_in_time_membership_required,
                "limitation": (
                    None
                    if membership_classification == "AUTHORITATIVE_HISTORICAL_POINT_IN_TIME"
                    else "FORMER_CONSTITUENTS_ARE_ABSENT; RESULTS_DESCRIBE_THE_HISTORIES_OF_THE_CURRENT_MEMBER_POPULATION_AND_ARE_NOT_AN_AUTHORITATIVE_HISTORICAL_INDEX_RECONSTRUCTION"
                ),
            },
            "predictor_surface": predictor,
            "outcome_surface": outcome,
            "dataset_fingerprint_sha256": dataset_fingerprint,
            "hidden_answer_key_bound": bool(answer and answer.dataset_fingerprint_sha256 == dataset_fingerprint),
        }

    return {
        "format": "MTS_V4_CONTROL_READINESS_V1",
        "config_sha256": canonical_json_sha256(config),
        "controls": controls,
        "failures": failures,
        "status": "READY_FOR_BLINDED_CALIBRATION" if not failures else "NOT_READY",
        "sol_calls": 0,
        "scientific_grade_assigned": False,
    }


def require_ready_report(path: str | Path, config: Mapping[str, object]) -> Mapping[str, Any]:
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(report, Mapping):
        raise ControlReadinessError("control readiness report must be a JSON object")
    if report.get("status") != "READY_FOR_BLINDED_CALIBRATION":
        raise ControlReadinessError("control readiness report has not passed")
    if report.get("config_sha256") != canonical_json_sha256(config):
        raise ControlReadinessError("control readiness report belongs to different control configuration")
    if report.get("sol_calls") != 0 or report.get("scientific_grade_assigned") is not False:
        raise ControlReadinessError("control readiness report violates mechanical preflight boundary")
    return report


def require_calibration_pass(path: str | Path) -> Mapping[str, Any]:
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(report, Mapping) or report.get("overall_status") != "CALIBRATION_PASS":
        raise ControlReadinessError("open-ended universe discovery requires a completed CALIBRATION_PASS control campaign")
    if not report.get("all_five_controls_present") or not report.get("all_runs_completed") or not report.get("all_controls_assessed"):
        raise ControlReadinessError("calibration report is incomplete")
    return report


def require_ready_control(path: str | Path, control_id: str) -> Mapping[str, Any]:
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    controls = report.get("controls") if isinstance(report, Mapping) else None
    item = controls.get(control_id) if isinstance(controls, Mapping) else None
    if (
        report.get("status") != "READY_FOR_BLINDED_CALIBRATION"
        or not isinstance(item, Mapping)
        or item.get("hidden_answer_key_bound") is not True
        or report.get("sol_calls") != 0
    ):
        raise ControlReadinessError(
            f"control {control_id} lacks a passing dataset-bound zero-SOL readiness report"
        )
    return report
