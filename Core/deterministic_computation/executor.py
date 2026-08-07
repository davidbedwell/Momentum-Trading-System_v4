from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import pandas as pd

from .registry import build_registry
from .utils import validate_ohlcv


@dataclass(frozen=True)
class ComputationResult:
    data: pd.DataFrame
    audit: pd.DataFrame


def execute_computations(
    df: pd.DataFrame,
    *,
    families: list[str] | None = None,
    include_reference: bool = False,
    measurement_names: list[str] | None = None,
) -> ComputationResult:
    """Run deterministic families against canonical OHLCV.

    `measurement_names` filters output after family execution; it never changes
    formula semantics. Unknown measurement names fail explicitly.
    """
    validate_ohlcv(df)
    registry = build_registry()

    if families is None:
        selected = [
            k for k, v in registry.items()
            if v.status == "ACTIVE" or include_reference
        ]
    else:
        selected = families

    unknown = sorted(set(selected) - set(registry))
    if unknown:
        raise KeyError(f"Unknown computation families: {unknown}")

    generated_frames: list[pd.DataFrame] = []
    audit_rows: list[dict[str, object]] = []

    for family_id in selected:
        family = registry[family_id]
        if family.status != "ACTIVE" and not include_reference:
            continue

        started = perf_counter()
        generated = family.calculator(df)
        elapsed = perf_counter() - started

        if generated.columns.duplicated().any():
            dupes = generated.columns[generated.columns.duplicated()].tolist()
            raise ValueError(f"{family_id} emitted duplicate columns: {dupes}")

        generated_frames.append(generated)
        audit_rows.append(
            {
                "family_id": family_id,
                "formula_version": family.version,
                "status": "PASSED",
                "measurements_added": len(generated.columns),
                "elapsed_seconds": elapsed,
                "provenance": family.provenance,
            }
        )

    measured = pd.concat([df.copy(), *generated_frames], axis=1)
    if measured.columns.duplicated().any():
        dupes = measured.columns[measured.columns.duplicated()].tolist()
        raise ValueError(f"Cross-family duplicate columns: {dupes}")

    if measurement_names is not None:
        unknown_measurements = sorted(set(measurement_names) - set(measured.columns))
        if unknown_measurements:
            raise KeyError(f"Unknown/unimplemented measurements: {unknown_measurements}")
        base = [c for c in df.columns if c in measured.columns]
        measured = measured.loc[:, base + measurement_names]

    return ComputationResult(measured, pd.DataFrame(audit_rows))
