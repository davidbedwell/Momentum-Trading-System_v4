"""Chronological rolling selection from a pre-frozen candidate bank; diagnostic only.
Candidate genomes must be frozen before the earliest evaluation window.
This is NOT evolutionary retraining or a live continuous portfolio.
"""
import argparse,json,sys
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from ga5_chromosome_contract import Genome
from guarded_evaluator import PreparedSessions,evaluate
from optimizer_v3 import fitness

def windows(dates,train_years=5,validation_years=2,test_years=1):
 dates=pd.DatetimeIndex(sorted(pd.to_datetime(dates).unique()))
 if len(dates)<3:raise ValueError('Insufficient dates')
 end=dates.max()+pd.Timedelta(days=1)
 origin=dates.min().normalize()
 cursor=origin+pd.DateOffset(years=train_years+validation_years)
 while cursor+pd.DateOffset(years=test_years)<=end:
  train_end=cursor-pd.DateOffset(years=validation_years)
  test_end=cursor+pd.DateOffset(years=test_years)
  yield origin,train_end,cursor,test_end
  cursor=test_end

def run(argv=None):
 p=argparse.ArgumentParser()
 for name in ('features','policy-file','genomes','output'):p.add_argument('--'+name,required=True)
 p.add_argument('--diagnostic-only',action='store_true')
 p.add_argument('--train-years',type=int,default=5)
 p.add_argument('--validation-years',type=int,default=2)
 p.add_argument('--test-years',type=int,default=1)
 a=p.parse_args(argv)
 if not a.diagnostic_only:raise ValueError('Diagnostic-only required')
 if min(a.train_years,a.validation_years,a.test_years)<1:raise ValueError('Invalid window')
 source=Path(a.features);manifest=json.loads(source.with_suffix('.manifest.json').read_text())
 if manifest.get('engine')!='ga5-research-v4':raise ValueError('Unverified feature manifest')
 frame=pd.read_parquet(source);frame['date']=pd.to_datetime(frame.date)
 policy=json.loads(Path(a.policy_file).read_text())
 membership={(d,t):v for d,t,v in policy['membership']}
 veto=policy['risk_veto'];blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
 genomes=[Genome(**g) for g in json.loads(Path(a.genomes).read_text())]
 if not genomes or not all(g.valid() for g in genomes):raise ValueError('Invalid candidate bank')
 report=[]
 for origin,train_end,test_start,test_end in windows(frame.date,a.train_years,a.validation_years,a.test_years):
  training=frame[(frame.date>=origin)&(frame.date<train_end)]
  validation=frame[(frame.date>=train_end)&(frame.date<test_start)]
  testing=frame[(frame.date>=test_start)&(frame.date<test_end)]
  if min(len(training),len(validation),len(testing))==0:continue
  train_prep,val_prep,test_prep=map(PreparedSessions,(training,validation,testing))
  ranked=[]
  for g in genomes:
   tr=evaluate(train_prep,g,blocked=blocked,membership=membership,risk_veto=veto,annual_cash_yield=policy['cash_proxy_annual_yield'])
   va=evaluate(val_prep,g,blocked=blocked,membership=membership,risk_veto=veto,annual_cash_yield=policy['cash_proxy_annual_yield'])
   ranked.append((fitness(va),fitness(tr),g.identity(),g))
  ranked.sort(key=lambda x:(-x[0],-x[1],x[2]))
  chosen=ranked[0][3]
  # Test only AFTER selection is frozen for this window.
  te=evaluate(test_prep,chosen,blocked=blocked,membership=membership,risk_veto=veto,annual_cash_yield=policy['cash_proxy_annual_yield'])
  report.append({'train_end_exclusive':str(train_end.date()),'test_start':str(test_start.date()),'test_end_exclusive':str(test_end.date()),'selected_identity':chosen.identity(),'validation_fitness':ranked[0][0],'test_cagr':te['cagr_diagnostic'],'test_mdd':te['mdd_diagnostic'],'test_final_nav':te['final_nav'],'test_sessions':te['sessions'],'test_shadow_mean_return':te['shadow']['mean_net_return'],'test_scale_fills':te['scale_fills']})
 output={'status':'FIXED_BANK_WALK_FORWARD_DIAGNOSTIC_NOT_CERTIFIED','windows':report,'warnings':['No evolutionary retraining: fixed seed bank only','Do not compound independent fold NAVs as a continuous portfolio','Provisional PIT/earnings/market policy','Candidate bank provenance must be verified frozen before evaluation']}
 dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(output,indent=2))
 print(json.dumps({'status':output['status'],'windows':report},indent=2))
if __name__=='__main__':run()
