from __future__ import annotations

import math
from typing import Any, Mapping

import pandas as pd

from Core.deterministic_computation import execute_computations
from Core.deterministic_computation.registry import build_registry

from .analysis import RegisteredAnalysisMethod
from .method_catalog import MethodCatalog, MethodSpec, ParameterContract


DETERMINISTIC_FAMILY_METHOD_ID = "analysis.measurements.deterministic_family"
ARITHMETIC_METHOD_ID = "analysis.transform.arithmetic"


def _single_rows(evidence_payloads: Mapping[str, object]) -> tuple[Mapping[str, Any], ...]:
    if len(evidence_payloads) != 1:
        raise ValueError("discovery transform methods require exactly one resolved row dataset")
    payload = next(iter(evidence_payloads.values()))
    rows = tuple(payload)  # type: ignore[arg-type]
    if not all(isinstance(row, Mapping) for row in rows):
        raise ValueError("resolved dataset payload must be an iterable of row mappings")
    return rows


def _json_scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if hasattr(value, "item"):
        try:
            return _json_scalar(value.item())
        except Exception:
            pass
    return value


def _derived_dataset(name: str, rows: list[Mapping[str, Any]]) -> Mapping[str, Any]:
    schema = tuple(str(key) for key in rows[0]) if rows else ()
    return {
        "derived_dataset_catalog": {
            name: {
                "row_count": len(rows),
                "schema": list(schema),
                "output_path": ["derived_datasets", name],
                "temporary": True,
            }
        },
        "derived_datasets": {name: rows},
    }


def deterministic_family_measurements(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Materialize exact RD-selected active deterministic computation families.

    This exposes existing governed measurement capability to the autonomous RD.
    The method does not choose a family, measurement, parameterization, or
    scientific interpretation.
    """
    rows = _single_rows(evidence_payloads)
    families = tuple(str(value) for value in parameters["families"])
    registry = build_registry()
    active = {key for key, value in registry.items() if value.status == "ACTIVE"}
    unknown = [family for family in families if family not in active]
    if unknown:
        raise ValueError(f"requested family is not an active deterministic family: {unknown}")
    if len(set(families)) != len(families):
        raise ValueError("families must not contain duplicates")
    if not rows:
        return {
            "families": list(families),
            "measurement_columns": [],
            **_derived_dataset("deterministic_measurements", []),
            "interpretation_boundary": "MEASUREMENT_ONLY_RD_INTERPRETS",
        }

    required = ("date", "open", "high", "low", "close", "volume")
    missing = [column for column in required if any(column not in row for row in rows)]
    if missing:
        raise ValueError(f"canonical OHLCV columns required for deterministic families: {missing}")

    frame = pd.DataFrame([dict(row) for row in rows])
    canonical = frame.loc[:, list(required)].copy()
    result = execute_computations(canonical, families=list(families))
    measured = result.data.astype(object).where(pd.notna(result.data), None)
    output_rows = [
        {str(key): _json_scalar(value) for key, value in row.items()}
        for row in measured.to_dict(orient="records")
    ]
    measurement_columns = [column for column in measured.columns if column not in required]
    audit = result.audit.drop(columns=["elapsed_seconds"], errors="ignore").to_dict(orient="records")
    return {
        "families": list(families),
        "measurement_columns": measurement_columns,
        "audit": audit,
        **_derived_dataset("deterministic_measurements", output_rows),
        "interpretation_boundary": "GOVERNED_DETERMINISTIC_MEASUREMENTS_ONLY_RD_INTERPRETS",
    }


def _operand_value(spec: object, row: Mapping[str, Any]) -> float | None:
    if not isinstance(spec, Mapping):
        raise ValueError("operand must be an object with exactly one of column or literal")
    keys = set(spec)
    if keys == {"column"}:
        value = row.get(str(spec["column"]))
    elif keys == {"literal"}:
        value = spec["literal"]
    else:
        raise ValueError("operand must contain exactly one of column or literal")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def arithmetic_transform(
    evidence_payloads: Mapping[str, object],
    parameters: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Create one reusable RD-authored arithmetic feature without choosing science."""
    rows = _single_rows(evidence_payloads)
    operation = str(parameters["operation"]).upper()
    output_name = str(parameters["output_name"]).strip()
    if not output_name:
        raise ValueError("output_name cannot be blank")
    if output_name == "index":
        raise ValueError("output_name 'index' is reserved")

    operations = {
        "ADD": lambda left, right: left + right,
        "SUBTRACT": lambda left, right: left - right,
        "MULTIPLY": lambda left, right: left * right,
        "DIVIDE": lambda left, right: left / right,
    }
    if operation not in operations:
        raise ValueError(f"unsupported arithmetic operation: {operation}")

    output_rows: list[Mapping[str, Any]] = []
    excluded_non_numeric = 0
    excluded_zero_divisor = 0
    for index, row in enumerate(rows):
        left = _operand_value(parameters["left"], row)
        right = _operand_value(parameters["right"], row)
        if left is None or right is None:
            excluded_non_numeric += 1
            continue
        if operation == "DIVIDE" and right == 0:
            excluded_zero_divisor += 1
            continue
        value = operations[operation](left, right)
        if not math.isfinite(value):
            excluded_non_numeric += 1
            continue
        output_rows.append({"index": index, output_name: value})

    return {
        "operation": operation,
        "output_name": output_name,
        "observation_count": len(output_rows),
        "excluded_non_numeric": excluded_non_numeric,
        "excluded_zero_divisor": excluded_zero_divisor,
        **_derived_dataset("arithmetic_feature", output_rows),
        "interpretation_boundary": "RD_AUTHORED_ARITHMETIC_REPRESENTATION_ONLY_RD_INTERPRETS",
    }


def discovery_method_catalog() -> MethodCatalog:
    registry = build_registry()
    active_families = [
        {"family_id": key, "description": value.description, "version": value.version}
        for key, value in registry.items()
        if value.status == "ACTIVE"
    ]
    return MethodCatalog(
        [
            MethodSpec(
                DETERMINISTIC_FAMILY_METHOD_ID,
                ("NORMALIZED_DATASET",),
                (
                    "Materialize all governed measurements from one or more exact RD-selected active "
                    "deterministic computation families against canonical OHLCV, returning a reusable "
                    "row-level dataset. Analysis does not rank families or select measurements."
                ),
                (
                    ParameterContract(
                        "families",
                        True,
                        (list, tuple),
                        minimum_length=1,
                        meaning="one or more exact active family_id values selected by RD",
                    ),
                ),
                2,
                metadata={
                    "active_families": active_families,
                    "reusable_derived_dataset": True,
                    "derived_dataset_name": "deterministic_measurements",
                    "scientific_selection": "AI_RESEARCH_DIRECTOR_ONLY",
                    "deterministic_ranking": False,
                },
            ),
            MethodSpec(
                ARITHMETIC_METHOD_ID,
                ("NORMALIZED_DATASET",),
                (
                    "Create one reusable row-level arithmetic feature from exact RD-selected column and/or "
                    "literal operands. Useful for scientifically authored ratios, spreads, differences, "
                    "scaling, and interaction terms without Analysis choosing the representation."
                ),
                (
                    ParameterContract(
                        "left",
                        True,
                        (dict,),
                        meaning="RD-authored operand: exactly {'column': field} or {'literal': number}",
                    ),
                    ParameterContract(
                        "right",
                        True,
                        (dict,),
                        meaning="RD-authored operand: exactly {'column': field} or {'literal': number}",
                    ),
                    ParameterContract(
                        "operation",
                        True,
                        (str,),
                        allowed_values=("ADD", "SUBTRACT", "MULTIPLY", "DIVIDE"),
                        meaning="exact arithmetic operation selected by RD",
                    ),
                    ParameterContract(
                        "output_name",
                        True,
                        (str,),
                        meaning="RD-authored name for the derived feature column",
                    ),
                ),
                1,
                metadata={
                    "reusable_derived_dataset": True,
                    "derived_dataset_name": "arithmetic_feature",
                    "scientific_selection": "AI_RESEARCH_DIRECTOR_ONLY",
                    "deterministic_ranking": False,
                },
            ),
        ]
    )


def discovery_analysis_methods() -> tuple[RegisteredAnalysisMethod, ...]:
    return (
        RegisteredAnalysisMethod(DETERMINISTIC_FAMILY_METHOD_ID, deterministic_family_measurements),
        RegisteredAnalysisMethod(ARITHMETIC_METHOD_ID, arithmetic_transform),
    )
