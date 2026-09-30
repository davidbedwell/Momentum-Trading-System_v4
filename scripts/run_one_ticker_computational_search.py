from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import json
import os
from pathlib import Path
import time

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
    p.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
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


def _run_family(*, family_id, ticker, predictors, outcomes, evidence_identity, budget, seed):
    started=time.monotonic()
    evaluator=SearchCandidateAnalysisEvaluator.build(
        subject_id=f"equity:{ticker}",
        predictor_rows=predictors,
        outcome_rows=outcomes,
        evidence_identity=evidence_identity,
    )
    space=FAMILY_FACTORIES[family_id]()
    random_opt=RandomSearchOptimizer()
    ga_opt=EvolutionarySearchOptimizer(EvolutionaryConfig(
        population_size=min(32,budget),
        elite_count=min(6,max(1,min(32,budget)-1)),
        tournament_size=min(3,min(32,budget)),
        fitness_metric="search_fitness",
    ))
    family_seed=seed + EXECUTABLE_FAMILIES.index(family_id)
    random_req=SearchRunRequest(
        run_id=f"{ticker}:{family_id}:random", optimizer_id=random_opt.optimizer_id,
        search_space=space, evidence_identity=evidence_identity, scientific_cohort="DISCOVERY",
        budget_evaluations=budget, seed=family_seed,
    )
    ga_req=SearchRunRequest(
        run_id=f"{ticker}:{family_id}:ga", optimizer_id=ga_opt.optimizer_id,
        search_space=space, evidence_identity=evidence_identity, scientific_cohort="DISCOVERY",
        budget_evaluations=budget, seed=family_seed,
    )
    random_result=random_opt.run(random_req,evaluator,EvaluationCache())
    print(f"PROGRESS FAMILY={family_id} OPTIMIZER=RANDOM COMPLETED={budget}/{budget} ELAPSED_SEC={time.monotonic()-started:.1f}", flush=True)
    ga_result=ga_opt.run(ga_req,evaluator,EvaluationCache())
    elapsed=time.monotonic()-started
    print(f"PROGRESS FAMILY={family_id} OPTIMIZER=GA COMPLETED={budget}/{budget} ELAPSED_SEC={elapsed:.1f}", flush=True)
    return family_id, {
        "search_space_hash":space.content_hash,
        "known_feature_gaps":list(space.attributes.get("known_feature_gaps",())),
        "random":{"summary":asdict(random_result)|{"ledger":[]}, "top_candidates":_top(random_result.ledger)},
        "ga":{"summary":asdict(ga_result)|{"ledger":[]}, "top_candidates":_top(ga_result.ledger)},
        "elapsed_seconds":elapsed,
    }


def _checkpoint_path(output: Path) -> Path:
    return output.with_suffix(output.suffix + ".checkpoint.json")


def _write_checkpoint(path: Path, identity: dict, families: dict) -> None:
    payload={"format":"MTS_V4_ONE_SUBJECT_COMPUTATIONAL_SEARCH_CHECKPOINT_V1","identity":identity,"families":families}
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(payload,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    tmp.replace(path)


def main(argv=None) -> int:
    args=_parser().parse_args(argv)
    if args.budget_per_family < 10:
        raise RuntimeError("--budget-per-family must be >= 10")
    if args.workers < 1:
        raise RuntimeError("--workers must be >= 1")
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
    identity={
        "ticker":ticker,"security_id":security_id,"universe_id":args.universe_id,
        "partition_id":partition.partition_id,"evidence_identity":evidence_identity,
        "predictor_feature_set_version":args.predictor_feature_set_version,
        "outcome_feature_set_version":args.outcome_feature_set_version,
        "budget_per_family_per_optimizer":args.budget_per_family,"seed":args.seed,
    }
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    checkpoint=_checkpoint_path(target)
    families={}
    if checkpoint.exists():
        prior=json.loads(checkpoint.read_text(encoding="utf-8"))
        if prior.get("identity") != identity:
            raise RuntimeError(f"checkpoint identity mismatch: {checkpoint}")
        families=dict(prior.get("families",{}))
        print(f"CHECKPOINT_RESUME={checkpoint} COMPLETED_FAMILIES={len(families)}/{len(EXECUTABLE_FAMILIES)}", flush=True)

    pending=[f for f in EXECUTABLE_FAMILIES if f not in families]
    workers=min(args.workers,max(1,len(pending)))
    print(f"SEARCH_START TICKER={ticker} PENDING_FAMILIES={len(pending)} WORKERS={workers} BUDGET_PER_FAMILY_PER_OPTIMIZER={args.budget_per_family}", flush=True)
    started=time.monotonic()

    if workers == 1:
        for family_id in pending:
            fid,result=_run_family(
                family_id=family_id,ticker=ticker,predictors=predictors,outcomes=outcomes,
                evidence_identity=evidence_identity,budget=args.budget_per_family,seed=args.seed,
            )
            families[fid]=result
            _write_checkpoint(checkpoint,identity,families)
            print(f"CHECKPOINT_SAVED FAMILY={fid} COMPLETED_FAMILIES={len(families)}/{len(EXECUTABLE_FAMILIES)}",flush=True)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            future_map={
                pool.submit(
                    _run_family,
                    family_id=family_id,ticker=ticker,predictors=predictors,outcomes=outcomes,
                    evidence_identity=evidence_identity,budget=args.budget_per_family,seed=args.seed,
                ): family_id for family_id in pending
            }
            for future in as_completed(future_map):
                fid,result=future.result()
                families[fid]=result
                _write_checkpoint(checkpoint,identity,families)
                print(f"CHECKPOINT_SAVED FAMILY={fid} COMPLETED_FAMILIES={len(families)}/{len(EXECUTABLE_FAMILIES)} ELAPSED_SEC={time.monotonic()-started:.1f}",flush=True)

    ordered_families={fid:families[fid] for fid in EXECUTABLE_FAMILIES}
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
        "workers":workers,
        "earnings_policy":{
            "EVENT_EARNINGS_ALPHA_SEARCH":"DEFERRED_FOR_FIRST_TEST",
            "POST_EARNINGS_RISK_FILTER":"AVAILABLE_FOR_LATER_CONTROL",
            "PRE_EARNINGS_FILTER":"BLOCKED_UNTIL_PIT_SCHEDULED_EARNINGS_CALENDAR",
        },
        "interpretation_boundary":"COMPUTATIONAL_SEARCH_LANDSCAPE_ONLY_RD_SOL_MUST_INTERPRET",
        "families":ordered_families,
    }
    target.write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    if checkpoint.exists():
        checkpoint.unlink()
    print(f"REPORT={target}")
    print(f"TOTAL_ELAPSED_SEC={time.monotonic()-started:.1f}")
    print("SOL_CALLS=0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
