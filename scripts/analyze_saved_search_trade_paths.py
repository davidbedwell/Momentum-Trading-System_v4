from __future__ import annotations

import argparse
import json
from pathlib import Path

from MTS_V4.derived_market_store import DerivedMarketQuery, ParquetDerivedMarketStore
from MTS_V4.derived_market_updater import YFinanceDailyMarketSource
from MTS_V4.search_candidate_analysis import _compile_signal
from MTS_V4.trade_path_analysis import TradePathError, simulate_long_path, summarize_paths

STOP_FRACTIONS=(0.02,0.05,0.10,0.15)


def _parser():
    p=argparse.ArgumentParser(description="Executable next-session-open trade-path Analysis for saved search candidates.")
    p.add_argument("--search-report",required=True)
    p.add_argument("--derived-market-root",required=True)
    p.add_argument("--top-n",type=int,default=10)
    p.add_argument("--output",required=True)
    return p


def _accepted_signal_indices(signals,horizon):
    accepted=[]; next_allowed=0
    for i,active in enumerate(signals):
        if active and i>=next_allowed:
            accepted.append(i)
            next_allowed=i+horizon
    return accepted


def main(argv=None):
    args=_parser().parse_args(argv)
    search=json.loads(Path(args.search_report).read_text())
    store=ParquetDerivedMarketStore(args.derived_market_root)
    security_id=search["security_id"]; universe_id=search["universe_id"]
    predictors=list(store.query(DerivedMarketQuery(
        universe_id=universe_id,feature_set_id="mts_market_predictors",
        feature_set_version=search["predictor_feature_set_version"],security_ids=(security_id,),
    )))
    predictors.sort(key=lambda r:str(r["effective_date"]))
    if not predictors:
        raise SystemExit("TRADE_PATH_FAIL=NO_PREDICTORS")
    ticker=search["ticker"]
    start=str(predictors[0]["effective_date"]); end=str(predictors[-1]["effective_date"])
    raw=list(YFinanceDailyMarketSource().fetch(ticker=ticker,start_date=start,end_date=end))
    raw.sort(key=lambda r:str(r["date"]))
    by_date={str(r["date"]):i for i,r in enumerate(raw)}
    results={}
    for family_id,family in search["families"].items():
        results[family_id]={}
        for optimizer in ("random","ga"):
            evaluated=[]
            for candidate in family[optimizer]["top_candidates"][:args.top_n]:
                horizon=int(candidate["genome"]["forward_horizon"])
                signals=_compile_signal(predictors,candidate)
                accepted=_accepted_signal_indices(signals,horizon)
                paths=[]; excluded=[]
                for pi in accepted:
                    signal_date=str(predictors[pi]["effective_date"])
                    raw_i=by_date.get(signal_date)
                    if raw_i is None:
                        excluded.append({"signal_date":signal_date,"reason":"SIGNAL_DATE_MISSING_FROM_REACQUIRED_OHLCV"})
                        continue
                    try:
                        paths.append(simulate_long_path(
                            bars=raw,signal_index=raw_i,horizon_sessions=horizon,
                            stop_fractions=STOP_FRACTIONS,
                        ))
                    except TradePathError as exc:
                        excluded.append({"signal_date":signal_date,"reason":str(exc)})
                evaluated.append({
                    "candidate_id":candidate["candidate_id"],"family_id":family_id,
                    "genome":candidate["genome"],"accepted_nonoverlap_signals":len(accepted),
                    "executable_trade_paths":len(paths),"excluded_paths":excluded,
                    "summary":summarize_paths(paths),
                    "paths":[{
                        "signal_date":p.signal_date,"entry_date":p.entry_date,"exit_date":p.exit_date,
                        "entry_price":p.entry_price,"exit_price":p.exit_price,
                        "fixed_horizon_return":p.fixed_horizon_return,
                        "mae_return":p.mae_return,"mfe_return":p.mfe_return,
                        "stop_results":p.stop_results,
                    } for p in paths],
                })
            results[family_id][optimizer]=evaluated
    out={
        "format":"MTS_V4_EXECUTABLE_TRADE_PATH_ANALYSIS_V1",
        "source_search_report":args.search_report,"ticker":ticker,"security_id":security_id,
        "source_seed":search["seed"],"partition_id":search["partition_id"],
        "raw_market_source":"YFINANCE_DAILY_AUTO_ADJUSTED_REACQUIRED_NOT_PERSISTED",
        "execution_policy":{
            "signal_information_cutoff":"COMPLETED_SIGNAL_DAY_BAR",
            "entry":"NEXT_TRADING_SESSION_OPEN",
            "exit":"CLOSE_ON_SIGNAL_DATE_PLUS_FORWARD_HORIZON_TRADING_SESSIONS",
            "overlapping_positions":"PROHIBITED_WITHIN_CANDIDATE",
            "exploratory_stop_fractions":list(STOP_FRACTIONS),
            "gap_through_stop":"FILL_AT_OBSERVED_OPEN",
            "intraday_stop_touch":"FILL_AT_STOP",
            "profit_target":"NONE",
            "transaction_costs":"NOT_APPLIED",
        },
        "scientific_boundary":"DISCOVERY_POST_SEARCH_ANALYSIS_ONLY_NOT_VALIDATION_NOT_PROMOTION",
        "search_result_mutated":False,"results":results,
    }
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(f"RAW_OHLCV_ROWS={len(raw)}")
    print(f"REPORT={target}")
    print("SEARCH_RESULT_MUTATED=False")
    print("SOL_CALLS=0")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
