"""Research-only shared $100k, 13-niche next-open portfolio replay."""
import sys,json,csv,math
from pathlib import Path
import pandas as pd
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
from ga5_chromosome_contract import Genome
from guarded_evaluator_niche_single_exit import PreparedSessions
from ga5_feature_adapter import extract
from ga5_chromosome_decisions import PositionState
from fast_decision import evaluate as signal
from settlement_ledger import SettledLedger
from mts_next_open_ledger_v1 import Order
from ga5_earnings_entry_embargo import entry_allowed
root=Path('/opt/mts/ga5_redesign')
dest=root/'dev79_niche_origin_500x1000_20261019'/'all13_niche_screen'/'shared_capital_13_niche_v1'
dest.mkdir(parents=True,exist_ok=True)
ledger_path=root/'dev79_niche_origin_500x1000_20261019'/'all_evaluations.jsonl'
selected={}
for line in ledger_path.open():
 x=json.loads(line);r=x['result'];n=x['origin_niche']
 if r.get('fills',0)<100:continue
 if n not in selected or r['cagr_diagnostic']>selected[n]['result']['cagr_diagnostic']:selected[n]=x
genomes={n:Genome(**x['genome']) for n,x in selected.items()}
if len(genomes)!=13:raise RuntimeError('Insufficient trade-active niches')
print('SELECTED',len(genomes),flush=True)
frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet')
frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
sessions=PreparedSessions(frame)
labels=pd.read_parquet(root/'dev79_niche_ga_v1/labels.parquet')
label_map={(str(r.date)[:10],r.ticker):r.research_niche for r in labels.itertuples(index=False)}
policy=json.loads((root/'exploratory79_policy.json').read_text())
membership={(d,t):v for d,t,v in policy['membership']}
blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
veto=policy['risk_veto']
if not sessions.membership_keys.issubset(membership) or not sessions.dates.issubset(veto):raise RuntimeError('Missing PIT policies')
for key in sessions.membership_keys:label_map.setdefault(key,None)
ledger=SettledLedger(100000,.001,price_basis='split_adjusted')
positions={};last={};pending=None;nav=[];util=[];rejected={}
for i,(ds,rows,opens,closes) in enumerate(sessions.sessions):
 ledger.start_session(ds,i,policy['cash_proxy_annual_yield'])
 for t,r in rows.items():
  if r.get('dividends',0) or r.get('stock_splits',0):
   ledger.apply_ex_date(ds,t,float(r.get('stock_splits',0)),float(r.get('dividends',0)))
 if pending:
  signal_date,exits,entries=pending
  if veto[ds] is not True:
   exits=list(ledger.holdings);entries=[]
  for t in exits:
   q=ledger.holdings.get(t,0)
   if q and t in opens:
    ledger.execute_open(Order(signal_date,t,'SELL',q),ds,opens[t]);positions.pop(t,None)
  for t,n,weight,strength in entries:
   if t in positions or t not in opens or not membership.get((ds,t),False) or not entry_allowed(t,ds,blocked) or veto[signal_date] is not True or veto[ds] is not True:continue
   if len(positions)>=35:break
   price=opens[t];equity=ledger.cash+sum(q*opens.get(k,last.get(k,0)) for k,q in ledger.holdings.items())
   cap=min(weight,.10)
   q=min(int(equity*cap/(price*1.001)),int(ledger.available_cash()/(price*1.001)))
   if q<=0:continue
   ledger.execute_open(Order(signal_date,t,'BUY',q),ds,price)
   positions[t]=(n,PositionState(q,price,price,0))
 if any(q>0 and t not in closes for t,q in ledger.holdings.items()):raise RuntimeError('Missing held close')
 last.update(closes)
 equity=ledger.nav(closes)
 nav.append((ds,equity))
 util.append(sum(q*closes[t] for t,q in ledger.holdings.items())/equity)
 exits=[];entries=[]
 for t,(n,p) in list(positions.items()):
  p=PositionState(p.shares,p.entry_price,max(p.peak_price,closes[t]),p.sessions_held+1)
  positions[t]=(n,p)
  g=genomes[n];f=extract(rows[t],(g.entry_feature,g.hold_feature,g.exit_feature,g.regime_feature,g.sizing_feature,g.replace_feature))
  if f is None:continue
  action,_=signal(g,f,p,closes[t])
  if action in ('EXIT','REPLACE_CANDIDATE'):exits.append(t)
 for t,r in rows.items():
  if t in positions or t in exits:continue
  n=label_map[(ds,t)]
  if n not in genomes:continue
  g=genomes[n]
  f=extract(r,(g.entry_feature,g.hold_feature,g.exit_feature,g.regime_feature,g.sizing_feature,g.replace_feature))
  if f is None:continue
  action,weight=signal(g,f,PositionState(),closes[t])
  if action=='ENTER':entries.append((t,n,weight,float(f[g.entry_feature])))
 entries.sort(key=lambda x:(-x[3],x[0]))
 if veto[ds] is not True:exits=list(positions);entries=[]
 pending=(ds,exits,entries)
 if i%500==0:print('SESSIONS',i,'/',len(sessions.sessions),flush=True)
peak=100000;mdd=0
for _,value in nav:
 peak=max(peak,value);mdd=min(mdd,value/peak-1)
years=(pd.Timestamp(nav[-1][0])-pd.Timestamp(nav[0][0])).days/365.25
result=dict(status='RESEARCH_IN_SAMPLE_SELECTION',starting_cash=100000,final_nav=nav[-1][1],cagr=(nav[-1][1]/100000)**(1/years)-1,mdd=mdd,years=years,sessions=len(nav),fills=len(ledger.fills),buys=sum(f['side']=='BUY' for f in ledger.fills),sells=sum(f['side']=='SELL' for f in ledger.fills),mean_capital_utilization=sum(util)/len(util),cash_yield=ledger.cash_yield_total,fees=sum(f['fee'] for f in ledger.fills),niches_selected=list(genomes),limitations='Chromosomes selected by full-sample CAGR (lookahead selection); no out-of-sample certification; excludes scale-in/out for initial shared allocator; one best full-sample chromosome per niche with >=100 fills; selected from historical evaluation ledger rather than corrected-breeder offspring.')
with (dest/'daily_nav.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['date','nav','invested_fraction']);w.writerows((date,value,frac) for (date,value),frac in zip(nav,util))
(dest/'report.json').write_text(json.dumps(result,indent=2))
print('RESULT',json.dumps(result,indent=2),flush=True)
