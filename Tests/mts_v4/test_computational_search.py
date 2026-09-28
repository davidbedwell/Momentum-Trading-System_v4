from __future__ import annotations

import pytest

from MTS_V4.computational_search import (
    CallableAnalysisAdapter, Candidate, Evaluation, EvaluationCache,
    RandomSearchOptimizer, SearchGovernanceError, SearchRunRequest,
)
from MTS_V4.search_families import breakout_search_space_v1, momentum_search_space_v1


def _adapter():
    def evaluate(candidate: Candidate, evidence_identity: str) -> Evaluation:
        return Evaluation(
            candidate_id=candidate.candidate_id,
            evidence_identity=evidence_identity,
            analysis_contract_version="test-v1",
            metrics={"net_expectancy": float(len(candidate.genome))},
            analysis_refs=(f"analysis:{candidate.candidate_id}",),
        )
    return CallableAnalysisAdapter(analysis_contract_version="test-v1", evaluate_callable=evaluate)


def test_adaptive_search_fails_closed_outside_discovery():
    with pytest.raises(SearchGovernanceError):
        SearchRunRequest("r", "search.random.v1", momentum_search_space_v1(), "e", "VERIFICATION_A", 10, 7)


def test_random_search_is_seed_reproducible_and_cacheable():
    optimizer = RandomSearchOptimizer()
    cache = EvaluationCache()
    request = SearchRunRequest("r1", optimizer.optimizer_id, momentum_search_space_v1(), "evidence:1", "DISCOVERY", 25, 42)
    first = optimizer.run(request, _adapter(), cache)
    second = optimizer.run(request, _adapter(), cache)
    assert [x.candidate_id for x in first.ledger] == [x.candidate_id for x in second.ledger]
    assert first.analysis_evaluation_count > 0
    assert second.analysis_evaluation_count == 0
    assert second.cache_hit_count == 25
    assert first.search_space_hash == momentum_search_space_v1().content_hash


def test_candidate_identity_ignores_search_ancestry():
    a = Candidate.from_genome(family_id="MOMENTUM", genome={"x": 1}, parent_ids=("p1",), proposal_source="GA")
    b = Candidate.from_genome(family_id="MOMENTUM", genome={"x": 1}, parent_ids=("p2",), proposal_source="RANDOM")
    assert a.candidate_id == b.candidate_id


def test_breakout_and_momentum_share_framework_but_have_distinct_spaces():
    momentum = momentum_search_space_v1()
    breakout = breakout_search_space_v1()
    assert momentum.family_id == "MOMENTUM"
    assert breakout.family_id == "BREAKOUT"
    assert momentum.content_hash != breakout.content_hash
    assert breakout.attributes["known_feature_gaps"]
