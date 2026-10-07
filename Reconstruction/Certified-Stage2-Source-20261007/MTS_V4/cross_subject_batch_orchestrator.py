from __future__ import annotations

from typing import Mapping

from .batch_orchestrator import BatchResearchLoopOrchestrator
from .contracts import AnalysisResult
from .cross_subject_context import build_cross_subject_context
from .cross_subject_memory import CrossSubjectScientificMemory


class CrossSubjectBatchResearchLoopOrchestrator(BatchResearchLoopOrchestrator):
    """Batched research loop augmented with compact prior-subject scientific memory."""

    def __init__(self, *, scientific_memory: CrossSubjectScientificMemory | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._scientific_memory = scientific_memory

    def _nexus_context(
        self,
        subject_id: str,
        results_by_analysis_id: Mapping[str, AnalysisResult],
    ) -> Mapping[str, object]:
        context = dict(super()._nexus_context(subject_id, results_by_analysis_id))
        context["cross_subject_scientific_memory"] = build_cross_subject_context(
            self._scientific_memory,
            active_subject_id=subject_id,
        )
        return context
