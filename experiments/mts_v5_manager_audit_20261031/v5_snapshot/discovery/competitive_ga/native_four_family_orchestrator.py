"""Causal four-family native producer orchestration for research replays.
The caller supplies real archived genomes, per-session panels, and executed-fill state.
No synthetic surrogate chromosome signals are manufactured here.
"""
from .ga4_native_daily_producer import produce as ga4
from .horizons_native_daily_producer import produce as horizons
from .ga7_native_daily_producer import produce as ga7
from .ga6_native_daily_producer import produce as ga6
from .native_signal_contract import normalize_proposals


def produce(date, *, trained_through, source_hash, snapshot_hash,
            ga4_specs=(), horizons_specs=(), ga6_producer=None,
            ga7_specs=(), ga4_compiler=None, horizons_panel=None,
            ga7_bars=None, held=None, defensive=False, ga6_specs=(),
            ga6_rows=None, session=None, held_by_owner=None):
    held=held or {}
    def owned(family, cid):
        if held_by_owner is not None:
            return held_by_owner.get((family,cid), {})
        return {t:s for t,s in held.items() if s["owner"] == (family,cid)}
    result=[]
    for spec in ga4_specs:
        if ga4_compiler is None:raise ValueError('GA4 compiler required')
        result.extend(ga4(ga4_compiler,spec['chromosomes'],decision_date=date,
            chromosome_id=spec['id'],trained_through=trained_through,
            source_hash=source_hash,snapshot_hash=snapshot_hash,
            target_weight=spec.get('target_weight',.10),held=owned('GA4',spec['id']),
            exit_producer=spec.get('exit_producer')))
    for spec in horizons_specs:
        if horizons_panel is None:raise ValueError('Horizons causal panel required')
        result.extend(horizons(spec['genome'],horizons_panel,
            previous={t:s['weight'] for t,s in owned('HORIZONS',spec['id']).items()},
            prior_returns=spec.get('prior_returns'),
            decision_date=date,chromosome_id=spec['id'],
            trained_through=trained_through,source_hash=source_hash,
            snapshot_hash=snapshot_hash))
    for spec in ga6_specs:
        if ga6_rows is None or session is None:
            raise ValueError('GA6 causal rows and session required')
        result.extend(ga6(spec['candidate'], ga6_rows, decision_date=date,
            session=session, chromosome_id=spec['id'], trained_through=trained_through,
            source_hash=source_hash, snapshot_hash=snapshot_hash,
            held=owned('GA6',spec['id']), defensive=defensive))
    if ga6_producer is not None:
        result.extend(ga6_producer(date,held,defensive))
    for spec in ga7_specs:
        if ga7_bars is None:raise ValueError('GA7 causal feature bars required')
        ga7_held=owned('GA7',spec['id'])
        result.extend(ga7(spec['genome'],ga7_bars,decision_date=date,
            trained_through=trained_through,source_hash=source_hash,
            snapshot_hash=snapshot_hash,chromosome_id=spec['id'],
            defensive=defensive,held=ga7_held,niche_group=spec.get('niche_group','NON_NICHE'),
            signal_evaluator=spec.get('signal_evaluator'),strength_evaluator=spec.get('strength_evaluator')))
    normalized=normalize_proposals(result,date)
    # A chromosome must not give conflicting instructions for one symbol.
    keys=[(p.family,p.chromosome_id,p.ticker) for p in normalized]
    if len(set(keys))!=len(keys):raise ValueError('duplicate native family/chromosome/ticker proposal')
    return normalized
