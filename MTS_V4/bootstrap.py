from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .analysis import ExactMethodAnalysisExecutor
from .cache import TemporaryResearchCache
from .concept_library import ResearchConceptLibrary, seed_market_concepts
from .cross_evidence import cross_evidence_analysis_method, cross_evidence_method_spec
from .cross_subject_memory import CrossSubjectScientificMemory
from .cross_subject_orchestrator import CrossSubjectResearchLoopOrchestrator
from .discovery_methods import discovery_analysis_methods, discovery_method_catalog
from .execution_interface import TransparentInputBindingValidator
from .group_aggregation import group_aggregation_analysis_method, group_aggregation_method_spec
from .interfaces import ResearchDirectorProvider
from .method_catalog import MethodCatalog
from .nexus import InMemoryResearchNexus, ResearchNexus
from .nexus_json import JsonResearchNexus
from .orchestrator import ResearchLoopOrchestrator
from .scientific_toolkit import scientific_toolkit_analysis_method, scientific_toolkit_method_spec
from .standard_methods import standard_analysis_methods, standard_method_catalog


DEFAULT_MISSION = (
    "Discover reproducible relationships between market information observable at time T and "
    "subsequent market behavior at T+1 onward, with sufficient predictive value in direction, "
    "magnitude, timing, continuation or reversal, and path quality to be practically exploitable "
    "as trades. During EXPLORATION, actively seek scientifically defensible prospective structure "
    "and use historical look-ahead when useful for discovery. Retrospective historical blind "
    "verification should use a ticker/subject that MTS had not previously analyzed before that "
    "verification campaign. Genuine live prospective prediction and trading remain allowed on "
    "previously analyzed tickers because their future outcomes have not yet occurred. During any "
    "blind prediction, evaluate frozen predictive hypotheses without look-ahead knowledge at the "
    "prediction point."
)


@dataclass(frozen=True, slots=True)
class V4Runtime:
    mission: str
    cache: TemporaryResearchCache
    nexus: ResearchNexus
    catalog: MethodCatalog
    concepts: ResearchConceptLibrary
    validator: TransparentInputBindingValidator
    analysis: ExactMethodAnalysisExecutor
    orchestrator: ResearchLoopOrchestrator


def build_runtime(
    *,
    rd: ResearchDirectorProvider,
    mission: str = DEFAULT_MISSION,
    nexus_path: str | Path | None = None,
    concept_library: ResearchConceptLibrary | None = None,
    max_contract_repairs: int = 3,
    scientific_memory: CrossSubjectScientificMemory | None = None,
) -> V4Runtime:
    """Assemble the v4 research runtime without external credentials or data.

    Provider creation is intentionally outside this function. The caller may use
    a fake AI for proofs or an approved live provider at integration time.

    Human market concepts are supplied as non-authoritative idea seeds. RD may
    test, reject, reformulate, combine, or extend them; deterministic runtime
    components never treat concept presence as scientific evidence.

    When compact cross-subject scientific memory is supplied, the same runtime
    components are used but RD context is augmented through
    CrossSubjectResearchLoopOrchestrator. Subject-local Nexus behavior and the
    raw-data retention boundary remain unchanged.
    """
    cache = TemporaryResearchCache()
    nexus: ResearchNexus
    if nexus_path is None:
        nexus = InMemoryResearchNexus()
    else:
        nexus = JsonResearchNexus(nexus_path)

    catalog = standard_method_catalog()
    for spec in discovery_method_catalog().all():
        catalog.register(spec)
    catalog.register(cross_evidence_method_spec())
    catalog.register(scientific_toolkit_method_spec())
    catalog.register(group_aggregation_method_spec())
    concepts = concept_library or seed_market_concepts()
    validator = TransparentInputBindingValidator(catalog)
    analysis = ExactMethodAnalysisExecutor()
    for method in standard_analysis_methods():
        analysis.register(method)
    for method in discovery_analysis_methods():
        analysis.register(method)
    analysis.register(cross_evidence_analysis_method())
    analysis.register(scientific_toolkit_analysis_method())
    analysis.register(group_aggregation_analysis_method())

    orchestrator_type = (
        CrossSubjectResearchLoopOrchestrator
        if scientific_memory is not None
        else ResearchLoopOrchestrator
    )
    orchestrator_kwargs = {
        "mission": mission,
        "rd": rd,
        "validator": validator,
        "analysis": analysis,
        "nexus": nexus,
        "cache": cache,
        "available_methods": catalog.capability_payloads(),
        "research_concepts": concepts.payloads(),
        "max_contract_repairs": max_contract_repairs,
    }
    if scientific_memory is not None:
        orchestrator_kwargs["scientific_memory"] = scientific_memory
    orchestrator = orchestrator_type(**orchestrator_kwargs)

    return V4Runtime(
        mission=mission,
        cache=cache,
        nexus=nexus,
        catalog=catalog,
        concepts=concepts,
        validator=validator,
        analysis=analysis,
        orchestrator=orchestrator,
    )
