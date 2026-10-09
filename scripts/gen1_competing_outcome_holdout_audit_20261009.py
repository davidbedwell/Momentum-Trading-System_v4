"""Evaluate frozen matched-failure scores against distinct first-passage outcomes.
This is cross-target diagnostic evidence, not a fitted competing-risk model.
"""
import pathlib,json
import numpy as np,pandas as pd
from sklearn.metrics import roc_auc_score,brier_score_loss
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
OUT=ROOT/'matched_winner_loser_checkpoint_v3_20261009'
def main():
 p=pd.read_parquet(OUT/'heldout_event_predictions.parquet')
 rows=[]
 for c in (5,10,15):
  x=p.loc[p.checkpoint==c].copy()
  labels=pd.read_parquet(ROOT/'shared_path_store_20261009'/f'competing_path_labels_{c:02d}.parquet')
  x=x.merge(labels[['event_id','up_first','down_first','censored_or_tied']],on='event_id',how='left',validate='many_to_one')
  assert not x.down_first.isna().any()
  # Side is not stored in the predictions; recover frozen candidate side only.
  candidates={r['index']:r['side'] for r in map(json.loads,(ROOT/'all_candidates.jsonl').open())}
  x['side']=x.genome_index.map(candidates)
  assert x.side.notna().all()
  # In a short, upward movement is adverse; in a long, downward is adverse.
  x['adverse_first']=np.where(x.side=='LONG',x.down_first,x.up_first)
  x['favorable_first']=np.where(x.side=='LONG',x.up_first,x.down_first)
  x=x.loc[~x.censored_or_tied].copy()
  y=x.adverse_first.astype(int)
  assert ((x.adverse_first.astype(int)+x.favorable_first.astype(int))==1).all()
  for genome,g in x.groupby('genome_index'):
   yy=g.adverse_first.astype(int)
   if yy.nunique()<2:continue
   rows.append({'checkpoint':c,'genome_index':int(genome),'n':len(g),
    'adverse_rate':float(yy.mean()),'failure_score_auc_for_adverse_first':float(roc_auc_score(yy,g.failure_probability)),
    'failure_score_brier_for_adverse_first':float(brier_score_loss(yy,g.failure_probability)),
    'constant_base_brier':float(brier_score_loss(yy,np.repeat(yy.mean(),len(yy))))})
 out=pd.DataFrame(rows)
 out.to_parquet(OUT/'competing_outcome_cross_target_metrics.parquet',index=False)
 report={'status':'CROSS_TARGET_DIAGNOSTIC_UNCERTIFIED','records':len(out),
 'total_uncensored_predictions':int(out.n.sum()),'mean_auc_unweighted':float(out.failure_score_auc_for_adverse_first.mean()),
 'mean_brier_delta_vs_oracle_prevalence':float((out.constant_base_brier-out.failure_score_brier_for_adverse_first).mean()),
 'note':'Endpoint-trained failure score evaluated on different adverse-first target; no claim of target calibration. Oracle prevalence baseline is descriptive and not deployable.',
 'remaining':['Fit chronological competing-outcome model with censoring','Episode-aware paired out-of-time tests','Feature release-time audit','Economic portfolio replay'],
 'protected_banks_touched':False}
 (OUT/'competing_outcome_cross_target_audit.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
