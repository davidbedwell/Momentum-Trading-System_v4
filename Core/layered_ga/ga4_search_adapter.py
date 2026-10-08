"""Adapter between existing evolutionary genome proposals and GA4 evidence storage.

This is an integration seam, not a new evolutionary algorithm or a new fitness
function. Search/selection must be frozen and audited separately.
"""
from __future__ import annotations

from .ga4_conditional_runner import evaluate_conditional_candidate
from .ga4_catalog_store import append_record


def evaluate_and_record(*, candidate, compiler, context_mask, context,
                        paths, costs, cluster_ids, fold, data_provenance,
                        catalog_dir, side="LONG", min_raw_n=200, min_effective_n=20):
    """Consume a proposal with 'chromosomes': [(family, genome), ...].

    A candidate may be proposed by the surviving G0/G2/NSGA-II machinery;
    no CAGR/MDD optimization or search selection is performed here.
    """
    if set(candidate) != {"chromosomes"}:
        raise ValueError("Expected chromosome proposal only")
    record = evaluate_conditional_candidate(
        compiler=compiler, chromosomes=candidate["chromosomes"],
        context_mask=context_mask, context=context, paths=paths, costs=costs,
        cluster_ids=cluster_ids, fold=fold, data_provenance=data_provenance,
        side=side, min_raw_n=min_raw_n, min_effective_n=min_effective_n)
    file, created = append_record(catalog_dir, record)
    return {"record": record, "file": str(file), "created": created}
