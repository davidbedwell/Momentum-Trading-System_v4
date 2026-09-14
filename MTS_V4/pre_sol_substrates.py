from __future__ import annotations

from typing import Mapping, Sequence

from .contracts import AnalysisResult, EvidenceDescriptor, SubjectMetadata
from .intraday_analysis_substrate import build_for_subject as build_intraday
from .neutral_analysis_substrate import build_for_subject as build_daily
from .share_structure_analysis import build_for_subject as build_sec


def build_for_subject(
    *,
    subject: SubjectMetadata,
    evidence: Sequence[EvidenceDescriptor],
    cache,
    analysis,
) -> Mapping[str, AnalysisResult]:
    """Build all human-authorized neutral substrates before the first RD call.

    Composition is deterministic infrastructure only. Each component retains its
    own scientific-authority and temporal-information boundaries.
    """
    results: dict[str, AnalysisResult] = {}
    results.update(build_daily(subject=subject, evidence=evidence, cache=cache, analysis=analysis))
    results.update(build_sec(subject=subject, evidence=evidence, cache=cache, analysis=analysis))
    results.update(build_intraday(subject=subject, evidence=evidence, cache=cache, analysis=analysis))
    return results
