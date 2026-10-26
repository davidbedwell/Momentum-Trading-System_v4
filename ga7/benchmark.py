"""Compiled GA7 research benchmark. Does not certify GA6 parity.

python -m ga7.benchmark --data ... --policy ... --tape ... --output ...
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import random
import time
import numpy as np
import pandas as pd
from ga7.runner import FEATURES, COLUMNS
from ga7.engine import FAMILIES, random_genome
from ga7.market_arrays import prepare
from ga7.compiled_signals import scan_signals
from ga7.compiled_portfolio import replay

def benchmark(data, policy_path, tape, output, count=32, seed=70079):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    df = pd.read_parquet(data)
    policy = json.loads(Path(policy_path).read_text())
    state = pd.read_csv(tape)
    if state.date.duplicated().any():
        raise ValueError("Duplicate defense dates")
    defense = dict(zip(state.date.astype(str), state.defensive.astype(bool)))
    arrays = prepare(df, COLUMNS, policy, defense)
    preparation_seconds = time.perf_counter() - start
    split_events = int(np.count_nonzero(arrays.splits[arrays.present]))
    if split_events:
        report = {"status": "BLOCKED_UNCERTIFIED_SPLIT_CONVENTION",
                  "split_events": split_events,
                  "stock_count": len(arrays.tickers),
                  "sessions": len(arrays.dates),
                  "preparation_seconds": preparation_seconds,
                  "evaluations_completed": 0}
        path = output / "benchmark.json"
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(report, indent=2))
        temp.replace(path)
        return report
    rng = random.Random(seed)
    genomes = [random_genome(rng, FEATURES, FAMILIES[i % 8]) for i in range(count)]
    first = time.perf_counter()
    results = []
    for genome in genomes:
        ia = COLUMNS.index(genome.feature_a)
        ib = COLUMNS.index(genome.feature_b)
        signals = scan_signals(arrays.features, arrays.present, arrays.eligible,
            arrays.defense, ia, ib, (genome.threshold_a+1)/2,
            (genome.threshold_b+1)/2, genome.operator == "AND")
        metrics = replay(arrays.opens, arrays.closes, arrays.lows,
            arrays.dividends, arrays.splits, arrays.present, arrays.eligible,
            arrays.sector, arrays.defense, signals, genome.hold_sessions,
            genome.entry_pct, genome.capacity)
        results.append({"genome": asdict(genome), "final_nav": float(metrics[0]),
            "cagr": float(metrics[1]), "mdd": float(metrics[2]),
            "trades": int(metrics[6])})
    elapsed = time.perf_counter() - first
    manifest = {"status": "UNCERTIFIED_COMPILED_RESEARCH_BENCHMARK",
        "stock_count": len(arrays.tickers), "sessions": len(arrays.dates),
        "genomes": count, "preparation_seconds": preparation_seconds,
        "evaluation_seconds_including_jit": elapsed,
        "evaluations_per_second_including_jit": count / max(elapsed, 1e-9),
        "estimated_seconds_for_300000_serial_including_jit_rate": 300000 * elapsed / count,
        "results": results}
    path = output / "benchmark.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(manifest, indent=2, allow_nan=False))
    temp.replace(path)
    return manifest

def main():
    p = argparse.ArgumentParser()
    for name in ("data", "policy", "tape", "output"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--count", type=int, default=32)
    a = p.parse_args()
    if a.count < 1:
        p.error("count must be positive")
    report = benchmark(a.data, a.policy, a.tape, a.output, a.count)
    print(json.dumps({k:v for k,v in report.items() if k!="results"}, indent=2))

if __name__ == "__main__":
    main()
