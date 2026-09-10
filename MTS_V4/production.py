from __future__ import annotations

from dataclasses import dataclass

from .bootstrap import V4Runtime, build_runtime
from .campaign import CheckpointedCampaignRunner
from .checkpoint import JsonCampaignCheckpointStore
from .decision_journal import JsonResearchDecisionJournal
from .research_package_provider import ResearchPackageAwareResearchDirector
from .research_package_store import JsonResearchPackageStore
from .research_recording import CampaignResearchRecorder
from .runtime_config import ProductionRuntimeConfig


@dataclass(frozen=True, slots=True)
class ProductionRuntimeBundle:
    config: ProductionRuntimeConfig
    runtime: V4Runtime
    campaign_runner: CheckpointedCampaignRunner


def build_production_runtime(config: ProductionRuntimeConfig) -> ProductionRuntimeBundle:
    """Assemble the production backend without acquiring data or calling AI.

    Construction is deterministic wiring only. Credentials remain in the
    supplied configuration/environment and no network activity occurs until RD
    is actually invoked by a campaign.
    """
    config.state_dir.mkdir(parents=True, exist_ok=True)
    rd_config = config.research_director
    rd = ResearchPackageAwareResearchDirector(
        base_url=rd_config.base_url,
        model=rd_config.model,
        api_key=rd_config.api_key,
        timeout_seconds=rd_config.timeout_seconds,
    )
    runtime = build_runtime(
        rd=rd,
        nexus_path=config.nexus_path,
        max_contract_repairs=config.max_contract_repairs,
    )
    recorder = CampaignResearchRecorder(
        package_store=JsonResearchPackageStore(config.research_packages_path),
        decision_journal=JsonResearchDecisionJournal(config.rd_decision_journal_path),
    )
    runner = CheckpointedCampaignRunner(
        orchestrator=runtime.orchestrator,
        cache=runtime.cache,
        checkpoint_store=JsonCampaignCheckpointStore(config.checkpoint_path),
        research_recorder=recorder,
    )
    return ProductionRuntimeBundle(
        config=config,
        runtime=runtime,
        campaign_runner=runner,
    )
