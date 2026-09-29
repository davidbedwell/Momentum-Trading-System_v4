from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from MTS_V4.computational_search import EvaluationCache, EvolutionaryConfig, EvolutionarySearchOptimizer, RandomSearchOptimizer, SearchRunRequest
from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import SearchCandidateAnalysisEvaluator
from MTS_V4.search_families import FAMILY_FACTORIES
from MTS_V4.universe_membership import load_membership_csv
from MTS_V4.universe_scientific_partition import ScientificCohort, load_frozen_partition


EXECUTABLE_FAMILIES = (
    "MOMENTUM","BREAKOUT","TREND","MEAN_REVERSION",
    "VOLATILITY","VOLUME_LIQUIDITY","RELATIVE_CROSS_SECTIONAL",
    "MARKET_REGIME_STRUCTURE",
)


def _parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="Run governed Random-vs-GA Discovery search for one ticker.")
    p.add_argument("--ticker", required=True)
    p.add_argument("--derived-market-root", required=True)
    p.add_argument("--universe-id", required=True)
    p.add_argument("--membership-csv", required=True)
    p.add_argument("--scientific-partition-manifest", required=True)
    p.add_argument("--predictor-feature-set-version", default="v2")
    p.add_argument("--outcome-feature-set-version", default="v1")
    p.add_argument("--budget-per-family", type=int, default=500)
    p.add_argument("--seed", type=int, default=20260928)
    p.add_argument("--output", required=True)
    return p


def _ticker_identity(membership, ticker: str) -> str:
    matches={x.security_id for x in membership.intervals() if x.ticker.upper()==ticker}
    if len(matches)!=1:
        raise RuntimeError(f"expected exactly one security identity for {ticker}; found {sorted(matches)}")
    return next(iter(matches))


def _top(entries, n=10):
    usable=[e for e in entries if isinstance(e.metrics.get("search_fitness"), (int,float))]
    usable.sort(key=lambda e: float(e.metrics["search_fitness"]), reverse=True)
    return [
        {
            "candidate_id":e.candidate_id,
            "family_id":e.family_id,
            "genome":dict(e.genome),
            "proposal_source":e.proposal_source,
            "parent_ids":list(e.parent_ids),
            "metrics":dict(e.metrics),
        } for e in usable[:n]
    ]


def main(argv=None) -> int:
    args=_parser().parse_args(argv)
    if args.budget_per_family < 10:
        raise RuntimeError("--budget-per-family must be >= 10")
    ticker=args.ticker.upper().strip()
    membership=load_membership_csv(args.membership_csv)
    security_id=_ticker_identity(membership,ticker)
    partition=load_frozen_partition(args.scientific_partition_manifest)
    if partition.universe_id != args.universe_id:
        raise RuntimeError("partition universe mismatch")
    if security_id not in partition.members(ScientificCohort.DISCOVERY):
        raise RuntimeError(f"{ticker} is not in DISCOVERY; adaptive search is prohibited")

    store=ParquetDerivedMarketStore(args.derived_market_root)
    predictor_set=store.get_feature_set("mts_market_predictors", args.predictor_feature_set_version)
    outcome_set=store.get_feature_set("mts_historical_outcomes", args.outcome_feature_set_version)
    if predictor_set is None:
        raise RuntimeError("predictor v2 is absent; rebuild/maintain the derived store before search")
    if outcome_set is None:
        raise RuntimeError("historical outcomes are absent")

    predictors=store.query(DerivedMarketQuery(
        universe_id=args.universe_id,
        feature_set_id="mts_market_predictors",
        feature_set_version=args.predictor_feature_set_version,
        security_ids=(security_id,),
    ))
    outcomes=store.query(DerivedMarketQuery(
        universe_id=args.universe_id,
        feature_set_id="mts_historical_outcomes",
        feature_set_version=args.outcome_feature_set_version,
        security_ids=(security_id,),
    ))
    if not predictors or not outcomes:
        raise RuntimeError("ticker predictor/outcome rows are missing")

    evidence_identity=f"{partition.partition_id}|{security_id}|predictors:{args.predictor_feature_set_version}|outcomes:{args.outcome_feature_set_version}"
    evaluator=SearchCandidateAnalysisEvaluator.build(
        subject_id=f"equity:{ticker}",
        predictor_rows=predictors,
        outcome_rows=outcomes,
        evidence_identity=evidence_identity,
    )

    families={}
    for family_id in EXECUTABLE_FAMILIES:
        space=FAMILY_FACTORIES[family_id]()
        random_opt=RandomSearchOptimizer()
        ga_opt=EvolutionarySearchOptimizer(EvolutionaryConfig(
            population_size=min(32,args.budget_per_family),
            elite_count=min(6,max(1,min(32,args.budget_per_family)-1)),
            tournament_size=min(3,min(32,args.budget_per_family)),
            fitness_metric="search_fitness",
        ))
        family_seed=args.seed + EXECUTABLE_FAMILIES.index(family_id)
        random_req=SearchRunRequest(
            run_id=f"{ticker}:{family_id}:random", optimizer_id=random_opt.optimizer_id,
            search_space=space, evidence_identity=evidence_identity, scientific_cohort="DISCOVERY",
            budget_evaluations=args.budget_per_family, seed=family_seed,
        )
        ga_req=SearchRunRequest(
            run_id=f"{ticker}:{family_id}:ga", optimizer_id=ga_opt.optimizer_id,
            search_space=space, evidence_identity=evidence_identity, scientific_cohort="DISCOVERY",
            budget_evaluations=args.budget_per_family, seed=family_seed,
        )
        random_result=random_opt.run(random_req,evaluator,EvaluationCache())
        ga_result=ga_opt.run(ga_req,evaluator,EvaluationCache())
        families[family_id]={
            "search_space_hash":space.content_hash,
            "known_feature_gaps":list(space.attributes.get("known_feature_gaps",())),
            "random":{"summary":asdict(random_result)|{"ledger":[]}, "top_candidates":_top(random_result.ledger)},
            "ga":{"summary":asdict(ga_result)|{"ledger":[]}, "top_candidates":_top(ga_result.ledger)},
        }
        print(f"FAMILY={family_id} RANDOM_EVALS={random_result.analysis_evaluation_count} GA_EVALS={ga_result.analysis_evaluation_count}", flush=True)

    report={
        "format":"MTS_V4_ONE_SUBJECT_COMPUTATIONAL_SEARCH_V1",
        "ticker":ticker,
        "security_id":security_id,
        "cohort":"DISCOVERY",
        "universe_id":args.universe_id,
        "partition_id":partition.partition_id,
        "predictor_feature_set_version":args.predictor_feature_set_version,
        "outcome_feature_set_version":args.outcome_feature_set_version,
        "budget_per_family_per_optimizer":args.budget_per_family,
        "seed":args.seed,
        "earnings_policy":{
            "EVENT_EARNINGS_ALPHA_SEARCH":"DEFERRED_FOR_FIRST_TEST",
            "POST_EARNINGS_RISK_FILTER":"AVAILABLE_FOR_LATER_CONTROL",
            "PRE_EARNINGS_FILTER":"BLOCKED_UNTIL_PIT_SCHEDULED_EARNINGS_CALENDAR",
        },
        "interpretation_boundary":"COMPUTATIONAL_SEARCH_LANDSCAPE_ONLY_RD_SOL_MUST_INTERPRET",
        "families":families,
    }
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    print(f"REPORT={target}")
    print("SOL_CALLS=0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
