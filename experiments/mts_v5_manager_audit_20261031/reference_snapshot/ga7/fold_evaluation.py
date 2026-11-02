"""GA7 fold replay: phase-isolated sessions and fold-local feature ranks."""
from ga7.request_replay import replay_requests
from ga7.fold_features import rank_filtered_sessions


def replay_fold(genome, sessions, passes, window, tickers, phase, columns=None):
    if phase not in ('train','forward'): raise ValueError('Invalid fold phase')
    start,end=(window['train_start'],window['train_end_exclusive']) if phase=='train' else (window['test_start'],window['test_end_exclusive'])
    raw=(row for row in sessions if start<=row[0]<end)
    if columns is None:
        raise ValueError('Fold feature columns required for isolated ranking')
    subset=rank_filtered_sessions(raw,tickers,columns)
    if len(subset)<2: raise ValueError('Insufficient fold sessions')
    result,_=replay_requests(genome,subset,passes)
    return result


def summarize_forward(results, min_trades=5):
    """Descriptive forward evidence; do not treat repeated tests as independent."""
    if not results: raise ValueError('Missing forward results')
    total=sum(r['trades'] for r in results)
    valid=[r for r in results if r['trades']>=min_trades]
    return dict(windows=len(results),valid_windows=len(valid),trades=total,
                worst_conservative_ev_r=min(r['conservative_ev_r'] for r in results),
                worst_mae_stop_p90=max(r['mae_stop_ratio'] for r in results),
                positive_windows=sum(r['conservative_ev_r']>0 for r in results),
                status='FORWARD_EVIDENCE_ONLY_NOT_BREEDING')
