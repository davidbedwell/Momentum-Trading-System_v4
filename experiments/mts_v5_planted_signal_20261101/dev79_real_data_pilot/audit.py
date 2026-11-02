"""Read-only inventory; never imports strategy engines or computes returns."""
import os, resource, time, json, hashlib
from pathlib import Path
from datetime import datetime, timezone
os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
resource.setrlimit(resource.RLIMIT_CPU, (1200, 1200))
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', ARROW_NUM_THREADS='1')
import pyarrow as pa
pa.set_cpu_count(1)
pa.set_io_thread_count(1)
import pyarrow.parquet as pq
import pandas as pd
O=Path(__file__).resolve().parent
ROOT=O.parents[2]
BASE=O.parent
start=time.monotonic()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(name,v): (O/name).write_text(json.dumps(v,indent=2,default=str)+'\n')
paths=[Path(p) for p in [
 '/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet',
 '/opt/mts/ga5_redesign/exploratory79_features.parquet',
 '/opt/mts/ga6/data/ga6d_defensive_features.parquet']]
inventory=[];constituents={}
for p in paths:
    pf=pq.ParquetFile(p);names=pf.schema_arrow.names
    cols=[c for c in ['date','ticker','security_id','dividends','stock_splits','sector_name'] if c in names]
    d=pf.read(columns=cols,use_threads=False).to_pandas()
    d['date']=pd.to_datetime(d.date).dt.strftime('%Y-%m-%d')
    coverage=d.groupby('ticker').agg(first_date=('date','min'),last_date=('date','max'),rows=('date','size')).reset_index()
    coverage['security_ids']=coverage.ticker.map(d.groupby('ticker').security_id.agg(lambda v:'|'.join(sorted(set(map(str,v))))) if 'security_id' in d else '')
    coverage.to_csv(O/(p.stem+'_constituents.csv'),index=False)
    constituents[p.stem]=sorted(d.ticker.unique().tolist())
    actions={c:{'missing':int(d[c].isna().sum()),'nonzero_rows':int((d[c].fillna(0)!=0).sum())} for c in ['dividends','stock_splits'] if c in d}
    period=d[(d.date>='2009-01-01')&(d.date<='2018-12-31')]
    item=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,rows=len(d),columns=names,
      first_date=d.date.min(),last_date=d.date.max(),sessions=d.date.nunique(),tickers=d.ticker.nunique(),
      duplicate_date_ticker_rows=int(d.duplicated(['date','ticker']).sum()),corporate_action_columns=actions,
      period_2009_2018=dict(rows=len(period),tickers=period.ticker.nunique(),sessions=period.date.nunique(),absent_symbols=sorted(set(d.ticker)-set(period.ticker))),
      pit_timestamp_columns=[c for c in names if any(s in c.lower() for s in ['available_time','release_time','vintage','revision','payment_date'])])
    inventory.append(item)
dump('data_inventory.json',inventory);dump('constituents.json',constituents)
gate=Path('/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518/ga6_ga7_dev79_provenance_gate_20261028.json')
dump('archived_provenance_gate.json',json.loads(gate.read_text()))
lock=BASE/'iteration8b_calibration_validation/threshold_lock.json'
locked=json.loads(lock.read_text());locked['actual_calibration_sha256']=sha(lock.with_name('calibration.json'))
locked['calibration_hash_matches']=locked['calibration_sha256']==locked['actual_calibration_sha256']
dump('frozen_8b_cal_identity.json',locked)
sources=[gate,lock,lock.with_name('calibration.json'),lock.with_name('engine.py'),lock.with_name('run.py'),
 BASE/'iteration8_four_arm/corrected/engine.py',BASE/'discrimination_iteration6/engine.py',BASE/'discrimination_iteration5/experiment.py',
 Path('/opt/mts/ga7-deploy/current/ga7/runner.py'),Path('/opt/mts/ga7-deploy/current/ga7/RESEARCH_CONTRACT.md'),
 Path('/opt/mts/ga5_redesign/exploratory79_assumptions.json'),Path('/opt/mts/ga5_redesign/launch_exploratory_79.py'),
 Path('/opt/mts/ga5_redesign/canonical_engine.py'),Path('/opt/mts/ga5_redesign/exploratory79_policy.json'),
 ROOT/'manifest.json',ROOT/'DATA_SOURCE_POLICY.md',ROOT/'CONTROLLING_PROTOCOL_V2.md',O/'audit.py']
dump('source_hashes.json',{str(p):sha(p) for p in sources})
# Inventory independent data schema/coverage only; synthetic experiment tapes excluded.
ind=[]
for p in sorted((ROOT/'experiments/sector_etf_20261031/data').glob('*.parquet')):
    pf=pq.ParquetFile(p)
    ind.append(dict(path=str(p),sha256=sha(p),rows=pf.metadata.num_rows,columns=pf.schema_arrow.names,role='ETF panel, not a verified DEV79 sensor tape'))
dump('independent_data_inventory.json',dict(repository_manifest=json.loads((ROOT/'manifest.json').read_text()),etf_panels=ind,
 other_available_inputs=['universe_2019/members_2019_start.csv','universe_2019/identity_audit_2019.csv','universe_2019/price_coverage_2019.csv','universe_2019/pilot_technicals_2019.csv','universe_2019/pilot_technicals_2020.csv'],
 interpretation='Partial membership, identity, price and technical studies do not define or certify the synthetic cell sensor.'))
dump('report.json',dict(status='BLOCKED_NO_REAL_PREDICTOR_AND_UNVERIFIED_PIT_INPUTS',audit_completed=True,
 real_predictor_computable_as_defined=False,real_stock_sensor_mapping=None,pilot_run=False,portfolio_replays=0,
 preregistration_status='NOT_OPENED_FEASIBILITY_GATE_FAILED',production_changed=False,ga_launched=False,monitoring_launched=False,
 frozen_thresholds=locked['thresholds'],frozen_calibration_hash_matches=locked['calibration_hash_matches'],
 blockers=['No real-stock definition of synthetic latent-class-derived sensor cells',
 'Historical PIT membership/sector/earnings/niche feature/dividend payment-date gates unverified',
 'Frozen implementation hardcodes 24 assets; DEV79 universe and sparse cells require an explicit validated adapter',
 'Real execution price basis, corporate-action accounting and outcome availability contract not verified'],
 smallest_next_step='Specify and freeze a real-stock sensor feature contract with a source-backed PIT historical sample, without deriving cells from future returns or synthetic truth. This is a new predictor hypothesis; do not relabel momentum or GA4 features as the existing sensor.',
 resource=dict(cpu_affinity=list(os.sched_getaffinity(0)),cpu_limit_seconds=1200,elapsed_seconds=time.monotonic()-start,cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime),
 completed_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(json.loads((O/'report.json').read_text()),indent=2))
