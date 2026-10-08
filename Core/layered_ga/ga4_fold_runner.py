"""Guarded GA4 discovery entry point. No validation partition accepted."""
from .ga4_fold_execution import build_discovery_execution
from .ga4_combination_runner import run_combination_discovery

def run_fold_discovery(*, stock_local, raw, membership, spaces, context_factory,
                       catalog_dir, seed, population_size=24, generations=5):
    predictors, paths, costs, clusters, scope = build_discovery_execution(stock_local, raw, membership)
    from .stage2_compiler_v3 import VectorSignalCompiler
    compiler = VectorSignalCompiler(predictors)
    context_mask, context = context_factory(predictors)
    return run_combination_discovery(
        spaces=spaces, compiler=compiler, context_mask=context_mask, context=context,
        paths=paths, costs=costs, cluster_ids=clusters, fold='DEV80',
        data_provenance=scope, catalog_dir=catalog_dir, seed=seed,
        population_size=population_size, generations=generations)
