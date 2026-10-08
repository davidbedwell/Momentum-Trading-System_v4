"""GA4 candidate evaluation adapter: chromosome conjunctions, contextual slices, 63-day evidence.

The evolutionary engine supplies candidate chromosomes. This adapter does not
optimize global CAGR/MDD and does not touch validation partitions.
"""
from __future__ import annotations

import numpy as np

from .ga4_relationship_catalog import relationship_record
from .ga4_horizon_contract import FORWARD_HORIZONS
from .stage2_evaluator_v3 import evaluate_curve
from .ga4_discovery_evidence_policy import annotate_discovery
from .ga4_candidate_context_evidence import summarize_candidate_context


def evaluate_conditional_candidate(*, compiler, chromosomes, context_mask, context,
                                   paths, costs, cluster_ids, fold, data_provenance,
                                   side="LONG", min_raw_n=200, min_effective_n=20,
                                   stage1_context_frame=None, stage1_reference=None):
    """Evaluate 1–4 (family, genome) chromosomes under a causal context mask.

    Each chromosome's boolean signal is AND-combined. The context mask must
    be computed solely from contemporaneously available predictors.
    The caller must supply a fold-isolated compiler, paths and clusters.
    """
    if not 1 <= len(chromosomes) <= 4:
        raise ValueError("One to four chromosomes required")
    rows = paths.endpoint_return.shape[0]
    mask = np.asarray(context_mask)
    if mask.dtype != np.dtype(bool) or mask.shape != (rows,):
        raise ValueError("Context mask must be a boolean vector aligned with outcome rows")
    if len(cluster_ids) != rows or len(compiler.frame) != rows:
        raise ValueError("Fold/compiler/outcome alignment mismatch")
    selected = mask.copy()
    chromosome_ids = []
    for family, genome in chromosomes:
        chromosome_ids.append(f"{family}:{__import__('json').dumps(genome, sort_keys=True, separators=(',', ':'), allow_nan=False)}")
        signal = np.asarray(compiler.compile(family, genome))
        if signal.dtype != np.dtype(bool) or signal.shape != (rows,):
            raise ValueError("Chromosome signal misaligned")
        selected &= signal
    if len(set(chromosome_ids)) != len(chromosome_ids):
        raise ValueError("Duplicate chromosome")
    curve = evaluate_curve(selected, paths, costs, side, np.asarray(cluster_ids),
                           min_raw_n=min_raw_n, min_effective_n=min_effective_n)
    if len(curve.points) != len(FORWARD_HORIZONS):
        raise ValueError("Incomplete GA4 horizon evidence")
    record = relationship_record(chromosomes=chromosome_ids, context=context, curve=curve,
                                 fold=fold, data_provenance=data_provenance)
    if (stage1_context_frame is None) != (stage1_reference is None):
        raise ValueError('Stage 1 frame and reference must be supplied together')
    if stage1_context_frame is not None:
        evidence=summarize_candidate_context(stage1_context_frame, selected, stage1_reference)
        record['stage1_context_reference']=evidence['reference']
        record['stage1_candidate_context']=evidence
    return annotate_discovery(record)
