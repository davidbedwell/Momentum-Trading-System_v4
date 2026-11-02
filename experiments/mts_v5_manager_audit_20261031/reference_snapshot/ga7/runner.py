"""GA7 DEV79 research runner. Execute from repository root with python -m ga7.runner."""
import argparse
import base64
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import pickle
import random
import time
import pandas as pd

from math import sqrt
from ga7.engine import FAMILIES, Genome, next_population, random_genome, add_behavioral_diversity, niche_population_groups
from ga7.request_replay import replay_requests
from ga7.guardrails import Guardrails
from ga7.stagnation import update_stagnation
from ga7.niche_controller import controlling_niche
from ga7.ga7_folds import expanding_walk_forward
from ga7.fold_features import rank_filtered_sessions
from ga7.independence import unique_training_epochs,assert_nonoverlapping_forward
from ga7.defense_contract import read_defense_state
from ga7.chronological_partition import partition

FEATURES = {
    "momentum": ("ga4_return_5__v1", "ga4_return_20__v1"),
    "breakout": ("ga4_prior_high_break_distance_20__v1", "ga4_range_position_20__v1"),
    "trend": ("ga4_close_to_sma_50__v1", "ga4_sma50_slope_10__v1"),
    "mean_reversion": ("ga4_rsi_14__v1", "ga4_price_zscore_20__v1"),
    "volatility": ("ga4_natr_14__v1", "ga4_volatility_ratio_20_63__v1"),
    "volume_liquidity": ("ga4_relative_volume_20__v1", "ga4_dollar_volume_relative_20__v1"),
    "relative_cross_sectional": ("ga4_return_126_percentile__v1", "ga4_return_252_percentile__v1"),
    "market_regime_structure": ("ga4_breadth_above_sma_200__v1", "ga4_sector_vs_universe_return_63__v1"),
}
COLUMNS = sorted({x for pair in FEATURES.values() for x in pair})
SESSIONS = None
GUARDS = None
FOLD_WINDOWS = None
FOLD_CACHE = {}

def load_sessions(data_path, tape_path, policy_path, selected_tickers=None):
    frame = pd.read_parquet(data_path)
    if not {"dividends", "stock_splits", "security_id"}.issubset(frame.columns):
        raise ValueError("Missing corporate action or security identity columns")
    required = {"date", "ticker", "open", "close", "low", "dividends", "stock_splits", "sector_name", *COLUMNS}
    if not required.issubset(frame.columns):
        raise ValueError("Missing data columns: " + str(sorted(required - set(frame.columns))))
    frame["date"] = pd.to_datetime(frame.date).dt.strftime("%Y-%m-%d")
    frame["dividends"] = frame["dividends"].fillna(0)
    frame["stock_splits"] = frame["stock_splits"].fillna(0)
    frame = frame[(frame.date >= "2009-01-01") & (frame.date <= "2026-09-14")].copy()
    if frame.ticker.nunique() != 79:
        raise ValueError("DEV79 ticker count mismatch")
    if frame.duplicated(["date", "ticker"]).any():
        raise ValueError("Duplicate date/ticker bars")
    # Keep raw features until eligible universe and stock fold are selected.
    # Ranking the full DEV79 universe here would contaminate fold ranks.
    if selected_tickers is not None:
        if not set(selected_tickers).issubset(set(frame.ticker)):
            raise ValueError("Selected fold contains tickers missing from DEV79")
        frame = frame[frame.ticker.isin(selected_tickers)].copy()
    # Each distance is already divided by its OWN past-only annual radius.
    # Model metadata records training cutoff and evaluation interval.
    manifest_path = Path("/opt/mts/ga7-deploy/ga7_unbounded/niche_pit_manifest.json")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("status") not in ("PIT_VERIFIED", "CHRONOLOGY_VERIFIED_FEATURE_PROVENANCE_PENDING"):
        raise ValueError("Chronological niche model missing or invalid")
    models = json.loads(Path(manifest["model_file"]).read_text())
    for model in models:
        if not (model["trained_through"] < model["first_evaluation"] <= model["last_evaluation"]):
            raise ValueError("Niche model lookahead detected")
        if not (len(model["centers"]) == len(model["radii"]) == 13):
            raise ValueError("Niche model incomplete")
    ids = manifest["ids"]
    distances = pd.read_parquet(manifest["distance_file"])
    distances["date"] = pd.to_datetime(distances.date).dt.strftime("%Y-%m-%d")
    if distances.duplicated(["date","ticker"]).any():
        raise ValueError("Duplicate PIT niche distance")
    if not {"date","ticker",*ids}.issubset(distances.columns):
        raise ValueError("Missing PIT niche columns")
    if frame.date.min() < manifest["first_evaluation"]:
        raise ValueError("Evaluation predates first chronological niche model")
    multi_niche = {
        (day,ticker): tuple(float(v) for v in vals)
        for (day,ticker),vals in zip(
            distances[["date","ticker"]].itertuples(index=False,name=None),
            distances[ids].to_numpy())
    }
    # Rows lacking sufficient historical feature warmup have no niche;
    # do not fabricate a retrospective niche assignment.
    missing_niche = set(zip(frame.date, frame.ticker)) - set(multi_niche)
    if missing_niche:
        print(f'NON_NICHE_WARMUP_ROWS {len(missing_niche)}', flush=True)
    previous,resolved={},{}
    for day,ticker in sorted(set(zip(frame.date,frame.ticker))):
        controller,active=(controlling_niche(multi_niche[(day,ticker)], [1.0]*13, ids, previous.get(ticker)) if (day,ticker) in multi_niche else (None, ()))
        previous[ticker]=controller
        resolved[(day,ticker)]=(controller,active)
    state = read_defense_state(tape_path)
    defense = {day: flags['defensive'] for day, flags in state.items()}
    policy = json.loads(Path(policy_path).read_text())
    membership = {(str(d)[:10], t): bool(v) for d, t, v in policy["membership"]}
    blocked = {t: set(map(lambda d: str(d)[:10], days)) for t, days in policy["blocked"].items()}
    veto = {str(d)[:10]: bool(v) for d, v in policy["risk_veto"].items()}
    sessions = []
    for day, group in frame.groupby("date", sort=True):
        if day not in veto:
            raise ValueError("Missing risk veto for " + day)
        for ticker in group.ticker:
            if (day, ticker) not in membership:
                raise ValueError("Missing PIT membership for " + day + " " + ticker)
        if day not in defense:
            raise ValueError("Missing defense decision for " + day)
        bars = {}
        for row in group.itertuples(index=False):
            bars[row.ticker] = {"eligible": membership[(day, row.ticker)] and day not in blocked.get(row.ticker, set()) and veto[day], "open": float(row.open), "close": float(row.close), "low": float(row.low),
                                "dividend": float(row.dividends), "split": float(row.stock_splits), "sector": str(row.sector_name),
                                "features": {col: float(getattr(row, col)) for col in COLUMNS},
                                "controlling_niche": resolved[(day, row.ticker)][0],
                                "niche_distance": None,
                                "active_niches": resolved[(day, row.ticker)][1]}
        sessions.append((day, bars, defense[day]))
    if len(sessions) < 4000:
        raise ValueError("Unexpectedly short DEV79 history")
    return sessions

def init_worker(data_path, tape_path, policy_path, selected_tickers=None):
    global SESSIONS, GUARDS, FOLD_WINDOWS, FOLD_CACHE
    SESSIONS = load_sessions(data_path, tape_path, policy_path, selected_tickers)
    GUARDS = None  # Existing GA6 policy has no certification metadata; never invent it.
    FOLD_WINDOWS = expanding_walk_forward()
    assert_nonoverlapping_forward(FOLD_WINDOWS)
    FOLD_CACHE = {}

def passes(g, bar):
    a = bar["features"][g.feature_a] >= (g.threshold_a + 1) / 2
    b = bar["features"][g.feature_b] >= (g.threshold_b + 1) / 2
    return (a and b) if g.operator == "AND" else (a or b)

def evaluate(item):
    group, g, stock_folds = item
    if SESSIONS is None or FOLD_WINDOWS is None:
        raise RuntimeError("Worker data not initialized")
    def niche_passes(genome, bar):
        controller = bar.get("controlling_niche") or "NON_NICHE"
        return (group == "NON_NICHE" or controller == group) and passes(genome, bar)
    train_results=[]
    # Discovery uses only training windows across all three stock folds.
    # Forward windows are reserved for frozen-cohort promotion, not breeding.
    discovery_epochs,_=partition(FOLD_WINDOWS)
    for start,end in discovery_epochs:
        for fold_name, stock_fold in stock_folds.items():
            key=(start,end,fold_name,tuple(stock_fold))
            if key not in FOLD_CACHE:
                raw=(row for row in SESSIONS if start<=row[0]<end)
                FOLD_CACHE[key]=rank_filtered_sessions(raw,stock_fold,("ga4_return_126_percentile__v1", "ga4_return_252_percentile__v1"))
            subset=FOLD_CACHE[key]
            if len(subset)>1:
                metrics,_=replay_requests(g,subset,niche_passes)
                train_results.append(metrics)
    if not train_results:
        raise RuntimeError('No training folds available')
    # Pool non-overlapping discovery epochs by trade count; sparse folds are
    # coverage diagnostics, not fabricated losing trades.
    out=dict(train_results[-1])
    n=sum(x['trades'] for x in train_results)
    total=sum(x['r_sum'] for x in train_results)
    sq=sum(x['r_sumsq'] for x in train_results)
    mean=total/n if n else 0.
    variance=max(0.,(sq-total*total/n)/(n-1)) if n>1 else 0.
    effective=max(1.,n/2.)
    out['ev_r']=mean
    out['conservative_ev_r']=mean-1.96*sqrt(variance/effective) if n>1 else -1.
    out['mae_stop_ratio']=max((x['mae_stop_ratio'] for x in train_results if x['trades']>=5),default=0.)
    out['trades']=n
    out['active_folds']=sum(x['trades']>0 for x in train_results)
    out['total_folds']=len(train_results)
    out['fold_ev_spread']=max((x['ev_r'] for x in train_results if x['trades']>=5),default=0.)-min((x['ev_r'] for x in train_results if x['trades']>=5),default=0.)
    out['entry_signature']=sorted(set(sum((x['entry_signature'] for x in train_results),[])))
    out['training_windows']=len(train_results)
    out['training_epoch_policy']='nonoverlapping_epochs_no_duplicate_history'
    out['stock_fold_count']=len(stock_folds)
    return out

def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def run(args):
    from ga7.design_gate import certify
    if not args.exploratory:
        certify(Path(__file__).resolve().parent.parent / 'GA7_DESIGN_GATE.json')
    else:
        print('EXPLORATORY_ONLY_UNCERTIFIED_DEV79_NO_FORWARD_VALIDATION',flush=True)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    data_hash = file_hash(args.data)
    tape_hash = file_hash(args.tape)
    policy_hash = file_hash(args.policy)
    selection = json.loads(Path(args.selection).read_text()) if args.selection else None
    selected_tickers = tuple(sorted(x["ticker"] for x in selection["tickers"])) if selection else None
    if selection and (len(selected_tickers) != 32 or len(set(selected_tickers)) != 32):
        raise ValueError("Invalid DEV32 selection")
    source_files = ("niche_controller.py", "runner.py", "engine.py", "evaluator.py", "compiled_portfolio.py", "compiled_signals.py", "market_arrays.py", "stagnation.py", "request_replay.py", "proposals.py", "shadow_ledger.py", "defense_contract.py", "chronological_partition.py", "fold_features.py", "portfolio_priority.py", "trade_accounting.py")
    source_digest = hashlib.sha256("".join(file_hash(Path(__file__).with_name(name)) for name in source_files).encode()).hexdigest()
    niche_manifest = json.loads(Path("/opt/mts/ga7-deploy/ga7_unbounded/niche_pit_manifest.json").read_text())
    groups = niche_population_groups(niche_manifest["ids"])
    niche_hashes = {key:file_hash(niche_manifest[key]) for key in ("model_file","distance_file")}
    fold_plan=json.loads(Path("GA7_FOLD_PLAN_DRAFT.json").read_text())
    if fold_plan.get("status") != "PLAN_ONLY_NOT_WIRED_TO_EVALUATOR":
        raise ValueError("Unexpected fold plan version")
    stock_folds=fold_plan["stock_folds"]
    if len(set(sum(stock_folds.values(),[])))!=79:
        raise ValueError("DEV79 fold membership mismatch")
    config = {"data_sha256": data_hash, "tape_sha256": tape_hash, "policy_sha256": policy_hash, "runner_sha256": source_digest, "exploratory": args.exploratory, "niche_hashes": niche_hashes, "groups": groups, "fold_sha256":file_hash("GA7_FOLD_PLAN_DRAFT.json"), "fold_policy":"fixed_2019_cutoff_no_forward_breeding", "population": args.population, "seed": args.seed, "selection_sha256": file_hash(args.selection) if args.selection else None, "patience": args.patience}
    checkpoint = output / "checkpoint.json"
    cache_file = output / "evaluation_cache.jsonl"
    cache = {}
    if cache_file.exists():
        lines = cache_file.read_text().splitlines()
        for index, line in enumerate(lines):
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                if index != len(lines) - 1:
                    raise
                continue
            if item["config"] == config:
                cache[(item["group"],item["id"])] = item["metrics"]
    rng = random.Random(args.seed)
    generation = 0
    frontier = {group:[] for group in groups}
    stagnant = {group:0 for group in groups}
    population = {group: [random_genome(rng, FEATURES, FAMILIES[i % len(FAMILIES)]) for i in range(args.population)] for group in groups}
    if checkpoint.exists():
        saved = json.loads(checkpoint.read_text())
        if saved["config"] != config:
            raise ValueError("Checkpoint data/configuration mismatch")
        generation = saved["generation"]
        frontier = {group:[tuple(x) for x in saved.get("frontier",{}).get(group,[])] for group in groups}
        stagnant = {group:saved.get("stagnant",{}).get(group,0) for group in groups}
        population = {group:[Genome(**g) for g in saved["population"][group]] for group in groups}
        rng.setstate(pickle.loads(base64.b64decode(saved["rng_state"])))
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init_worker, initargs=(args.data, args.tape, args.policy, selected_tickers)) as pool:
        while generation < args.generations:
            started = time.monotonic()
            pending = {(group,g.identity()):(group,g,stock_folds) for group in groups for g in population[group] if (group,g.identity()) not in cache}
            fresh = list(pool.map(evaluate, pending.values(), chunksize=4))
            with cache_file.open("a") as stream:
                for ((group, identity), _), metrics in zip(pending.items(), fresh):
                    stream.write(json.dumps({"config":config,"group":group,"id":identity,"metrics":metrics})+"\n")
                    cache[(group,identity)] = metrics
                stream.flush()
                os.fsync(stream.fileno())
            scored_by_group = {}
            improved_groups = []
            for group in groups:
                scored = add_behavioral_diversity([(g,cache[(group,g.identity())]) for g in population[group]])
                scored_by_group[group] = scored
                previous_frontier = frontier.get(group, [])
                new_frontier, group_stagnant, improved = update_stagnation([m for _,m in scored], previous_frontier, stagnant.get(group,0))
                frontier[group] = new_frontier
                stagnant[group] = group_stagnant
                if improved: improved_groups.append(group)
            generation_path = output / ("generation_%04d.jsonl" % (generation + 1))
            generation_tmp = generation_path.with_suffix(".tmp")
            with generation_tmp.open("w") as stream:
                for group, scored in scored_by_group.items():
                    for g,metrics in scored:
                        stream.write(json.dumps({"generation":generation+1,"group":group,"genome":asdict(g),"metrics":metrics})+"\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(generation_tmp,generation_path)
            generation += 1
            population = {group:next_population(scored_by_group[group],rng,FEATURES,args.population) for group in groups}
            saved = {"config": config, "generation": generation, "population": {group:[asdict(g) for g in population[group]] for group in groups},
                     "rng_state": base64.b64encode(pickle.dumps(rng.getstate())).decode(),
                     "frontier": frontier, "stagnant": stagnant}
            tmp = checkpoint.with_suffix(".tmp")
            with tmp.open("w") as stream:
                stream.write(json.dumps(saved))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, checkpoint)
            print(json.dumps({"generation":generation,"groups":len(groups),"evaluated":sum(map(len,scored_by_group.values())),"new_evaluations":len(pending),"elapsed_seconds":time.monotonic()-started,"improved_groups":improved_groups,"stagnation_by_group":stagnant}),flush=True)
            if all(value >= args.patience for value in stagnant.values()):
                print(json.dumps({"stopped":"ALL_GROUPS_PARETO_STAGNATION","generation":generation}),flush=True)
                break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exploratory", action="store_true", help="Uncertified DEV79 discovery; does not certify validation or deployment")
    parser.add_argument("--data", required=True)
    parser.add_argument("--tape", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--selection", help="DEV32 selection JSON")
    parser.add_argument("--generations", type=int, default=1000)
    parser.add_argument("--population", type=int, default=300)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=70079)
    parser.add_argument("--patience", type=int, default=100)
    args = parser.parse_args()
    if args.generations < 1 or args.population < 16 or args.workers < 1 or args.patience < 1:
        parser.error("Invalid evolution budget")
    run(args)

if __name__ == "__main__":
    main()
