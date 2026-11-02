"""Four-fold selector learning infrastructure. No chromosome evolution.
The ledger is append-only; updates occur only after outcome_available_at.
Proof fold is immutable. Portfolio replay requires separate integration.
"""
from dataclasses import dataclass
from pathlib import Path
import csv,json,hashlib,datetime,math
FOLDS=(('F1','2015-01-01','2018-01-01','train'),('F2','2018-01-01','2020-01-01','train'),('F3','2020-01-01','2023-01-01','train'),('F4','2023-01-01','2025-01-01','proof'))
CASH_RATE=.01
OUT=Path('/opt/mts/ga6/runs/selector_learning_fourfold_20261025')
FIELDS=('signal_id','signal_date','ticker','niche_id','chromosome_id','defense_mode','selector_version','rank','predicted_net_return','predicted_risk','allocation','decision','decision_reason','entry_date','exit_date','outcome_available_at','realized_net_return','mae','mfe','holding_sessions','shadow','capital_feasible','correlation_feasible')
def fold_for(date):
 d=str(date)[:10]
 for name,start,end,role in FOLDS:
  if start<=d<end:return name
 raise ValueError('Outside configured folds: '+d)
def stable_id(date,ticker,niche,chromosome,mode):
 raw='|'.join(map(str,(date,ticker,niche,chromosome,mode)))
 return hashlib.sha256(raw.encode()).hexdigest()
class ShadowLedger:
 def __init__(self,path=OUT/'shadow_ledger.jsonl'):
  self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
 def append(self,row):
  missing=set(FIELDS)-set(row)
  if missing:raise ValueError('Missing shadow fields: '+str(sorted(missing)))
  if fold_for(row['signal_date'])=='F4' and row['selector_version'] not in ('FROZEN_V0','FROZEN_V1'):
   raise ValueError('Proof fold must use frozen selector')
  if row['outcome_available_at'] and str(row['outcome_available_at'])<str(row['signal_date']):raise ValueError('Outcome precedes signal')
  with self.path.open('a') as h:h.write(json.dumps({k:row[k] for k in FIELDS},sort_keys=True,allow_nan=False)+'\n')
 def matured(self,asof,training_only=True):
  with self.path.open() as h:
   for line in h:
    row=json.loads(line)
    if training_only and fold_for(row['signal_date'])=='F4':continue
    if row['outcome_available_at'] and row['outcome_available_at']<str(asof) and row['realized_net_return'] is not None:
     yield row
class RetainedSelectorMemory:
 """Stable chromosome/niche identities, anchored prior, bounded updates and replayable snapshots."""
 def __init__(self,prior_strength=20):
  self.prior_strength=prior_strength;self.state={};self.seen=set()
 def observe(self,row,asof):
  if fold_for(row['signal_date'])=='F4':raise ValueError('Proof data cannot train selector')
  if not row['outcome_available_at'] or row['outcome_available_at']>=str(asof):raise ValueError('Unmatured outcome')
  sid=row['signal_id']
  if sid in self.seen:raise ValueError('Duplicate outcome update')
  value=float(row['realized_net_return'])
  mae=float(row['mae'] or 0)
  if not math.isfinite(value) or not math.isfinite(mae):raise ValueError('Invalid return or MAE')
  key=(row['niche_id'],row['chromosome_id'])
  rec=self.state.setdefault(key,{'count':0,'sum_net':0.,'sum_sq':0.,'sum_mae':0.,'wins':0})
  rec['count']+=1;rec['sum_net']+=value;rec['sum_sq']+=value*value
  rec['sum_mae']+=mae
  self.seen.add(sid)
  rec['wins']+=int(value>0)
 def score(self,niche,chromosome):
  rec=self.state.get((niche,chromosome))
  if not rec:return 0.
  return rec['sum_net']/(self.prior_strength+rec['count'])
 def snapshot(self,path,trained_through):
  if str(trained_through)>='2023-01-01':raise ValueError('Training cutoff breaches proof fold')
  doc={'schema':'selector-memory-v1','trained_through':str(trained_through),'prior_strength':self.prior_strength,'records':[{'niche':n,'chromosome':c,**v} for (n,c),v in sorted(self.state.items())],'seen_ids_sha256':hashlib.sha256('|'.join(sorted(self.seen)).encode()).hexdigest(),'observation_count':len(self.seen),'chromosomes_frozen':True}
  p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(doc,indent=2,sort_keys=True));return doc
def write_plan():
 OUT.mkdir(parents=True,exist_ok=True)
 plan={'status':'INFRASTRUCTURE_CREATED_NOT_PORTFOLIO_REPLAYED','folds':[dict(name=n,start=s,end_exclusive=e,role=r) for n,s,e,r in FOLDS],'cash_annual_rate':CASH_RATE,'universes':['DEV79','DEV87'],'portfolio_modes':['defense_on','defense_off'],'starting_capital_per_mode':100000,'learning':'cumulative mature outcomes only; stable niche/chromosome IDs; anchored smoothed returns; append-only shadow ledger; frozen F4','benchmark':['fold-start equal-dollar buy and hold','daily equal-weight rebalance'],'requirements_before_execution':['reconcile 165 unique observed vs expected 166','certify price data and fold-start universe membership','integrate actual chromosome signal generation and realistic exits into shadow ledger','integrate shared-capital portfolio simulator and independent ON/OFF ledgers','freeze selector at 2022-12-31 and prohibit fold4 learning','prevent outcomes whose exit crosses fold boundary from leaking into earlier training','retain untouched original selector as V0 comparator'],'source_niche_memory':['persistent_niche_memory_v1.py','adaptive_niche_memory_v1.py','expandable_niche_memory_v1.py','forward_only_niche_policy_v1.py']}
 (OUT/'study_plan.json').write_text(json.dumps(plan,indent=2))
 with (OUT/'shadow_ledger_schema.csv').open('w',newline='') as h:csv.writer(h).writerow(FIELDS)
 return plan
if __name__=='__main__':print(json.dumps(write_plan(),indent=2))
