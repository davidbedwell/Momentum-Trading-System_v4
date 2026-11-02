"""Allowlisted offline zero-fill diagnosis. No downloads, model calls or code writes."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .execution import Gene, Manager, replay
from .exploratory import inputs, model_signal, edge_manager
from .supervisor import atomic


def diagnose(source, output):
    evidence=json.loads((Path(source)/'best.json').read_text())
    provenance=json.loads((Path(source)/'inputs.json').read_text())
    kind='synthetic' if provenance['kind']=='synthetic' else 'real'
    p,meta,_=inputs(kind)
    if provenance['symbols'] != p.symbols or provenance.get('sources') != meta.get('sources'):
        result=dict(classification='UNKNOWN_INPUT_CHANGED',action='Review source hashes/cohort before retry')
    else:
        manager=Manager(**evidence['manager']); positive=blocked=counterfactual=0; folds=[]
        for fold in evidence['folds']:
            a=int(p.dates.searchsorted(pd.Timestamp(fold['start'])))
            b=int(p.dates.searchsorted(pd.Timestamp(fold['end_exclusive'])))
            signal,_=model_signal(p,evidence['family'],a,evidence['horizon'])
            raw=signal[0,a:b];valid=np.isfinite(raw)&(raw>0)
            biases=np.array([manager.niche_bias[int(n)] if n>=0 else 0. for n in p.niche[a:b].flat]).reshape(raw.shape)
            adjusted=raw+biases+(manager.specialist_bias[0] if manager.specialist_bias else 0.)
            positive+=int(valid.sum());blocked+=int((valid&(adjusted<manager.entry_floor)).sum())
            z=replay(p,[Gene(evidence['family'],threshold=0,hold_sessions=evidence['horizon'],weight=.06)],
                     edge_manager(manager),p.dates[a],p.dates[b-1]+pd.Timedelta(days=1),detail=True,
                     signal=signal,hold_signal=signal,edge_mode=True,absolute_edges=True)
            counterfactual+=z['metrics']['fills']
            folds.append(dict(metrics=z['metrics'],audit=z['audit'],first_fills=z['fills'][:3],
                              trade_decisions=sum(e['decision']=='TRADE' for e in z['events'])))
        known=(positive>0 and blocked==positive and counterfactual>0
               and all(f['metrics']['fills']==0 for f in evidence['folds']))
        result=dict(classification='EDGE_UNIT_MISMATCH' if known else 'UNKNOWN_ZERO_FILL',
                    positive_forecasts=positive,rank_offset_blocked_forecasts=blocked,
                    counterfactual_fills=counterfactual,folds=folds,
                    repair='edge_units_v2' if known else None,
                    action='Disable uncalibrated rank offsets; adapt manager floors to net return/session' if known else
                    'Inspect signal support, eligibility, capital/settlement and execution rejection audits; no automatic gate relaxation')
    result.update(certified=False,promotion_allowed=False,production_allowed=False,final_validation_allowed=False,llm_spend_usd=0)
    atomic(Path(output),result)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(__doc__);ap.add_argument('--source',required=True);ap.add_argument('--output',required=True)
    a=ap.parse_args();print(json.dumps(diagnose(a.source,a.output),allow_nan=False))
