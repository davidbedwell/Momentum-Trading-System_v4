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
import pandas as pd

from ga7.engine import FAMILIES, Genome, next_population, random_genome
from ga7.evaluator import Portfolio, Policy

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

def load_sessions(data_path, tape_path):
    frame = pd.read_parquet(data_path)
    required = {"date", "ticker", "open", "close", "low", *COLUMNS}
    if not required.issubset(frame.columns):
        raise ValueError("Missing data columns: " + str(sorted(required - set(frame.columns))))
    frame["date"] = pd.to_datetime(frame.date).dt.strftime("%Y-%m-%d")
    frame = frame[(frame.date >= "2005-09-14") & (frame.date <= "2026-09-14")].copy()
    if frame.ticker.nunique() != 79:
        raise ValueError("DEV79 ticker count mismatch")
    if frame.duplicated(["date", "ticker"]).any():
        raise ValueError("Duplicate date/ticker bars")
    for col in COLUMNS:
        frame[col] = frame.groupby("date")[col].rank(pct=True)
    state = pd.read_csv(tape_path)
    state["date"] = state.date.astype(str)
    if state.date.duplicated().any() or not {"date", "defensive"}.issubset(state.columns):
        raise ValueError("Invalid defense tape")
    defense = dict(zip(state.date, state.defensive.astype(bool)))
    sessions = []
    for day, group in frame.groupby("date", sort=True):
        if day not in defense:
            raise ValueError("Missing defense decision for " + day)
        bars = {}
        for row in group.itertuples(index=False):
            bars[row.ticker] = {"open": float(row.open), "close": float(row.close), "low": float(row.low),
                                "features": {col: float(getattr(row, col)) for col in COLUMNS}}
        sessions.append((day, bars, defense[day]))
    if len(sessions) < 5000:
        raise ValueError("Unexpectedly short DEV79 history")
    return sessions

def init_worker(data_path, tape_path):
    global SESSIONS
    SESSIONS = load_sessions(data_path, tape_path)

def passes(g, bar):
    a = bar["features"][g.feature_a] >= (g.threshold_a + 1) / 2
    b = bar["features"][g.feature_b] >= (g.threshold_b + 1) / 2
    return (a and b) if g.operator == "AND" else (a or b)

def evaluate(g):
    if SESSIONS is None:
        raise RuntimeError("Worker data not initialized")
    portfolio = Portfolio(Policy(max_positions=g.capacity))
    previous = None
    last_date = None
    last_closes = None
    for i, (day, bars, defensive) in enumerate(SESSIONS):
        portfolio.session = i
        portfolio.accrue_cash()
        opens = {t: b["open"] for t, b in bars.items()}
        closes = {t: b["close"] for t, b in bars.items()}
        lows = {t: b["low"] for t, b in bars.items()}
        if set(portfolio.positions) - set(opens):
            raise ValueError("Missing held security open; no silent delisting")
        if previous is not None:
            prior_day, prior_bars, prior_defensive = previous
            for t in list(portfolio.positions):
                p = portfolio.positions[t]
                age = i - p["session"]
                price = opens[t]
                pnl = price / p["entry"] - 1
                decay = t in prior_bars and not passes(g, prior_bars[t])
                should_exit = prior_defensive or defensive or age >= min(g.hold_sessions, 40) or pnl <= -g.stop_pct
                should_exit |= g.exit_rule == "signal_decay" and decay
                should_exit |= g.exit_rule == "reversal" and pnl < -.005
                should_exit |= g.exit_rule == "volatility" and abs(pnl) > .04
                if should_exit:
                    portfolio.sell(t, price)
            if not defensive and not prior_defensive:
                candidates = [(sum(prior_bars[t]["features"][x] for x in (g.feature_a, g.feature_b)), t)
                              for t in prior_bars if t in bars and t not in portfolio.positions and passes(g, prior_bars[t])]
                for _, t in sorted(candidates, reverse=True):
                    if len(portfolio.positions) >= g.capacity:
                        break
                    portfolio.buy(t, opens[t], g.entry_pct, opens)
        for t in portfolio.positions:
            portfolio.update_low(t, lows[t])
        if i < len(SESSIONS) - 1:
            portfolio.mark(day, closes)
        previous = (day, bars, defensive)
        last_date, last_closes = day, closes
    if last_date is None:
        raise ValueError("No sessions")
    result = portfolio.finish(last_date, last_closes)
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
    config = {"data_sha256": data_hash, "tape_sha256": tape_hash, "population": args.population, "seed": args.seed}
    checkpoint = output / "checkpoint.json"
    rng = random.Random(args.seed)
    generation = 0
    population = [random_genome(rng, FEATURES, FAMILIES[i % len(FAMILIES)]) for i in range(args.population)]
    if checkpoint.exists():
        saved = json.loads(checkpoint.read_text())
        if saved["config"] != config:
            raise ValueError("Checkpoint data/configuration mismatch")
        generation = saved["generation"]
        population = [Genome(**g) for g in saved["population"]]
        rng.setstate(pickle.loads(base64.b64decode(saved["rng_state"])))
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init_worker, initargs=(args.data, args.tape)) as pool:
        while generation < args.generations:
            results = list(pool.map(evaluate, population, chunksize=1))
            scored = list(zip(population, results))
            with (output / "evaluations.jsonl").open("a") as stream:
                for g, metrics in scored:
                    stream.write(json.dumps({"generation": generation + 1, "genome": asdict(g), "metrics": metrics}) + "\n")
            generation += 1
            population = next_population(scored, rng, FEATURES, args.population)
            saved = {"config": config, "generation": generation, "population": [asdict(g) for g in population],
                     "rng_state": base64.b64encode(pickle.dumps(rng.getstate())).decode()}
            tmp = checkpoint.with_suffix(".tmp")
            tmp.write_text(json.dumps(saved))
            os.replace(tmp, checkpoint)
            print(json.dumps({"generation": generation, "evaluated": len(scored),
                              "best_cagr": max(x["cagr"] for x in results)}), flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--tape", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--generations", type=int, default=1000)
    parser.add_argument("--population", type=int, default=300)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=70079)
    args = parser.parse_args()
    if args.generations < 1 or args.population < 16 or args.workers < 1:
        parser.error("Invalid evolution budget")
    run(args)

if __name__ == "__main__":
    main()
