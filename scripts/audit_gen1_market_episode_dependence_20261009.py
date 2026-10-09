"""Outcome-blind episode-level inference on held-out DEV80 predictions.

Calendar-year grouping is a conservative shared-market block proxy, NOT proof
of independent market crashes. Report both pooled and episode-level results.
"""
import argparse,json,pathlib
import numpy as np,pandas as pd
from scipy.stats import binomtest
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008/matched_horizon_v4_full_20261009')
def audit():
 files=sorted(ROOT.glob('batch_*/heldout_event_predictions.parquet'))
 if not files:raise RuntimeError('No completed batches')
 frames=[pd.read_parquet(f) for f in files if (f.parent/'verified.json').exists()]
 if not frames:raise RuntimeError('No verified batches')
 p=pd.concat(frames,ignore_index=True)
 if p.empty:raise RuntimeError('No predictions')
 p['year']=pd.to_datetime(p.decision_date).dt.year
 if not p['year'].between(2021,2026).all():raise RuntimeError('Unexpected heldout year')
 y=p.failure_outcome.to_numpy(float)
 p['gain']=(p.baseline_probability.to_numpy(float)-y)**2-(p.failure_probability.to_numpy(float)-y)**2
 # First aggregate within each calendar date, eliminating pseudo-replication across genomes.
 daily=p.groupby(['year','decision_date'],sort=True).gain.mean().reset_index()
 episodes=daily.groupby('year').agg(days=('gain','size'),gain=('gain','mean')).reset_index()
 k=int((episodes.gain>0).sum());n=len(episodes)
 report={'status':'EPISODE_BLOCK_AUDIT_DESCRIPTIVE_NOT_INDEPENDENCE_CERTIFICATION',
 'verified_batches':len(frames),'predictions':len(p),'years':n,
 'daily_equal_weight_gain':float(daily.gain.mean()),'episode_equal_weight_gain':float(episodes.gain.mean()),
 'positive_years':k,'one_sided_sign_test_p':float(binomtest(k,n,0.5,alternative='greater').pvalue),
 'worst_year_gain':float(episodes.gain.min()),'year_table':episodes.to_dict('records'),
 'limitations':['Calendar years are dependent and not independent crash episodes',
 'Test period 2021-2026 cannot independently validate GFC or COVID',
 'Multiple genomes and checkpoints share underlying dates and market shocks',
 'No certification until outcome-blind regime segmentation and episode holdouts'] }
 (ROOT/'market_episode_audit.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=='__main__':audit()
