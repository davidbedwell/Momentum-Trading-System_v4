from __future__ import annotations

from typing import Mapping

from .blind_validation import (
    BlindValidationResearchDirector,
    HistoricalBlindValidationSession,
)
from .bootstrap import V4Runtime
from .contracts import AnalysisRequest, AnalysisResult, ContractDefect, EvidenceDescriptor, ResearchPhase
from .execution_interface import TransparentInputBindingValidator
from .orchestrator import ResearchLoopOrchestrator
from .research_package_store import JsonResearchPackageStore
from .verification_eligibility import require_unseen_historical_verification_subject


class BlindPredictionValidator(TransparentInputBindingValidator):
    """Add the objective VALIDATION-only boundary for a historical blind run."""

    def validate(
        self,
        request: AnalysisRequest,
        evidence: Mapping[str, EvidenceDescriptor],
        analysis_results: Mapping[str, AnalysisResult] | None = None,
    ) -> tuple[ContractDefect, ...]:
        defects = list(super().validate(request, evidence, analysis_results))
        if request.research_phase is not ResearchPhase.VALIDATION:
            defects.append(
                ContractDefect(
                    code="BLIND_VALIDATION_REQUIRES_VALIDATION_PHASE",
                    message=(
                        "Historical blind prediction requests must use research_phase=VALIDATION. "
                        "The prediction sandbox is not an exploratory look-ahead context."
                    ),
                    field="research_phase",
                    method_id=request.method_id,
                )
            )
        return tuple(defects)


def build_blind_prediction_orchestrator(
    *,
    session: HistoricalBlindValidationSession,
    runtime: V4Runtime,
    research_package_store: JsonResearchPackageStore,
    hypothesis_statement: str,
    success_definition: str,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    timeout_seconds: int = 180,
) -> ResearchLoopOrchestrator:
    """Build retrospective historical blind verification on an unseen subject.

    The unseen-subject requirement applies only to retrospective historical
    replay/holdout verification. It does not govern genuine live prospective
    prediction or trading, where the future outcome has not yet occurred.

    Scientific methods remain exactly the methods registered in the supplied v4
    runtime. The historical blind run receives the session's masked cache,
    masked evidence, isolated Nexus, no exploratory concept payloads, and a
    non-RP-aware RD transport containing only the frozen hypothesis and success
    definition.

    Provider arguments are explicit when supplied so the caller can preserve the
    approved AI scientific authority for the blind stage. If omitted, the blind
    RD retains the legacy environment-based provider behavior.
    """

    require_unseen_historical_verification_subject(
        package_store=research_package_store,
        subject_id=session.subject.subject_id,
    )
    rd = BlindValidationResearchDirector(
        trial_id=session.trial_id,
        hypothesis_id=session.hypothesis_id,
        hypothesis_statement=hypothesis_statement,
        success_definition=success_definition,
        base_url=base_url,
        model=model,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
    )
    validator = BlindPredictionValidator(runtime.catalog)
    return ResearchLoopOrchestrator(
        mission=runtime.mission,
        rd=rd,
        validator=validator,
        analysis=runtime.analysis,
        nexus=session.nexus,
        cache=session.cache,
        available_methods=runtime.catalog.capability_payloads(),
        research_concepts=(),
        max_contract_repairs=3,
    )
