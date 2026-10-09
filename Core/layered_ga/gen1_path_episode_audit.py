"""Descriptive block-level scoring; no independent-episode certification."""
import numpy as np,pandas as pd
def paired_brier_by_episode(predictions,episode_col='episode'):
 required={'failure_probability','baseline_probability','failure_outcome',episode_col}
 if not required.issubset(predictions):raise ValueError('Missing scoring columns')
 p=predictions.copy()
 if len(p)==0:raise ValueError('Empty predictions')
 for key in ('failure_probability','baseline_probability','failure_outcome'):
  if not np.isfinite(p[key].to_numpy(dtype=float)).all():raise ValueError('Nonfinite score inputs')
 if not p.failure_probability.between(0,1).all() or not p.baseline_probability.between(0,1).all():raise ValueError('Probability outside [0,1]')
 if not p.failure_outcome.isin([0,1]).all():raise ValueError('Invalid outcomes')
 if p[episode_col].isna().any():raise ValueError('Missing episode')
 y=p.failure_outcome.to_numpy(float)
 p['paired_gain']=(p.baseline_probability.to_numpy(float)-y)**2-(p.failure_probability.to_numpy(float)-y)**2
 grouped=p.groupby(episode_col,sort=True).agg(n=('paired_gain','size'),gain=('paired_gain','mean'))
 return {'row_weighted_gain':float(p.paired_gain.mean()),'episode_mean_gain':float(grouped.gain.mean()),
         'episodes':int(len(grouped)),'positive_episodes':int((grouped.gain>0).sum()),
         'episode_table':grouped.reset_index().to_dict('records'),
         'certification':'DESCRIPTIVE_ONLY_EPISODE_INDEPENDENCE_UNVERIFIED'}
def quarter_labels(dates):
 d=pd.to_datetime(dates)
 return d.to_period('Q').astype(str)
