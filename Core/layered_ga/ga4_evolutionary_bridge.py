
"""Connect surviving NSGA-II callback to GA4 evidence persistence."""
from .ga4_conditional_runner import evaluate_conditional_candidate
from .ga4_catalog_store import append_record
from .stage2_nsga2_engine_v3 import evolve
from .stage2_evaluator_v3 import CurveEvaluation


def run_family_discovery(*, space, family, compiler, context_mask, context, paths, costs, cluster_ids, fold, data_provenance, catalog_dir, seed, population_size=24, generations=5):
    saved = []
    def evaluate(genome):
        record = evaluate_conditional_candidate(compiler=compiler, chromosomes=[(family, genome)], context_mask=context_mask, context=context, paths=paths, costs=costs, cluster_ids=cluster_ids, fold=fold, data_provenance=data_provenance)
        location, created = append_record(catalog_dir, record)
        saved.append((record['candidate_id'], str(location), created))
        return CurveEvaluation(record['side'], tuple(record['daily_horizon_evidence']), tuple(record['pareto_horizons']), tuple(tuple(x) for x in record['pareto_ranges']))
    result = evolve(space, evaluate, seed=seed, population_size=population_size, generations=generations)
    return {'family': family, 'fold': fold, 'saved': saved, 'generations': result['generations'], 'unique_evaluations': result['unique_evaluations'], 'certified': False}

[executed on device: instance-e298gycb-main (a21f8a9b-b225-483b-b45f-ba34708f98ee)]