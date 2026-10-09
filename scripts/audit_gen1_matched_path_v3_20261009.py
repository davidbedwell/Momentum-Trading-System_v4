"""Episode-block paired predictive-skill audit; explicitly not trading certification."""
import json,pathlib
import numpy as np,pandas as pd
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008/matched_winner_loser_checkpoint_v3_20261009')
def main():
 p=pd.read_parquet(ROOT/'heldout_event_predictions.parquet')
 if p.empty:raise ValueError('No predictions')
 p['episode']=pd.to_datetime(p.decision_date).dt.to_period('Q').astype(str)
 p['model_loss']=(p.failure_probability-p.failure_outcome)**2
 p['baseline_loss']=(p.baseline_probability-p.failure_outcome)**2
 p['gain']=p.baseline_loss-p.model_loss
 # Aggregate by calendar episode first: shared markets and overlapping trades
 # must not be counted as independent evidence.
 g=p.groupby('episode').gain.mean()
 rng=np.random.default_rng(20261009)
 boots=np.mean(rng.choice(g.to_numpy(),size=(3000,len(g)),replace=True),axis=1)
 lo,hi=np.quantile(boots,[.025,.975])
 report={'status':'SCIENTIFIC_CERTIFICATION_FAIL' if lo<=0 else 'PREDICTIVE_EPISODE_TEST_PASS_ONLY',
 'heldout_rows':len(p),'genomes':int(p.genome_index.nunique()),
 'independent_quarter_blocks':len(g),'paired_brier_improvement':float(p.gain.mean()),
 'episode_mean_improvement':float(g.mean()),'episode_bootstrap_ci95':[float(lo),float(hi)],
 'episode_block_seed':20261009,'bootstrap_replicates':3000,
 'blocked_for_full_certification':['Calendar quarters are imperfect market episodes','Need as-of source release timestamp provenance','Need path-state recovery/failure targets beyond endpoint','Need portfolio policy replay with cost, CAGR and MDD','Need family/genome multiplicity and full-population coverage'],
 'protected_banks_touched':False}
 (ROOT/'paired_episode_audit.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
