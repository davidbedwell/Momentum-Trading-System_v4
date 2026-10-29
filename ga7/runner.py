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

from ga7.engine import FAMILIES, Genome, next_population, random_genome
from ga7.request_replay import replay_requests
from ga7.guardrails import Guardrails
from ga7.stagnation import update_stagnation

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
    frame = frame[(frame.date >= "2005-09-14") & (frame.date <= "2026-09-14")].copy()
    if frame.ticker.nunique() != 79:
        raise ValueError("DEV79 ticker count mismatch")
    if frame.duplicated(["date", "ticker"]).any():
        raise ValueError("Duplicate date/ticker bars")
    if selected_tickers is not None:
        if not set(selected_tickers).issubset(set(frame.ticker)):
            raise ValueError("DEV32 contains tickers missing from DEV79")
        frame = frame[frame.ticker.isin(selected_tickers)].copy()
    for col in COLUMNS:
        frame[col] = frame.groupby("date")[col].rank(pct=True)
    state = pd.read_csv(tape_path)
    state["date"] = state.date.astype(str)
    if state.date.duplicated().any() or not {"date", "defensive"}.issubset(state.columns):
        raise ValueError("Invalid defense tape")
    defense = dict(zip(state.date, state.defensive.astype(bool)))
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
                                "features": {col: float(getattr(row, col)) for col in COLUMNS}}
        sessions.append((day, bars, defense[day]))
    if len(sessions) < 5000:
        raise ValueError("Unexpectedly short DEV79 history")
    return sessions

def init_worker(data_path, tape_path, policy_path, selected_tickers=None):
    global SESSIONS, GUARDS
    SESSIONS = load_sessions(data_path, tape_path, policy_path, selected_tickers)
    GUARDS = None  # Existing GA6 policy has no certification metadata; never invent it.

def passes(g, bar):
    a = bar["features"][g.feature_a] >= (g.threshold_a + 1) / 2
    b = bar["features"][g.feature_b] >= (g.threshold_b + 1) / 2
    return (a and b) if g.operator == "AND" else (a or b)

def evaluate(g):
    if SESSIONS is None:
        raise RuntimeError("Worker data not initialized")
    result, _ledger = replay_requests(g, SESSIONS, passes)
    return result

def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def run(args):
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    data_hash = file_hash(args.data)
    tape_hash = file_hash(args.tape)
    policy_hash = file_hash(args.policy)
    selection = json.loads(Path(args.selection).read_text()) if args.selection else None
    selected_tickers = tuple(sorted(x["ticker"] for x in selection["tickers"])) if selection else None
    if selection and (len(selected_tickers) != 32 or len(set(selected_tickers)) != 32):
        raise ValueError("Invalid DEV32 selection")
    source_files = ("runner.py", "engine.py", "evaluator.py", "compiled_portfolio.py", "compiled_signals.py", "market_arrays.py", "stagnation.py", "request_replay.py", "proposals.py", "shadow_ledger.py")
    source_digest = hashlib.sha256("".join(file_hash(Path(__file__).with_name(name)) for name in source_files).encode()).hexdigest()
    config = {"data_sha256": data_hash, "tape_sha256": tape_hash, "policy_sha256": policy_hash, "runner_sha256": source_digest, "population": args.population, "seed": args.seed, "selection_sha256": file_hash(args.selection) if args.selection else None, "patience": args.patience}
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
                cache[item["id"]] = item["metrics"]
    rng = random.Random(args.seed)
    generation = 0
    frontier = []
    stagnant = 0
    population = [random_genome(rng, FEATURES, FAMILIES[i % len(FAMILIES)]) for i in range(args.population)]
    if checkpoint.exists():
        saved = json.loads(checkpoint.read_text())
        if saved["config"] != config:
            raise ValueError("Checkpoint data/configuration mismatch")
        generation = saved["generation"]
        frontier = [tuple(x) for x in saved.get("frontier", [])]
        stagnant = saved.get("stagnant", 0)
        population = [Genome(**g) for g in saved["population"]]
        rng.setstate(pickle.loads(base64.b64decode(saved["rng_state"])))
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init_worker, initargs=(args.data, args.tape, args.policy, selected_tickers)) as pool:
        while generation < args.generations:
            started = time.monotonic()
            pending = {g.identity(): g for g in population if g.identity() not in cache}
            fresh = list(pool.map(evaluate, pending.values(), chunksize=1))
            with cache_file.open("a") as stream:
                for (identity, _), metrics in zip(pending.items(), fresh):
                    stream.write(json.dumps({"config": config, "id": identity, "metrics": metrics}) + "\n")
                    cache[identity] = metrics
                stream.flush()
                os.fsync(stream.fileno())
            results = [cache[g.identity()] for g in population]
            scored = list(zip(population, results))
            frontier, stagnant, improved = update_stagnation(results, frontier, stagnant)
            generation_path = output / ("generation_%04d.jsonl" % (generation + 1))
            generation_tmp = generation_path.with_suffix(".tmp")
            with generation_tmp.open("w") as stream:
                for g, metrics in scored:
                    stream.write(json.dumps({"generation": generation + 1, "genome": asdict(g), "metrics": metrics}) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(generation_tmp, generation_path)
            generation += 1
            population = next_population(scored, rng, FEATURES, args.population)
            saved = {"config": config, "generation": generation, "population": [asdict(g) for g in population],
                     "rng_state": base64.b64encode(pickle.dumps(rng.getstate())).decode(),
                     "frontier": frontier, "stagnant": stagnant}
            tmp = checkpoint.with_suffix(".tmp")
            with tmp.open("w") as stream:
                stream.write(json.dumps(saved))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, checkpoint)
            print(json.dumps({"generation": generation, "evaluated": len(scored),
                              "new_evaluations": len(pending), "cache_hits": len(population)-len(pending),
                              "elapsed_seconds": time.monotonic()-started,
                              "best_cagr": max(x["cagr"] for x in results),
                              "feasible_frontier_improved": improved,
                              "stagnant_generations": stagnant}), flush=True)
            if stagnant >= args.patience:
                print(json.dumps({"stopped": "PARETO_STAGNATION", "generation": generation,
                                  "patience": args.patience}), flush=True)
                break

def main():
    parser = argparse.ArgumentParser()
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
