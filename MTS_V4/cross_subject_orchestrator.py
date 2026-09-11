from __future__ import annotations

from typing import Mapping

from .contracts import AnalysisResult
from .cross_subject_context import build_cross_subject_context
from .cross_subject_memory import CrossSubjectScientificMemory
from .orchestrator import ResearchLoopOrchestrator


class CrossSubjectResearchLoopOrchestrator(ResearchLoopOrchestrator):
    """Research loop that augments normal subject-local RD context with prior-subject science."""

    def __init__(self, *, scientific_memory: CrossSubjectScientificMemory | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._scientific_memory = scientific_memory

    def _nexus_context(
        self,
        subject_id: str,
        analysis_results: Mapping[str, AnalysisResult] | None = None,
    ) -> Mapping[str, object]:
        context = dict(super()._nexus_context(subject_id, analysis_results))
        context["cross_subject_scientific_memory"] = build_cross_subject_context(
            self._scientific_memory,
            active_subject_id=subject_id,
        )
        return context
