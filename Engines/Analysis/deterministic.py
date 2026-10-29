from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import pandas as pd

from Core.deterministic_computation import execute_computations

from .canonical import semantic_fingerprint


class DeterministicMeasurementError(RuntimeError):
    """Base error for Analysis deterministic-measurement resolution."""


class DeterministicMeasurementUnavailable(DeterministicMeasurementError):
    """Raised when the shared library cannot materialize a requested measurement."""


@dataclass(frozen=True, slots=True)
class DeterministicMeasurementUse:
    measurement_name: str
    source: str
    computation_id: str | None
    version: str | None
    parameters: Mapping[str, Any]
    input_fingerprint: str
    output_column: str
    audit: tuple[Mapping[str, Any], ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "measurement_name": self.measurement_name,
            "source": self.source,
            "computation_id": self.computation_id,
            "version": self.version,
            "parameters": dict(self.parameters),
            "input_fingerprint": self.input_fingerprint,
            "output_column": self.output_column,
            "audit": [dict(item) for item in self.audit],
        }


@dataclass(frozen=True, slots=True)
class DeterministicResolutionResult:
    records: tuple[Mapping[str, Any], ...]
    uses: tuple[DeterministicMeasurementUse, ...]
    measurements_reused: tuple[str, ...]
    measurements_computed: tuple[str, ...]

    @property
    def available_measurements(self) -> tuple[str, ...]:
        values = set(self.measurements_reused) | set(self.measurements_computed)
        return tuple(sorted(values))


def _audit_records(audit: Any) -> tuple[Mapping[str, Any], ...]:
    if audit is None:
        return ()
    if isinstance(audit, pd.DataFrame):
        records = audit.to_dict(orient="records")
    elif isinstance(audit, Mapping):
        records = [dict(audit)]
    elif isinstance(audit, Sequence) and not isinstance(audit, (str, bytes, bytearray)):
        records = [dict(item) if isinstance(item, Mapping) else {"value": item} for item in audit]
    else:
        records = [{"value": str(audit)}]

    # Runtime timing is operational telemetry, not scientific identity.
    cleaned = []
    for record in records:
        item = dict(record)
        item.pop("elapsed_seconds", None)
        cleaned.append(item)
    return tuple(cleaned)


def _find_audit_identity(
    audit: tuple[Mapping[str, Any], ...],
    measurement_name: str,
) -> tuple[str | None, str | None]:
    for item in audit:
        added = item.get("measurements_added", item.get("measurements_computed", ()))
        if isinstance(added, str):
            added_values = {value.strip() for value in added.replace(",", "|").split("|") if value.strip()}
        elif isinstance(added, Sequence):
            added_values = {str(value) for value in added}
        else:
            added_values = set()
        if measurement_name in added_values:
            computation_id = (
                item.get("family_id")
                or item.get("module_id")
                or item.get("computation_id")
            )
            version = (
                item.get("formula_version")
                or item.get("module_version")
                or item.get("version")
            )
            return (
                str(computation_id) if computation_id is not None else None,
                str(version) if version is not None else None,
            )
    return None, None


class DeterministicMeasurementResolver:
    """Resolve measurement requirements without duplicating computation logic.

    Existing valid materialized columns are reused. Missing governed measurements
    are delegated to Core.deterministic_computation.execute_computations, the same
    shared capability used by Data Intake.
    """

    def resolve(
        self,
        records: Sequence[Mapping[str, Any]],
        *,
        required_measurements: Sequence[str],
        parameters: Mapping[str, Mapping[str, Any]] | None = None,
        input_identity: Mapping[str, Any] | None = None,
    ) -> DeterministicResolutionResult:
        parameters = parameters or {}
        original_records = tuple(dict(row) for row in records)
        frame = pd.DataFrame(original_records)
        input_fingerprint = semantic_fingerprint(
            {
                "input_identity": dict(input_identity or {}),
                "records": original_records,
            }
        )

        reused = []
        missing = []
        for measurement in required_measurements:
            if measurement in frame.columns and frame[measurement].notna().any():
                reused.append(measurement)
            else:
                missing.append(measurement)

        uses: list[DeterministicMeasurementUse] = []
        for measurement in reused:
            uses.append(
                DeterministicMeasurementUse(
                    measurement_name=measurement,
                    source="MATERIALIZED_INPUT",
                    computation_id=None,
                    version=None,
                    parameters=dict(parameters.get(measurement, {})),
                    input_fingerprint=input_fingerprint,
                    output_column=measurement,
                    audit=(),
                )
            )

        if not missing:
            return DeterministicResolutionResult(
                records=original_records,
                uses=tuple(uses),
                measurements_reused=tuple(sorted(reused)),
                measurements_computed=(),
            )

        # Current shared API accepts governed measurement identities as a batch.
        # Parameterized variants remain governed by the library's own definitions;
        # Phase F records requested parameters but does not bypass library authority.
        # Send only canonical OHLCV into the shared computation library.
        # Pre-materialized measurements belong to the Analysis working frame
        # and must not collide with columns emitted by shared computation families.
        canonical_ohlcv = frame[
            ["date", "open", "high", "low", "close", "volume"]
        ].copy()

        result = execute_computations(
            canonical_ohlcv,
            measurement_names=list(missing),
        )
        computed_frame = result.data
        audit = _audit_records(result.audit)

        still_missing = tuple(
            measurement
            for measurement in missing
            if measurement not in computed_frame.columns
        )
        if still_missing:
            raise DeterministicMeasurementUnavailable(
                f"Shared deterministic library did not produce requested measurement(s): "
                f"{still_missing}"
            )

        for measurement in missing:
            computation_id, version = _find_audit_identity(audit, measurement)
            uses.append(
                DeterministicMeasurementUse(
                    measurement_name=measurement,
                    source="SHARED_DETERMINISTIC_LIBRARY",
                    computation_id=computation_id,
                    version=version,
                    parameters=dict(parameters.get(measurement, {})),
                    input_fingerprint=input_fingerprint,
                    output_column=measurement,
                    audit=audit,
                )
            )

        # Merge only the requested missing measurements back into the
        # original Analysis working frame. This preserves already-materialized
        # columns while keeping shared computation semantics authoritative.
        measured = frame.copy()
        for measurement in missing:
            measured[measurement] = computed_frame[measurement]

        # Normalize pandas/NumPy missing values to Python None. NaN != NaN,
        # so leaving warm-up NaNs in dictionaries would make two otherwise
        # identical deterministic executions compare unequal.
        stable_measured = measured.astype(object).where(
            pd.notna(measured),
            None,
        )

        return DeterministicResolutionResult(
            records=tuple(stable_measured.to_dict(orient="records")),
            uses=tuple(sorted(uses, key=lambda item: item.measurement_name)),
            measurements_reused=tuple(sorted(reused)),
            measurements_computed=tuple(sorted(missing)),
        )
