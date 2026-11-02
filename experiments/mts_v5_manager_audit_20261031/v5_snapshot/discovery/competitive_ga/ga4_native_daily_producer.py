"""Research GA4 native boolean chromosomes -> dated manager proposals.
Uses archived GA4 compiler on ONE contemporaneous cross-sectional session.
Never fits quantile thresholds on later sessions. Exits are NOT inferred from
entry predicates: native GA4 exit/horizon producer is still required.
"""
from .native_signal_contract import NativeProposal


def produce(compiler,chromosomes,*,decision_date,chromosome_id,
            trained_through,source_hash,snapshot_hash,target_weight=.10,held=None,exit_producer=None):
    held=held or {}
    if held and exit_producer is None:
        raise ValueError('GA4 native held-position exit policy unavailable; horizon is not an exit')
    frame=compiler.frame
    if len(frame)<2:raise ValueError('cross-sectional session required')
    if 'date' not in frame or 'ticker' not in frame:
        raise ValueError('dated ticker feature panel required')
    if frame['date'].astype(str).str[:10].nunique()!=1 or str(frame['date'].iloc[0])[:10]!=decision_date:
        raise ValueError('mixed or wrong-day panel: future quantile leakage')
    if frame['ticker'].duplicated().any():raise ValueError('duplicate ticker in daily panel')
    if not 1<=len(chromosomes)<=4:raise ValueError('invalid GA4 chromosome conjunction')
    selected=None
    for family,genome in chromosomes:
        mask=compiler.compile(family,genome)
        if len(mask)!=len(frame):raise ValueError('native compiler alignment failure')
        selected=mask.copy() if selected is None else selected & mask
    result=[]
    for ticker in frame.loc[selected,'ticker']:
        if str(ticker) in held:continue
        result.append(NativeProposal(decision_date,str(ticker),'GA4',chromosome_id,
            'ENTER',target_weight,1.,'native_horizon_score',source_hash,
            snapshot_hash,trained_through))
    if held:
        exits=list(exit_producer(decision_date,held))
        if {p.ticker for p in exits} != set(held) or len(exits)!=len(held):
            raise ValueError('GA4 exit policy must decide every held ticker exactly once')
        for p in exits:
            if (p.family!='GA4' or p.chromosome_id!=chromosome_id or
                p.decision_date!=decision_date or p.action=='ENTER'):
                raise ValueError('invalid native GA4 held-position decision')
        result.extend(exits)
    return result
