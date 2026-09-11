from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from .adaptive_batch import SubjectRunLedger, ThreeSubjectBatchController
from .batch_synthesis import BatchScientificSynthesis, SolBatchScientificSynthesizer
from .subject_selection import RDSubjectSelectionDecision, SolAdaptiveSubjectSelector
from .validation_first import ValidationFirstSubjectGate


RunExploration = Callable[[RDSubjectSelectionDecision], SubjectRunLedger]
RunBlindValidation = Callable[[RDSubjectSelectionDecision, ValidationFirstSubjectGate], None]
AvailableSources = Callable[[str], Sequence[str]]


@dataclass(frozen=True, slots=True)
class AdaptiveBatchResult:
    selections: tuple[RDSubjectSelectionDecision, ...]
    synthesis: BatchScientificSynthesis


class SolAdaptiveThreeSubjectProgram:
    """Coordinate one approved autonomous batch without choosing science in code.

    Sol chooses each subject and whether it should begin with blind validation.
    The controller enforces objective eligibility, uniqueness, the three-subject
    limit, and validation-first ordering. Callbacks perform the actual subject
    validation/exploration campaign using the production Intake/Analysis/RD path.
    """

    def __init__(
        self,
        *,
        mission: str,
        selector: SolAdaptiveSubjectSelector,
        controller: ThreeSubjectBatchController,
        synthesizer: SolBatchScientificSynthesizer,
        run_exploration: RunExploration,
        run_blind_validation: RunBlindValidation,
        available_sources: AvailableSources | None = None,
    ) -> None:
        self._mission = mission
        self._selector = selector
        self._controller = controller
        self._synthesizer = synthesizer
        self._run_exploration = run_exploration
        self._run_blind_validation = run_blind_validation
        self._available_sources = available_sources or (lambda _subject_id: ())

    def run_batch(
        self,
        *,
        candidate_subject_ids: Sequence[str],
        previously_seen: Sequence[str] = (),
    ) -> AdaptiveBatchResult:
        seen = list(previously_seen)
        selections: list[RDSubjectSelectionDecision] = []

        while not self._controller.requires_review:
            available_map: Mapping[str, Sequence[str]] = {
                subject_id: tuple(self._available_sources(subject_id))
                for subject_id in candidate_subject_ids
            }
            selection = self._selector.choose_next(
                mission=self._mission,
                previously_seen=tuple(seen),
                candidate_subject_ids=candidate_subject_ids,
                available_sources_by_subject=available_map,
            )
            defects = self._controller.validate_selection(
                subject_id=selection.subject_id,
                rationale=selection.rationale,
                previously_seen=tuple(seen),
                available_sources=available_map.get(selection.subject_id, ()),
            )
            if defects:
                raise RuntimeError("RD subject selection failed objective validation: " + "; ".join(defects))

            self._controller.accept_selection(
                subject_id=selection.subject_id,
                rationale=selection.rationale,
            )
            selections.append(selection)

            if selection.mode == "VALIDATION_FIRST":
                gate = ValidationFirstSubjectGate(
                    subject_id=selection.subject_id,
                    hypothesis_id=selection.hypothesis_id or "",
                )
                self._run_blind_validation(selection, gate)
                if gate.phase.value != "VALIDATION_SCORED":
                    raise RuntimeError(
                        "blind-validation callback returned before the validation outcome was scored"
                    )
                gate.release_to_exploration()

            row = self._run_exploration(selection)
            if row.subject_id != selection.subject_id:
                raise RuntimeError("exploration ledger subject does not match accepted selection")
            self._controller.record_run(row)
            seen.append(selection.subject_id)

        ledger = self._controller.ledger()
        synthesis = self._synthesizer.synthesize(mission=self._mission, ledger=ledger)
        return AdaptiveBatchResult(selections=tuple(selections), synthesis=synthesis)
