from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from .adaptive_batch import SubjectRunLedger, ThreeSubjectBatchController
from .batch_synthesis import BatchScientificSynthesis, SolBatchScientificSynthesizer
from .subject_memory_digest import SolSubjectScientificMemoryAuthor, SubjectScientificDigest
from .subject_selection import RDSubjectSelectionDecision, SolAdaptiveSubjectSelector
from .validation_first import SubjectResearchPhase, ValidationFirstSubjectGate


@dataclass(frozen=True, slots=True)
class CompletedSubjectRun:
    ledger: SubjectRunLedger
    scientific_context: Mapping[str, object]


RunExploration = Callable[[RDSubjectSelectionDecision], CompletedSubjectRun]
RunBlindValidation = Callable[[RDSubjectSelectionDecision, ValidationFirstSubjectGate], None]
AvailableSources = Callable[[str], Sequence[str]]


@dataclass(frozen=True, slots=True)
class AdaptiveBatchResult:
    selections: tuple[RDSubjectSelectionDecision, ...]
    subject_digests: tuple[SubjectScientificDigest, ...]
    synthesis: BatchScientificSynthesis


class SolAdaptiveThreeSubjectProgram:
    """Coordinate one approved autonomous batch without choosing science in code.

    Sol chooses each subject and whether it should begin with blind validation.
    The controller enforces objective eligibility, uniqueness, the three-subject
    limit, and validation-first ordering. After each subject completes, Sol authors
    compact cross-subject scientific memory before the next selection is made.
    """

    def __init__(
        self,
        *,
        mission: str,
        selector: SolAdaptiveSubjectSelector,
        controller: ThreeSubjectBatchController,
        synthesizer: SolBatchScientificSynthesizer,
        memory_author: SolSubjectScientificMemoryAuthor,
        run_exploration: RunExploration,
        run_blind_validation: RunBlindValidation,
        available_sources: AvailableSources | None = None,
    ) -> None:
        self._mission = mission
        self._selector = selector
        self._controller = controller
        self._synthesizer = synthesizer
        self._memory_author = memory_author
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
        digests: list[SubjectScientificDigest] = []

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
                if gate.phase is not SubjectResearchPhase.VALIDATION_SCORED:
                    raise RuntimeError(
                        "blind-validation callback returned before the validation outcome was scored"
                    )
                gate.release_to_exploration()

            completed = self._run_exploration(selection)
            row = completed.ledger
            if row.subject_id != selection.subject_id:
                raise RuntimeError("exploration ledger subject does not match accepted selection")
            self._controller.record_run(row)

            digest = self._memory_author.author_and_persist(
                mission=self._mission,
                subject_id=selection.subject_id,
                subject_scientific_context=completed.scientific_context,
            )
            digests.append(digest)
            seen.append(selection.subject_id)

        ledger = self._controller.ledger()
        synthesis = self._synthesizer.synthesize(mission=self._mission, ledger=ledger)
        return AdaptiveBatchResult(
            selections=tuple(selections),
            subject_digests=tuple(digests),
            synthesis=synthesis,
        )
