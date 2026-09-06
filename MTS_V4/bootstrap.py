from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .analysis import ExactMethodAnalysisExecutor
from .cache import TemporaryResearchCache
from .interfaces import ResearchDirectorProvider
from .method_catalog import MethodCatalog
from .nexus import InMemoryResearchNexus, ResearchNexus
from .nexus_json import JsonResearchNexus
from .orchestrator import ResearchLoopOrchestrator
from .standard_methods import standard_analysis_methods, standard_method_catalog
from .validation import ObjectiveContractValidator


DEFAULT_MISSION = (
    "Discover reproducible market conditions that can identify subsequent price "
    "movements with sufficient magnitude, directionality, timing, and path quality "
    "to be practically exploitable as trades."
)


@dataclass(frozen=True, slots=True)
class V4Runtime:
    mission: str
    cache: TemporaryResearchCache
    nexus: ResearchNexus
    catalog: MethodCatalog
    validator: ObjectiveContractValidator
    analysis: ExactMethodAnalysisExecutor
    orchestrator: ResearchLoopOrchestrator


def build_runtime(
    *,
    rd: ResearchDirectorProvider,
    mission: str = DEFAULT_MISSION,
    nexus_path: str | Path | None = None,
    max_contract_repairs: int = 3,
) -> V4Runtime:
    """Assemble the v4 research runtime without external credentials or data.

    Provider creation is intentionally outside this function. The caller may use
    a fake AI for proofs or an approved live provider at integration time.
    """
    cache = TemporaryResearchCache()
    nexus: ResearchNexus
    if nexus_path is None:
        nexus = InMemoryResearchNexus()
    else:
        nexus = JsonResearchNexus(nexus_path)

    catalog = standard_method_catalog()
    validator = ObjectiveContractValidator(catalog)
    analysis = ExactMethodAnalysisExecutor()
    for method in standard_analysis_methods():
        analysis.register(method)

    orchestrator = ResearchLoopOrchestrator(
        mission=mission,
        rd=rd,
        validator=validator,
        analysis=analysis,
        nexus=nexus,
        cache=cache,
        available_methods=catalog.capability_payloads(),
        max_contract_repairs=max_contract_repairs,
    )
    return V4Runtime(
        mission=mission,
        cache=cache,
        nexus=nexus,
        catalog=catalog,
        validator=validator,
        analysis=analysis,
        orchestrator=orchestrator,
    )
