from __future__ import annotations

from dataclasses import dataclass, replace
import json
from numbers import Real
from typing import Any, Mapping, Sequence

from .cache import TemporaryResearchCache
from .contracts import EvidenceDescriptor, SubjectMetadata
from .nexus import InMemoryResearchNexus
from .openai_compatible_provider import OpenAICompatibleResearchDirector


class BlindValidationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class HistoricalEvidenceWindow:
    """Exact RD/human-authored temporal boundary for one evidence source.

    The window is mechanical. It does not choose the prediction date, evidence,
    horizon, or scientific meaning. ``cutoff`` must use the same directly
    comparable representation as the selected evidence column. ``outcome_end``
    is optional and is used only after the prediction has been durably locked.
    """

    evidence_id: str
    time_field: str
    cutoff: Any
    outcome_end: Any | None = None


@dataclass(frozen=True, slots=True)
class BlindValidationAudit:
    trial_id: str
    hypothesis_id: str
    evidence_id: str
    time_field: str
    cutoff: Any
    original_row_count: int
    visible_row_count: int
    withheld_row_count: int


class BlindValidationResearchDirector(OpenAICompatibleResearchDirector):
    """Fresh RD transport for the prediction stage of one blind trial.

    This deliberately does not inherit from the RP-aware production provider.
    Therefore it cannot automatically inject exploratory RP history. The only
    scientific prior supplied here is the already-frozen hypothesis and its
    success definition. A caller should pair this provider with the isolated
    Nexus and masked evidence/cache produced by HistoricalBlindValidationSession.
    """

    def __init__(
        self,
        *,
        trial_id: str,
        hypothesis_id: str,
        hypothesis_statement: str,
        success_definition: str,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int = 180,
    ) -> None:
        super().__init__(
            base_url=base_url,
            model=model,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        self._blind_trial_id = trial_id
        self._blind_hypothesis_id = hypothesis_id
        self._blind_hypothesis_statement = hypothesis_statement
        self._blind_success_definition = success_definition

    def _decision_messages(
        self,
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
        user = json.loads(messages[1]["content"])
        user["blind_validation"] = {
            "trial_id": self._blind_trial_id,
            "hypothesis_id": self._blind_hypothesis_id,
            "frozen_hypothesis_statement": self._blind_hypothesis_statement,
            "frozen_success_definition": self._blind_success_definition,
            "prediction_stage": True,
            "future_outcomes_available": False,
            "exploratory_rp_history_available": False,
        }
        user["instructions"].extend(
            [
                "This is a historical blind-validation prediction stage. Treat the supplied evidence as ending at the declared historical cutoff; no later outcome information is available to you.",
                "Evaluate only the frozen predictive hypothesis supplied in blind_validation. Do not revise that hypothesis or its success definition during this trial.",
                "When you judge the available pre-cutoff evidence sufficient to make the trial prediction, preserve the exact prediction under research_state.blind_prediction with trial_id, hypothesis_id, and prediction_statement before requesting any outcome evaluation.",
                "Exploratory RP/Nexus scientific memory is intentionally absent so prior look-ahead discoveries cannot disclose the hidden outcome for this historical trial.",
            ]
        )
        system = messages[0]["content"] + (
            " You are currently operating inside a historical blind-validation prediction sandbox. "
            "Only pre-cutoff evidence is available. The frozen hypothesis may be evaluated but not revised, "
            "and hidden post-cutoff outcomes must not be inferred from absent exploratory memory."
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


@dataclass(slots=True)
class HistoricalBlindValidationSession:
    """Mechanically isolated historical prediction view.

    During the prediction stage every supplied evidence payload is copied into a
    fresh temporary cache after rows later than the declared cutoff are removed.
    The returned evidence descriptors expose the masked row count and cutoff, not
    the original future coverage or source provenance. A fresh in-memory Nexus is
    supplied so prior exploratory findings/results are not transported into the
    blind run.

    Outcome rows cannot be revealed through this object until a prediction has
    been explicitly locked. The prediction text is immutable once locked.
    """

    trial_id: str
    hypothesis_id: str
    subject: SubjectMetadata
    evidence: tuple[EvidenceDescriptor, ...]
    cache: TemporaryResearchCache
    nexus: InMemoryResearchNexus
    audits: tuple[BlindValidationAudit, ...]
    _windows: Mapping[str, HistoricalEvidenceWindow]
    _source_payloads: Mapping[str, tuple[Mapping[str, Any], ...]]
    _prediction_statement: str | None = None

    @classmethod
    def build(
        cls,
        *,
        trial_id: str,
        hypothesis_id: str,
        subject: SubjectMetadata,
        evidence: Sequence[EvidenceDescriptor],
        source_cache: TemporaryResearchCache,
        windows: Sequence[HistoricalEvidenceWindow],
    ) -> "HistoricalBlindValidationSession":
        if not trial_id.strip():
            raise BlindValidationError("trial_id cannot be blank")
        if not hypothesis_id.strip():
            raise BlindValidationError("hypothesis_id cannot be blank")

        window_items = tuple(windows)
        window_map = {item.evidence_id: item for item in window_items}
        if len(window_map) != len(window_items):
            raise BlindValidationError("duplicate historical validation evidence window")

        supplied_ids = {item.evidence_id for item in evidence}
        if set(window_map) != supplied_ids:
            missing = sorted(supplied_ids - set(window_map))
            extra = sorted(set(window_map) - supplied_ids)
            raise BlindValidationError(
                f"blind validation requires exactly one window per supplied evidence; missing={missing} extra={extra}"
            )

        blind_cache = TemporaryResearchCache()
        blind_evidence: list[EvidenceDescriptor] = []
        audits: list[BlindValidationAudit] = []
        source_payloads: dict[str, tuple[Mapping[str, Any], ...]] = {}

        for descriptor in evidence:
            if descriptor.subject_id != subject.subject_id:
                raise BlindValidationError(
                    f"evidence {descriptor.evidence_id} does not belong to {subject.subject_id}"
                )
            window = window_map[descriptor.evidence_id]
            if not window.time_field.strip():
                raise BlindValidationError(
                    f"time_field cannot be blank for {descriptor.evidence_id}"
                )
            if window.time_field not in descriptor.schema:
                raise BlindValidationError(
                    f"time_field {window.time_field!r} is not in schema for {descriptor.evidence_id}"
                )

            raw_payload = source_cache.get(descriptor.cache_key)
            try:
                rows = tuple(raw_payload)
            except TypeError as exc:
                raise BlindValidationError(
                    f"evidence payload is not row-iterable: {descriptor.evidence_id}"
                ) from exc
            if not all(isinstance(row, Mapping) for row in rows):
                raise BlindValidationError(
                    f"evidence payload contains non-mapping row: {descriptor.evidence_id}"
                )
            typed_rows = tuple(dict(row) for row in rows)
            source_payloads[descriptor.evidence_id] = typed_rows

            visible: list[Mapping[str, Any]] = []
            for row in typed_rows:
                if window.time_field not in row:
                    raise BlindValidationError(
                        f"row missing time_field {window.time_field!r}: {descriptor.evidence_id}"
                    )
                if _less_than_or_equal(row[window.time_field], window.cutoff):
                    visible.append(row)

            blind_cache_key = f"blind-validation:{trial_id}:{descriptor.evidence_id}"
            blind_cache.put(blind_cache_key, tuple(visible))
            blind_evidence.append(
                replace(
                    descriptor,
                    cache_key=blind_cache_key,
                    coverage_end=str(window.cutoff),
                    row_count=len(visible),
                    provenance={
                        "blind_validation": {
                            "trial_id": trial_id,
                            "hypothesis_id": hypothesis_id,
                            "time_field": window.time_field,
                            "inclusive_cutoff": window.cutoff,
                            "future_rows_withheld": True,
                            "source_provenance_withheld_during_prediction": True,
                            "mechanical_only": True,
                        }
                    },
                    content_identity=None,
                )
            )
            audits.append(
                BlindValidationAudit(
                    trial_id=trial_id,
                    hypothesis_id=hypothesis_id,
                    evidence_id=descriptor.evidence_id,
                    time_field=window.time_field,
                    cutoff=window.cutoff,
                    original_row_count=len(typed_rows),
                    visible_row_count=len(visible),
                    withheld_row_count=len(typed_rows) - len(visible),
                )
            )

        isolated_nexus = InMemoryResearchNexus()
        isolated_nexus.upsert_subject(subject)
        for descriptor in blind_evidence:
            isolated_nexus.upsert_evidence_metadata(descriptor.durable_metadata())

        return cls(
            trial_id=trial_id,
            hypothesis_id=hypothesis_id,
            subject=subject,
            evidence=tuple(blind_evidence),
            cache=blind_cache,
            nexus=isolated_nexus,
            audits=tuple(audits),
            _windows=window_map,
            _source_payloads=source_payloads,
        )

    @property
    def prediction_locked(self) -> bool:
        return self._prediction_statement is not None

    @property
    def prediction_statement(self) -> str | None:
        return self._prediction_statement

    def lock_prediction(self, prediction_statement: str) -> None:
        if not prediction_statement.strip():
            raise BlindValidationError("prediction_statement cannot be blank")
        if self._prediction_statement is not None:
            if self._prediction_statement == prediction_statement:
                return
            raise BlindValidationError(
                "blind validation prediction is already locked and cannot be revised"
            )
        self._prediction_statement = prediction_statement

    def reveal_outcomes(self) -> Mapping[str, tuple[Mapping[str, Any], ...]]:
        """Return only post-cutoff rows after prediction lock.

        This is the scoring stage. It intentionally may expose future data, but
        only after the prediction is immutable. Rows at or before the cutoff are
        not returned again.
        """

        if self._prediction_statement is None:
            raise BlindValidationError(
                "cannot reveal historical outcomes before the prediction is locked"
            )
        revealed: dict[str, tuple[Mapping[str, Any], ...]] = {}
        for evidence_id, rows in self._source_payloads.items():
            window = self._windows[evidence_id]
            outcome_rows = []
            for row in rows:
                value = row[window.time_field]
                if not _greater_than(value, window.cutoff):
                    continue
                if window.outcome_end is not None and not _less_than_or_equal(
                    value, window.outcome_end
                ):
                    continue
                outcome_rows.append(row)
            revealed[evidence_id] = tuple(outcome_rows)
        return revealed

    def blind_context(self, *, hypothesis_statement: str, success_definition: str) -> Mapping[str, Any]:
        """Minimal scientific memory safe to hand to a fresh blind RD call."""

        return {
            "blind_validation": True,
            "trial_id": self.trial_id,
            "hypothesis_id": self.hypothesis_id,
            "frozen_hypothesis": {
                "statement": hypothesis_statement,
                "success_definition": success_definition,
            },
            "prediction_locked": self.prediction_locked,
            "lookahead_policy": (
                "PREDICTION_STAGE_CONTAINS_ONLY_ROWS_AT_OR_BEFORE_DECLARED_CUTOFFS; "
                "OUTCOME_ROWS_ARE_UNAVAILABLE_UNTIL_PREDICTION_LOCK"
            ),
            "exploratory_rp_or_nexus_memory_included": False,
        }


def _less_than_or_equal(value: Any, cutoff: Any) -> bool:
    if _is_number(value) and _is_number(cutoff):
        return float(value) <= float(cutoff)
    if isinstance(value, str) and isinstance(cutoff, str):
        return value <= cutoff
    raise BlindValidationError(
        "historical validation time values and cutoffs must be directly comparable "
        f"as both numeric or both strings; got {type(value).__name__} and {type(cutoff).__name__}"
    )


def _greater_than(value: Any, cutoff: Any) -> bool:
    if _is_number(value) and _is_number(cutoff):
        return float(value) > float(cutoff)
    if isinstance(value, str) and isinstance(cutoff, str):
        return value > cutoff
    raise BlindValidationError(
        "historical validation time values and cutoffs must be directly comparable "
        f"as both numeric or both strings; got {type(value).__name__} and {type(cutoff).__name__}"
    )


def _is_number(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)
