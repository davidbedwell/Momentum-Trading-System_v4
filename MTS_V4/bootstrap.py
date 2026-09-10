from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .analysis import ExactMethodAnalysisExecutor
from .cache import TemporaryResearchCache
from .concept_library import ResearchConceptLibrary, seed_market_concepts
from .cross_evidence import cross_evidence_analysis_method, cross_evidence_method_spec
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
) -> V4Runtime:
    """Assemble the v4 research runtime without external credentials or data.

    Provider creation is intentionally outside this function. The caller may use
    a fake AI for proofs or an approved live provider at integration time.

    Human market concepts are supplied as non-authoritative idea seeds. RD may
    test, reject, reformulate, combine, or extend them; deterministic runtime
    components never treat concept presence as scientific evidence.
    """
    cache = TemporaryResearchCache()
    nexus: ResearchNexus
    if nexus_path is None:
        nexus = InMemoryResearchNexus()
    else:
        nexus = JsonResearchNexus(nexus_path)

    catalog = standard_method_catalog()
    catalog.register(cross_evidence_method_spec())
    catalog.register(scientific_toolkit_method_spec())
    catalog.register(group_aggregation_method_spec())
    concepts = concept_library or seed_market_concepts()
    validator = TransparentInputBindingValidator(catalog)
    analysis = ExactMethodAnalysisExecutor()
    for method in standard_analysis_methods():
        analysis.register(method)
    analysis.register(cross_evidence_analysis_method())
    analysis.register(scientific_toolkit_analysis_method())
    analysis.register(group_aggregation_analysis_method())

    orchestrator = ResearchLoopOrchestrator(
        mission=mission,
        rd=rd,
        validator=validator,
        analysis=analysis,
        nexus=nexus,
        cache=cache,
        available_methods=catalog.capability_payloads(),
        research_concepts=concepts.payloads(),
        max_contract_repairs=max_contract_repairs,
    )
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
