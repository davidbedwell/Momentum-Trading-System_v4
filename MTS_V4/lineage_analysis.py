from __future__ import annotations

from typing import Any, Mapping

from .analysis import ExactMethodAnalysisExecutor
from .contracts import AnalysisRequest


class LineageAwareExactMethodAnalysisExecutor(ExactMethodAnalysisExecutor):
    """Extend objective alignment guards with mechanically provable row identity.

    The base executor intentionally refuses to equate unlike coordinate spaces.
    This subclass adds only provenance that is uniquely implied by deterministic
    execution: one-to-one row-preserving measurements and compose keys whose
    aligned inputs all prove the same parent identity. It never chooses a join,
    key, column, threshold, or other scientific representation for the RD.
    """

    @classmethod
    def _row_position_parent_identity(cls, payload: object) -> str | None:
        if not isinstance(payload, (list, tuple)) or not payload:
            return None
        parent_input: str | None = None
        for row_index, row in enumerate(payload):
            if not isinstance(row, Mapping):
                return None
            lineage = row.get("__observation_lineage")
            if not isinstance(lineage, Mapping):
                return None
            current_parent = str(lineage.get("input_name", "")).strip()
            if not current_parent or lineage.get("input_row_anchor") != row_index:
                return None
            if parent_input is None:
                parent_input = current_parent
            elif parent_input != current_parent:
                return None
        return parent_input

    @classmethod
    def _alignment_identity(
        cls,
        *,
        input_name: str,
        key: Mapping[str, Any],
        evidence_payloads: Mapping[str, object],
    ) -> tuple[str, str | None, str | None]:
        mode = str(key.get("mode", "")).upper()
        column: str | None = None
        identity: str | None = None
        payload = evidence_payloads.get(input_name)
        if mode == "ROW_POSITION":
            identity = cls._row_position_parent_identity(payload)
            if identity is None:
                identity = input_name
        elif mode == "COLUMN":
            column = str(key.get("column", "")).strip()
            if column and payload is not None:
                identity = cls._parent_row_position_identity(payload, column)
        return mode, column, identity

    @classmethod
    def _validate_alignment_identity_spaces(
        cls,
        request: AnalysisRequest,
        evidence_payloads: Mapping[str, object],
    ) -> None:
        if request.method_id != "analysis.dataset.compose":
            return
        alignment = request.parameters.get("alignment")
        if not isinstance(alignment, (list, tuple)):
            return

        normalized: list[tuple[str, str, str | None, str | None]] = []
        for spec in alignment:
            if not isinstance(spec, Mapping):
                continue
            input_name = str(spec.get("input_name", "")).strip()
            key = spec.get("key")
            if not input_name or not isinstance(key, Mapping):
                continue
            mode, column, identity = cls._alignment_identity(
                input_name=input_name,
                key=key,
                evidence_payloads=evidence_payloads,
            )
            normalized.append((input_name, mode, column, identity))

        # A proven COLUMN parent identity is the objective reference space. Once
        # one exists, every other aligned input must mechanically prove that same
        # space (or be the direct ROW_POSITION source itself). Unknown identity is
        # not silently repaired.
        proven = [
            item for item in normalized if item[1] == "COLUMN" and item[3] is not None
        ]
        for input_name, mode, column, identity in proven:
            assert identity is not None
            for other_name, other_mode, other_column, other_identity in normalized:
                if other_name == input_name:
                    continue
                if other_identity == identity:
                    continue
                other_key = (
                    "ROW_POSITION"
                    if other_mode == "ROW_POSITION"
                    else f"COLUMN {other_column!r}"
                )
                raise ValueError(
                    "alignment identity-space defect: "
                    f"input {input_name!r} COLUMN {column!r} is mechanically "
                    f"parent-row-position identity for {identity!r}, but input "
                    f"{other_name!r} {other_key} is not mechanically proven to use "
                    "that same identity space"
                )

    @classmethod
    def _attach_observation_lineage(
        cls,
        request: AnalysisRequest,
        outputs: dict[str, Any],
        evidence_payloads: Mapping[str, object],
    ) -> dict[str, Any]:
        outputs = super()._attach_observation_lineage(
            request,
            outputs,
            evidence_payloads,
        )

        if request.method_id == "analysis.measurements.deterministic_family":
            return cls._attach_row_preserving_measurement_lineage(outputs, evidence_payloads)
        if request.method_id == "analysis.dataset.compose":
            return cls._attach_compose_key_lineage(request, outputs, evidence_payloads)
        return outputs

    @classmethod
    def _attach_row_preserving_measurement_lineage(
        cls,
        outputs: dict[str, Any],
        evidence_payloads: Mapping[str, object],
    ) -> dict[str, Any]:
        if len(evidence_payloads) != 1:
            return outputs
        derived = outputs.get("derived_datasets")
        if not isinstance(derived, Mapping):
            return outputs
        rows = derived.get("deterministic_measurements")
        if not isinstance(rows, (list, tuple)):
            return outputs
        source_payload = next(iter(evidence_payloads.values()))
        if not isinstance(source_payload, (list, tuple)) or len(rows) != len(source_payload):
            return outputs

        input_name = next(iter(evidence_payloads))
        enriched_rows: list[Mapping[str, Any]] = []
        for row_index, raw_row in enumerate(rows):
            if not isinstance(raw_row, Mapping):
                return outputs
            row = dict(raw_row)
            row["__observation_lineage"] = {
                "input_name": input_name,
                "input_row_start": row_index,
                "input_row_end": row_index,
                "input_row_anchor": row_index,
                "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
            }
            enriched_rows.append(row)

        derived_copy = dict(derived)
        derived_copy["deterministic_measurements"] = enriched_rows
        outputs["derived_datasets"] = derived_copy
        cls._mark_catalog_lineage(outputs, "deterministic_measurements")
        return outputs

    @classmethod
    def _attach_compose_key_lineage(
        cls,
        request: AnalysisRequest,
        outputs: dict[str, Any],
        evidence_payloads: Mapping[str, object],
    ) -> dict[str, Any]:
        alignment = request.parameters.get("alignment")
        if not isinstance(alignment, (list, tuple)) or not alignment:
            return outputs

        identities: list[str] = []
        for spec in alignment:
            if not isinstance(spec, Mapping):
                return outputs
            input_name = str(spec.get("input_name", "")).strip()
            key = spec.get("key")
            if not input_name or not isinstance(key, Mapping):
                return outputs
            _, _, identity = cls._alignment_identity(
                input_name=input_name,
                key=key,
                evidence_payloads=evidence_payloads,
            )
            if identity is None:
                return outputs
            identities.append(identity)
        if len(set(identities)) != 1:
            return outputs

        key_column = outputs.get("alignment_key_column")
        derived = outputs.get("derived_datasets")
        if not isinstance(key_column, str) or not isinstance(derived, Mapping):
            return outputs
        rows = derived.get("composed_dataset")
        if not isinstance(rows, (list, tuple)):
            return outputs

        identity = identities[0]
        enriched_rows: list[Mapping[str, Any]] = []
        for raw_row in rows:
            if not isinstance(raw_row, Mapping) or key_column not in raw_row:
                return outputs
            logical_key = raw_row[key_column]
            row = dict(raw_row)
            row["__observation_lineage"] = {
                "input_name": identity,
                "input_row_start": logical_key,
                "input_row_end": logical_key,
                "input_row_anchor": logical_key,
                "semantics": "MECHANICALLY_PROVEN_COMMON_ALIGNMENT_IDENTITY_NOT_SCIENTIFIC_INTERPRETATION",
            }
            enriched_rows.append(row)

        derived_copy = dict(derived)
        derived_copy["composed_dataset"] = enriched_rows
        outputs["derived_datasets"] = derived_copy
        cls._mark_catalog_lineage(outputs, "composed_dataset")
        return outputs

    @staticmethod
    def _mark_catalog_lineage(outputs: dict[str, Any], dataset_name: str) -> None:
        catalog = outputs.get("derived_dataset_catalog")
        if not isinstance(catalog, Mapping):
            return
        entry = catalog.get(dataset_name)
        if not isinstance(entry, Mapping):
            return
        catalog_copy = dict(catalog)
        entry_copy = dict(entry)
        entry_copy["observation_lineage"] = {
            "stored_in_rows_as": "__observation_lineage",
            "scientific_schema_unchanged": True,
            "meaning": "Mechanically proven row/alignment identity provenance; no scientific join or variable was inferred.",
        }
        catalog_copy[dataset_name] = entry_copy
        outputs["derived_dataset_catalog"] = catalog_copy
