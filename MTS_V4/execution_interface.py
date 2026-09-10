from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Sequence

from .contracts import AnalysisRequest, AnalysisResult, ContractDefect, EvidenceDescriptor
from .research_package_provider import ResearchPackageAwareResearchDirector
from .validation import ObjectiveContractValidator


class TransparentExecutionResearchDirector(ResearchPackageAwareResearchDirector):
    """Expose literal Analysis input-binding mechanics to the AI Research Director.

    This layer does not recommend scientific methods, choose evidence, create aliases,
    or repair scientific requests. It only makes the actual execution namespace visible
    so the RD does not have to reverse-engineer bespoke plumbing by trial and error.
    """

    @classmethod
    def _decision_messages(
        cls,
        *,
        operation: str,
        mission: str,
        payload: Mapping[str, object],
    ) -> list[Mapping[str, str]]:
        messages = super()._decision_messages(
            operation=operation,
            mission=mission,
            payload=payload,
        )

        system = messages[0]["content"] + (
            " Analysis input binding is literal: every acquired evidence payload is available to "
            "Analysis under its exact evidence_id string; every prior derived payload referenced in "
            "analysis_inputs is available under that item's exact input_name; no other implicit or "
            "friendly aliases exist."
        )

        user = json.loads(messages[1]["content"])
        user["instructions"].extend(
            [
                "Literal Analysis input namespace: each request.evidence_ids value becomes an available input key equal to that exact evidence_id string. Each request.analysis_inputs item becomes an available input key equal to its exact input_name. No other input aliases exist.",
                "For analysis.dataset.compose, every alignment[].input_name must exactly equal an available input key, and every selections[].input_name must exactly name one of the alignment inputs. Acquired evidence therefore uses the full evidence_id as input_name; labels such as 'ohlcv' or 'options_flow' are invalid unless they are actual analysis_inputs input_name values.",
                "analysis.dataset.compose COLUMN alignment requires a unique key value within each aligned input and performs no aggregation of duplicate keys. If duplicate keys require aggregation, select an available method or scientific approach yourself; deterministic code will not choose one for you.",
            ]
        )

        return [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps(
                    user,
                    sort_keys=True,
                    default=str,
                    separators=(",", ":"),
                ),
            },
        ]


class TransparentInputBindingValidator(ObjectiveContractValidator):
    """Reject impossible literal input bindings before spending an Analysis execution.

    The validator only checks names against payloads the RD explicitly supplied in the
    request. It never chooses a dataset, alias, column, method, or scientific repair.
    """

    def validate(
        self,
        request: AnalysisRequest,
        evidence: Mapping[str, EvidenceDescriptor],
        analysis_results: Mapping[str, AnalysisResult] | None = None,
    ) -> tuple[ContractDefect, ...]:
        defects = list(super().validate(request, evidence, analysis_results))
        if request.method_id != "analysis.dataset.compose":
            return tuple(defects)

        available_bindings = tuple(
            dict.fromkeys(
                [*request.evidence_ids, *(item.input_name for item in request.analysis_inputs)]
            )
        )
        alignment = request.parameters.get("alignment")
        aligned_names: list[str] = []

        if isinstance(alignment, (list, tuple)):
            for index, spec in enumerate(alignment):
                if not isinstance(spec, Mapping):
                    continue
                input_name = str(spec.get("input_name", "")).strip()
                if not input_name:
                    continue
                aligned_names.append(input_name)
                if input_name not in available_bindings:
                    defects.append(
                        ContractDefect(
                            code="INVALID_INPUT_BINDING",
                            message=(
                                "analysis.dataset.compose alignment input_name is not supplied by the "
                                f"request: {input_name!r}. Exact available input keys are "
                                f"{available_bindings}. Acquired evidence is bound under its exact "
                                "evidence_id; prior derived data is bound under the exact "
                                "analysis_inputs.input_name authored by RD."
                            ),
                            field=f"alignment[{index}].input_name",
                            method_id=request.method_id,
                        )
                    )

        selections = request.parameters.get("selections")
        if isinstance(selections, (list, tuple)):
            aligned_set = set(aligned_names)
            for index, spec in enumerate(selections):
                if not isinstance(spec, Mapping):
                    continue
                input_name = str(spec.get("input_name", "")).strip()
                if not input_name:
                    continue
                if input_name not in aligned_set:
                    defects.append(
                        ContractDefect(
                            code="INVALID_INPUT_BINDING",
                            message=(
                                "analysis.dataset.compose selection input_name is not present in "
                                f"alignment: {input_name!r}. Exact aligned input names are "
                                f"{tuple(aligned_names)}."
                            ),
                            field=f"selections[{index}].input_name",
                            method_id=request.method_id,
                        )
                    )

        return tuple(defects)
