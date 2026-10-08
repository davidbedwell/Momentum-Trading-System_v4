"""Resume missing SHORT evolutionary calibrations; checkpoint each case.

This is engineering evidence generation, not scientific certification.
"""
import hashlib
import json
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Core.layered_ga.stage2_recovered_source_preflight_v3 import verify_recovered_sources
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces, VectorSignalCompiler
from Core.layered_ga.stage2_data_v3 import load_path_cache
from Core.layered_ga.stage2_calibration_outcomes_v3 import plant_endpoint_outcomes, OutcomeOnlyCurveEvaluator
from Core.layered_ga.stage2_calibration_shapes_v3 import planted_profile
from Core.layered_ga.stage2_evaluator_v3 import cluster_ids_from_frame
from Core.layered_ga.stage2_nsga2_engine_v3 import evolve

CAL = ROOT / "Research/Runs/layered/stage2-opportunity-v3-20261007/calibration"
def main():
    if verify_recovered_sources()["decision"] != "PASS":
        raise RuntimeError("recovered source preflight failed")
    batch_path = CAL / "nsga2_batch_evolutionary_evidence.json"
    batch = json.loads(batch_path.read_text())
    if len(batch.get("cases", [])) != 45:
        raise RuntimeError("expected existing 45 LONG cases")
    cache = CAL.parent / "cache"
    frame = pd.read_parquet(cache / "dev117_predictors_v3.parquet")
    paths, costs = load_path_cache(cache)
    compiler = VectorSignalCompiler(frame)
    clusters = cluster_ids_from_frame(frame)
    targets = json.loads((CAL / "target_manifest.json").read_text())["targets"]
    spaces = stage2_search_spaces()
    output = CAL / "ga4_short_evolutionary_evidence.json"
    record = json.loads(output.read_text()) if output.exists() else {"status": "RUNNING", "cases": []}
    done = {(c["family"], c["shape"], c["effect"]) for c in record["cases"]}
    for case in batch["cases"]:
        family, shape, effect = case["family"], case["shape"], case["effect"]
        if (family, shape, effect) in done:
            continue
        target = compiler.compile(family, targets[family]["genome"])
        planted = plant_endpoint_outcomes(paths, target, planted_profile(shape), effect)
        evaluator = OutcomeOnlyCurveEvaluator(compiler, planted.paths, costs, clusters)
        seed = int.from_bytes(hashlib.sha256(f"{family}|{shape}|{effect}|v3-nsga2|SHORT".encode()).digest()[:4], "big")
        run = evolve(spaces[family], lambda genome: evaluator.evaluate(family, genome, "SHORT"),
                     seed=seed, population_size=8, generations=2)
        record["cases"].append({"family": family, "shape": shape, "effect": effect,
                                "side": "SHORT", "seed": seed, "generations": run["generations"],
                                "unique_evaluations": run["unique_evaluations"],
                                "heldout_selection_adjusted_validation": None})
        tmp = output.with_suffix(".tmp")
        tmp.write_text(json.dumps(record, allow_nan=True))
        tmp.replace(output)
        print("SHORT_CASE_COMPLETE", len(record["cases"]), flush=True)
    record["status"] = "ENGINEERING_BATCH_COMPLETE_UNCERTIFIED"
    output.write_text(json.dumps(record, allow_nan=True))
if __name__ == "__main__":
    main()
