"""Frozen cohort promotion evidence; never used for GA7 breeding."""
import hashlib,json
from dataclasses import asdict
from ga7.fold_evaluation import replay_fold,summarize_forward
from ga7.independence import assert_nonoverlapping_forward
from ga7.runner import COLUMNS
from ga7.chronological_partition import partition


def freeze_cohort(scored_by_group, per_group=8):
    if per_group<1: raise ValueError('Invalid cohort size')
    cohort={}
    for group,scored in sorted(scored_by_group.items()):
        ranked=sorted(scored,key=lambda gm:(-gm[1].get('conservative_ev_r',-1),gm[1].get('mae_stop_ratio',10),gm[0].identity()))
        cohort[group]=[asdict(g) for g,_ in ranked[:per_group]]
    payload=json.dumps(cohort,sort_keys=True)
    return {'schema':'ga7-frozen-cohort-v1','sha256':hashlib.sha256(payload.encode()).hexdigest(),'chromosomes':cohort}


def forward_evidence(genome, group, sessions, windows, stock_folds, passes):
    def gated(g,bar):
        niche=bar.get('controlling_niche') or 'NON_NICHE'
        return (group=='NON_NICHE' or group==niche) and passes(g,bar)
    assert_nonoverlapping_forward(windows)
    _,windows=partition(windows)
    rows=[]
    for window in windows:
        for name,tickers in sorted(stock_folds.items()):
            try:
                m=replay_fold(genome,sessions,gated,window,tickers,'forward',columns=COLUMNS)
            except ValueError as exc:
                if str(exc)!='Insufficient fold sessions': raise
                continue
            rows.append({'window':window['test_start'],'stock_fold':name,**m})
    return summarize_forward(rows),rows
