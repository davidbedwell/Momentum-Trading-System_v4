"""Matched-null H.7 orchestration helpers. Freeze all Train80 finalists before Blind37 access."""
from __future__ import annotations
from pathlib import Path
from .ga import DD_BANDS
from .gates import freeze_finalists,require_all_fold_freezes
from .g2finalists import select_band_finalist
from .g2schema import genome_hash,canonical,genome_from_canonical_g2
from .g2fast import fast_simulate_g2
from .g2fitness import _cagr_mdd

def select_fold_finalists(tape,fold,archives):
    out=[]
    # I.4 is per DD band. Pool all training archives; selector re-applies band feasibility.
    pool=[];seen=set()
    for a in archives.values():
        for g,m in a:
            h=genome_hash(g)
            if h not in seen:pool.append((g,m));seen.add(h)
    for band in DD_BANDS:
        z=select_band_finalist(tape,fold,band,pool)
        if z is None:continue
        g,m,ev=z
        out.append({"band":float(band),"genome_hash":genome_hash(g),"genome":canonical(g),
                    "training_metrics":{k:v for k,v in m.items() if not str(k).startswith("_")},
                    "finalist_freeze_evidence":ev})
    return out

def freeze_training_fold(path,fold,tape,archives):
    finalists=select_fold_finalists(tape,fold,archives)
    if not finalists:raise RuntimeError(f"NO_I4_FINALISTS_FOLD_{fold}")
    h=freeze_finalists(path,fold,{"status":"FROZEN_TRAIN_ONLY","finalists":finalists})
    return finalists,h

def enforce_four_fold_barrier(paths,hashes):
    return require_all_fold_freezes([str(x) for x in paths],hashes)

def blind_replay(tape,finalists,decode=genome_from_canonical_g2):
    rows=[]
    for f in finalists:
        g=decode(f["genome"]);equity,*_=fast_simulate_g2(g,tape);cagr,mdd=_cagr_mdd(equity)
        rows.append({"band":f["band"],"genome_hash":f["genome_hash"],"blind_cagr":cagr,"blind_mdd":mdd})
    return rows
