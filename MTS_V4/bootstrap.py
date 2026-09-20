from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .acceptance_controls import null_analysis_method, null_method_spec
from .analysis import ExactMethodAnalysisExecutor
from .batch_orchestrator import BatchResearchDirectorProvider, BatchResearchLoopOrchestrator
from .cache import TemporaryResearchCache
from .cached_analysis import CachedLineageAwareAnalysisExecutor
from .concept_library import ResearchConceptLibrary, seed_market_concepts
from .cross_evidence import cross_evidence_analysis_method, cross_evidence_method_spec
from .cross_sectional_analysis import analysis_method as cross_sectional_analysis_method
from .cross_sectional_analysis import method_spec as cross_sectional_method_spec
from .cross_sectional_statistics import analysis_method as cross_sectional_statistics_method
from .cross_sectional_statistics import method_spec as cross_sectional_statistics_spec
from .cross_sectional_association import analysis_method as cross_sectional_association_method
from .cross_sectional_association import method_spec as cross_sectional_association_spec
from .cross_subject_batch_orchestrator import CrossSubjectBatchResearchLoopOrchestrator
from .cross_subject_memory import CrossSubjectScientificMemory
from .cross_subject_orchestrator import CrossSubjectResearchLoopOrchestrator
from .discovery_methods import discovery_analysis_methods, discovery_method_catalog
from .execution_interface import TransparentInputBindingValidator
from .group_aggregation import group_aggregation_analysis_method, group_aggregation_method_spec
from .interfaces import ResearchDirectorProvider
from .intraday_analysis_substrate import analysis_method as intraday_substrate_analysis_method
from .intraday_analysis_substrate import method_spec as intraday_substrate_method_spec
from .method_catalog import MethodCatalog
from .multiple_testing import analysis_method as multiple_testing_analysis_method
from .multiple_testing import method_spec as multiple_testing_method_spec
from .nexus import InMemoryResearchNexus, ResearchNexus
from .nexus_json import JsonResearchNexus
from .neutral_analysis_substrate import analysis_method as substrate_analysis_method
from .neutral_analysis_substrate import method_spec as substrate_method_spec
from .neutral_pre_sol_context import analysis_methods as neutral_context_analysis_methods
from .neutral_pre_sol_context import method_specs as neutral_context_method_specs
from .orchestrator import ResearchLoopOrchestrator
from .participation_analysis import analysis_method as participation_analysis_method
from .participation_analysis import method_spec as participation_method_spec
from .rolling_analysis_transform import analysis_method as rolling_analysis_method
from .rolling_analysis_transform import method_spec as rolling_method_spec
from .scientific_toolkit import scientific_toolkit_analysis_method, scientific_toolkit_method_spec
from .share_structure_analysis import analysis_method as share_structure_analysis_method
from .share_structure_analysis import method_spec as share_structure_method_spec
from .standard_methods import standard_analysis_methods, standard_method_catalog
from .universe_market_structure_substrate import analysis_method as universe_substrate_analysis_method
from .universe_market_structure_substrate import method_spec as universe_substrate_method_spec

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

@dataclass(frozen=True, slots=True)
class BatchV4Runtime:
    mission: str
    cache: TemporaryResearchCache
    nexus: ResearchNexus
    catalog: MethodCatalog
    concepts: ResearchConceptLibrary
    validator: TransparentInputBindingValidator
    analysis: ExactMethodAnalysisExecutor
    orchestrator: BatchResearchLoopOrchestrator

def _build_execution_components(*, nexus_path: str | Path | None, derived_market_root: str | Path | None, concept_library: ResearchConceptLibrary | None) -> tuple[TemporaryResearchCache, ResearchNexus, MethodCatalog, ResearchConceptLibrary, TransparentInputBindingValidator, ExactMethodAnalysisExecutor]:
    cache = TemporaryResearchCache()
    nexus: ResearchNexus = InMemoryResearchNexus() if nexus_path is None else JsonResearchNexus(nexus_path, derived_market_root=derived_market_root)
    catalog = standard_method_catalog()
    for spec in discovery_method_catalog().all(): catalog.register(spec)
    for spec in (cross_evidence_method_spec(), scientific_toolkit_method_spec(), group_aggregation_method_spec(), substrate_method_spec(), share_structure_method_spec(), intraday_substrate_method_spec(), participation_method_spec(), rolling_method_spec(), cross_sectional_method_spec(), cross_sectional_statistics_spec(), cross_sectional_association_spec(), null_method_spec(), multiple_testing_method_spec(), universe_substrate_method_spec(), *neutral_context_method_specs()): catalog.register(spec)
    concepts = concept_library or seed_market_concepts()
    validator = TransparentInputBindingValidator(catalog)
    analysis = CachedLineageAwareAnalysisExecutor()
    for method in standard_analysis_methods(): analysis.register(method)
    for method in discovery_analysis_methods(): analysis.register(method)
    for method in (cross_evidence_analysis_method(), scientific_toolkit_analysis_method(), group_aggregation_analysis_method(), substrate_analysis_method(), share_structure_analysis_method(), intraday_substrate_analysis_method(), participation_analysis_method(), rolling_analysis_method(), cross_sectional_analysis_method(), cross_sectional_statistics_method(), cross_sectional_association_method(), null_analysis_method(), multiple_testing_analysis_method(), universe_substrate_analysis_method(), *neutral_context_analysis_methods()): analysis.register(method)
    return cache, nexus, catalog, concepts, validator, analysis

def build_runtime(*, rd: ResearchDirectorProvider, mission: str = DEFAULT_MISSION, nexus_path: str | Path | None = None, derived_market_root: str | Path | None = None, concept_library: ResearchConceptLibrary | None = None, max_contract_repairs: int = 3, scientific_memory: CrossSubjectScientificMemory | None = None) -> V4Runtime:
    cache, nexus, catalog, concepts, validator, analysis = _build_execution_components(nexus_path=nexus_path, derived_market_root=derived_market_root, concept_library=concept_library)
    orchestrator_type = CrossSubjectResearchLoopOrchestrator if scientific_memory is not None else ResearchLoopOrchestrator
    kwargs = {"mission": mission, "rd": rd, "validator": validator, "analysis": analysis, "nexus": nexus, "cache": cache, "available_methods": catalog.capability_payloads(), "research_concepts": concepts.payloads(), "max_contract_repairs": max_contract_repairs}
    if scientific_memory is not None: kwargs["scientific_memory"] = scientific_memory
    orchestrator = orchestrator_type(**kwargs)
    return V4Runtime(mission, cache, nexus, catalog, concepts, validator, analysis, orchestrator)

def build_batch_runtime(*, rd: BatchResearchDirectorProvider, mission: str = DEFAULT_MISSION, nexus_path: str | Path | None = None, derived_market_root: str | Path | None = None, concept_library: ResearchConceptLibrary | None = None, scientific_memory: CrossSubjectScientificMemory | None = None) -> BatchV4Runtime:
    cache, nexus, catalog, concepts, validator, analysis = _build_execution_components(nexus_path=nexus_path, derived_market_root=derived_market_root, concept_library=concept_library)
    orchestrator_type = CrossSubjectBatchResearchLoopOrchestrator if scientific_memory is not None else BatchResearchLoopOrchestrator
    kwargs = {"mission": mission, "rd": rd, "validator": validator, "analysis": analysis, "nexus": nexus, "cache": cache, "available_methods": catalog.capability_payloads(), "research_concepts": concepts.payloads()}
    if scientific_memory is not None: kwargs["scientific_memory"] = scientific_memory
    orchestrator = orchestrator_type(**kwargs)
    return BatchV4Runtime(mission, cache, nexus, catalog, concepts, validator, analysis, orchestrator)
