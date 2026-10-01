from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import statistics

from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore
from MTS_V4.search_candidate_analysis import _compile_signal, _finite


def _parser():
    p=argparse.ArgumentParser(description="Post-search Analysis gate for saved top candidates; does not mutate search results.")
    p.add_argument("--search-report", required=True)
    p.add_argument("--derived-market-root", required=True)
    p.add_argument("--top-n", type=int, default=10)
    p.add_argument("--output", required=True)
    return p


def _stats(values):
    n=len(values)
    mean=statistics.fmean(values) if values else None
    sd=statistics.stdev(values) if n>1 else None
    se=None if sd is None else sd/math.sqrt(n)
    return {
        "count":n,
        "mean_forward_return":mean,
        "standard_deviation":sd,
        "naive_standard_error":se,
        "positive_fraction":None if not values else sum(v>0 for v in values)/n,
    }


def _evaluate(candidate, predictors, outcomes):
    predictors=sorted(predictors,key=lambda row:(str(row["effective_date"]),str(row["security_id"])))
    horizon=int(candidate["genome"]["forward_horizon"])
    outcome_column=f"forward_return_{horizon}__v1"
    out_index={(str(r["security_id"]),str(r["effective_date"])):r for r in outcomes}
    signals=_compile_signal(predictors,candidate)
    raw=[]
    events=[]
    cooldown=0
    for row,active in zip(predictors,signals):
        out=out_index.get((str(row["security_id"]),str(row["effective_date"])))
        value=None if out is None else _finite(out.get(outcome_column))
        if active and value is not None:
            raw.append(value)
            if cooldown == 0:
                events.append(value)
                cooldown=horizon
        if cooldown:
            cooldown-=1
    return {
        "candidate_id":candidate["candidate_id"],
        "family_id":candidate["family_id"],
        "genome":candidate["genome"],
        "forward_horizon":horizon,
        "raw_signal_day_statistics":_stats(raw),
        "non_overlapping_opportunity_statistics":_stats(events),
        "dependence_warning":"RAW_SIGNAL_DAYS_HAVE_OVERLAPPING_FORWARD_WINDOWS_AND_ARE_NOT_INDEPENDENT_TRADES",
        "trade_policy":{
            "entry":"FIRST_ACTIVE_SIGNAL_WHEN_FLAT",
            "exit":f"FIXED_{horizon}_TRADING_SESSION_HORIZON_ENDPOINT_RETURN",
            "reentry":f"BLOCKED_FOR_{horizon}_SESSIONS_AFTER_ENTRY",
            "position_overlap":"PROHIBITED_WITHIN_CANDIDATE",
            "stop_loss":"UNAVAILABLE_REQUIRES_PATH_LEVEL_OUTCOME_SIMULATION",
        },
        "ev":{
            "gross_conditional_mean_return":_stats(events)["mean_forward_return"],
            "cost_adjusted_ev":"UNAVAILABLE_REQUIRES_ESTIMATED_ALL_IN_COST_INPUT",
            "r_multiple_ev":"UNAVAILABLE_REQUIRES_EXPLICIT_RISK_STOP_AND_PATH_LEVEL_SIMULATION",
        },
        "interpretation_boundary":"POST_SEARCH_ANALYSIS_ONLY_NOT_VALIDATION_NOT_PROMOTION",
    }


def main(argv=None):
    args=_parser().parse_args(argv)
    source=Path(args.search_report)
    report=json.loads(source.read_text(encoding="utf-8"))
    store=ParquetDerivedMarketStore(args.derived_market_root)
    security_id=report["security_id"]
    universe_id=report["universe_id"]
    predictors=list(store.query(DerivedMarketQuery(
        universe_id=universe_id,feature_set_id="mts_market_predictors",
        feature_set_version=report["predictor_feature_set_version"],security_ids=(security_id,),
    )))
    predictors.sort(key=lambda row: (str(row["effective_date"]), str(row["security_id"])))
    outcomes=store.query(DerivedMarketQuery(
        universe_id=universe_id,feature_set_id="mts_historical_outcomes",
        feature_set_version=report["outcome_feature_set_version"],security_ids=(security_id,),
    ))
    results={}
    for family_id,family in report["families"].items():
        results[family_id]={}
        for optimizer in ("random","ga"):
            candidates=family[optimizer]["top_candidates"][:args.top_n]
            results[family_id][optimizer]=[_evaluate(c,predictors,outcomes) for c in candidates]
    output={
        "format":"MTS_V4_POST_SEARCH_ANALYSIS_GATE_V1",
        "source_search_report":str(source),
        "ticker":report["ticker"],
        "security_id":security_id,
        "partition_id":report["partition_id"],
        "source_seed":report["seed"],
        "source_budget_per_family_per_optimizer":report["budget_per_family_per_optimizer"],
        "methodology":{
            "search_result_mutated":False,
            "non_overlap_rule":"after an accepted signal, suppress subsequent entries for the candidate forward_horizon trading sessions",
            "raw_signal_statistics_retained":True,
            "stop_path_claims_prohibited_without_path_data":True,
            "cost_adjusted_ev_prohibited_without_cost_input":True,
        },
        "results":results,
    }
    target=Path(args.output); target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(output,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    print(f"REPORT={target}")
    print("SEARCH_RESULT_MUTATED=False")
    print("SOL_CALLS=0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
