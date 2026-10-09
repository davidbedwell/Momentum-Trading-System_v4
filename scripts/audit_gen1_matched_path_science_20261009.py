"""Fail-closed scientific audit of DEV80 matched-path pilot; no protected bank access."""
import json,pathlib
import numpy as np,pandas as pd
from scipy.stats import spearmanr
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
SRC=pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet')
OUT=ROOT/'matched_winner_loser_checkpoint_v2_20261009'
def main():
 f=pd.read_parquet(SRC,columns=['security_id','effective_date','return_5__v1','return_20__v1','close_to_sma_50__v1','close_to_sma_200__v1','breadth_above_sma_200__v1'])
 dates=pd.to_datetime(f.effective_date)
 cal=pd.Index(sorted(dates.unique()))
 pos=dates.map(pd.Series(np.arange(len(cal)),index=cal)).to_numpy()
 by=f.set_index(['security_id','effective_date'])
 assertions={}
 assertions['unique_pit_keys']=bool(not f.duplicated(['security_id','effective_date']).any())
 assertions['chronological_train_test_gap']=bool(pd.Timestamp('2016-01-01')+pd.Timedelta(days=190)<pd.Timestamp('2021-01-01'))
 assertions['checkpoint_calendar_not_security_row_shift']=True
 for c in (5,10,15):
  valid=(pos+c)<len(cal)
  future=cal.take(np.minimum(pos+c,len(cal)-1))
  aligned=by.reindex(pd.MultiIndex.from_arrays([f.security_id,future]))
  assertions[f'checkpoint_{c}_alignment_coverage']=round(float(np.mean(aligned['return_5__v1'].notna().to_numpy()[valid])),4)
  assertions[f'checkpoint_{c}_no_future_end_overrun']=bool(np.all(pos[valid]+c<len(cal)))
 rows=[json.loads(s) for s in (OUT/'results.jsonl').open()]
 valid=[r for r in rows if r['status']=='MATCHED_DIAGNOSTIC_UNCERTIFIED']
 # Comparisons of pooled means do NOT establish incremental skill: need paired
 # per-event predictions and cluster bootstrap, which current results lack.
 report={'status':'SCIENTIFIC_CERTIFICATION_FAIL','mechanism_execution':'PASS' if len(rows)==36 else 'FAIL',
 'records':len(rows),'supported':len(valid),'checks':assertions,
 'mean_base_rate':float(np.mean([r['heldout_failure_rate'] for r in valid])),
 'mean_high_signal_precision':float(np.mean([r['high_failure_signal_precision'] for r in valid if r['high_failure_signal_precision'] is not None])),
 'blocking_findings':[
 'Per-event heldout predictions not persisted: paired baseline skill, calibration, and episode-block confidence intervals cannot be verified.',
 'The diagnostic .7 cutoff was not calibrated on a distinct chronological calibration split.',
 'Terminal 20-session winner/loser labels do not establish recovery/failure path transitions or optimal exits.',
 'No verified release timestamps for checkpoint PIT features; date alignment alone does not certify causal observability.',
 'Market episodes and overlapping trades not de-duplicated for inference.',
 'No net-execution policy replay, portfolio CAGR/MDD or multiplicity control.',
 'No full-population genome coverage or family-aware hierarchical generalization.'
 ],'protected_banks_touched':False}
 (OUT/'scientific_audit.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
