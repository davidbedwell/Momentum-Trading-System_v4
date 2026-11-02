"""Authentic Horizons cross-sectional daily decisions to manager boundary.
Caller must provide point-in-time normalized full-universe panel and lagged
returns. Research only: this does not certify external PIT provenance.
"""
from .horizons_signed_decisions import decide
from .horizons_causal_rank import evaluate
from .horizons_native_proposal_adapter import from_horizons


def produce(genome,causal_panel,*,previous=None,prior_returns=None,
            decision_date,chromosome_id,trained_through,source_hash,
            snapshot_hash,cap=.10):
    if len(causal_panel)<2:
        raise ValueError('full cross-sectional panel required')
    if not source_hash or not snapshot_hash:
        raise ValueError('missing panel provenance')
    previous=previous or {}
    # Both native transitions and raw scores use the identical panel/genome.
    transitions=decide(genome,causal_panel,previous,prior_returns,cap,
                       allow_shorts=False)
    ranked=evaluate(genome,causal_panel)
    # Exiting symbols may no longer be in the ranked universe. Preserve native
    # exit with explicit zero score (never used as calibrated opportunity EV).
    scores={t:ranked[t]['raw'] if t in ranked else 0. for t in transitions}
    proposals=from_horizons(transitions,decision_date=decision_date,
        chromosome_id=chromosome_id,trained_through=trained_through,
        source_hash=source_hash,snapshot_hash=snapshot_hash,
        native_score_by_ticker=scores)
    return proposals
