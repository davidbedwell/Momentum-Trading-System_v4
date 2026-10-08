"""GA4 combination evolution callback: persist every candidate before selection."""
from .ga4_combination_evolution import evolve_combinations
from .ga4_conditional_runner import evaluate_conditional_candidate
from .ga4_catalog_store import append_record
from .stage2_evaluator_v3 import CurveEvaluation


def run_combination_discovery(*, spaces, compiler, context_mask, context,
                              paths, costs, cluster_ids, fold, data_provenance,
                              catalog_dir, seed, population_size=24, generations=5,
                              side="LONG", min_raw_n=200, min_effective_n=20):
    saved = []

    def evaluate(chromosomes):
        record = evaluate_conditional_candidate(
            compiler=compiler, chromosomes=chromosomes,
            context_mask=context_mask, context=context, paths=paths, costs=costs,
            cluster_ids=cluster_ids, fold=fold, data_provenance=data_provenance,
            side=side, min_raw_n=min_raw_n, min_effective_n=min_effective_n)
        path, created = append_record(catalog_dir, record)
        saved.append((record["candidate_id"], str(path), created))
        return CurveEvaluation(record["side"], tuple(record["daily_horizon_evidence"]),
                               tuple(record["pareto_horizons"]),
                               tuple(tuple(x) for x in record["pareto_ranges"]))

    result = evolve_combinations(spaces, evaluate, seed=seed,
                                 population_size=population_size, generations=generations)
    return {"saved": saved, "generations": result["generations"],
            "unique_evaluations": result["unique_evaluations"], "certified": False}
