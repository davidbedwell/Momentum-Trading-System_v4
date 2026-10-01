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
    assert "known_feature_gaps" in breakout.attributes


def test_all_planned_search_families_are_registered():
    from MTS_V4.search_families import FAMILY_FACTORIES
    assert set(FAMILY_FACTORIES) == {
        "MOMENTUM", "BREAKOUT", "TREND", "MEAN_REVERSION", "VOLATILITY",
        "VOLUME_LIQUIDITY", "RELATIVE_CROSS_SECTIONAL", "EVENT_EARNINGS",
        "MARKET_REGIME_STRUCTURE", "CROSS_FAMILY_COMPOSITE", "EXPERIMENTAL",
    }


def test_family_feature_values_cannot_masquerade_as_missing_predictor_columns():
    from MTS_V4.search_families import all_search_spaces_v1, implemented_predictor_columns
    implemented = implemented_predictor_columns()
    for space in all_search_spaces_v1():
        for gene in space.genes:
            for value in gene.values:
                if isinstance(value, str) and value.endswith("__v1"):
                    assert value in implemented, (space.family_id, gene.gene_id, value)


def test_every_market_family_declares_feature_gap_status_explicitly():
    from MTS_V4.search_families import all_search_spaces_v1
    for space in all_search_spaces_v1():
        assert "known_feature_gaps" in space.attributes
        assert isinstance(space.attributes["known_feature_gaps"], tuple)
        # Empty is an explicit completed-vocabulary state; nonempty entries must
        # name a real unavailable/deferred capability rather than an implicit gap.
        assert all(str(item).strip() for item in space.attributes["known_feature_gaps"])


def test_experimental_family_does_not_receive_unrestricted_feature_soup():
    from MTS_V4.search_families import experimental_search_space_v1
    space = experimental_search_space_v1()
    assert len(space.genes) == 1
    assert space.genes[0].values == ("RD_DEFINED_SEARCH_SPACE_REQUIRED",)


def test_evolutionary_search_is_reproducible_and_budget_bounded():
    from MTS_V4.computational_search import EvolutionaryConfig, EvolutionarySearchOptimizer
    opt = EvolutionarySearchOptimizer(EvolutionaryConfig(population_size=8, elite_count=2, tournament_size=2, fitness_metric="net_expectancy"))
    req = SearchRunRequest("ga1", opt.optimizer_id, momentum_search_space_v1(), "evidence:1", "DISCOVERY", 30, 123)
    a = opt.run(req, _adapter(), EvaluationCache())
    b = opt.run(req, _adapter(), EvaluationCache())
    assert a.proposed_count == 30
    assert b.proposed_count == 30
    assert [x.candidate_id for x in a.ledger] == [x.candidate_id for x in b.ledger]
    assert a.analysis_evaluation_count <= 30


def test_evolutionary_search_requires_predeclared_numeric_fitness():
    from MTS_V4.computational_search import EvolutionaryConfig, EvolutionarySearchOptimizer
    opt = EvolutionarySearchOptimizer(EvolutionaryConfig(population_size=4, elite_count=1, tournament_size=2, fitness_metric="scientific_significance"))
    req = SearchRunRequest("ga2", opt.optimizer_id, momentum_search_space_v1(), "evidence:1", "DISCOVERY", 8, 3)
    with pytest.raises(SearchGovernanceError):
        opt.run(req, _adapter())


def test_null_search_requires_explicit_null_evidence_namespace():
    from MTS_V4.computational_search import NullControlEvaluator
    with pytest.raises(SearchGovernanceError):
        NullControlEvaluator(_adapter(), null_evidence_identity="evidence:ordinary")


def test_null_search_preserves_same_budget_and_search_space():
    from MTS_V4.computational_search import RandomSearchOptimizer, run_null_search_control
    opt = RandomSearchOptimizer()
    req = SearchRunRequest("real", opt.optimizer_id, momentum_search_space_v1(), "evidence:real", "DISCOVERY", 12, 99)

    def eval_any(candidate: Candidate, evidence_identity: str) -> Evaluation:
        return Evaluation(candidate.candidate_id, evidence_identity, "null-test-v1", {"net_expectancy": 0.0})
    adapter = CallableAnalysisAdapter(analysis_contract_version="null-test-v1", evaluate_callable=eval_any)
    control = run_null_search_control(control_id="perm-001", optimizer=opt, request=req, evaluator=adapter, null_evidence_identity="null:perm-001")
    assert control.search_result.proposed_count == req.budget_evaluations
    assert control.search_result.search_space_hash == req.search_space.content_hash
    assert control.search_result.run_id.endswith(":null:perm-001")
