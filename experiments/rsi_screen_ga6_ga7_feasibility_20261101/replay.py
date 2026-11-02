"""Bounded existing-chromosome feasibility; no optimizer, no production writes."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import sys,json,sqlite3,hashlib
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent; E=P.parent; M=Path('/opt/mts')
sys.path[:0]=[str(M),str(M/'ga7-deploy/ga7_audit_v2')]
from ga7.engine import Genome
from ga7.niche_controller import controlling_niche
from ga7.defense_contract import read_defense_state
sys.path.insert(0,str(E/'mts_v5_manager_repair_20261031/v5_working_copy'))
from discovery.competitive_ga.ga7_native_daily_producer import decision
sys.path.insert(0,str(E/'dev79_minimal_manager_20261101'))
from manager import Ledger, INITIAL

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCE=M/'portfolio_evolution_dev80/dev80_raw_no_smci.parquet'
ENRICH=M/'ga5_redesign/exploratory79_ga4_enriched.parquet'
COHORT=M/'ga7-deploy/ga7_audit_v2/validation/handoff/frozen_cohort.json'
CAT=M/'ga6/runs/frozen_four_run_20261024/catalogue.sqlite'
POL=M/'ga5_redesign/exploratory79_policy.json'
MAN=M/'ga7-deploy/ga7_unbounded/niche_pit_manifest.json'
TAPE=M/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv'
cohort=json.loads(COHORT.read_text()); bank={g:sorted(items,key=lambda z:z['identity'])[0] for g,items in cohort['cohort'].items()}
genomes={g:Genome(**v['genome']) for g,v in bank.items()}
assert len(bank)==14 and all(genomes[g].identity()==v['identity'] for g,v in bank.items())
(P/'bank.json').write_text(json.dumps(bank,indent=2))
con=sqlite3.connect('file:'+str(CAT)+'?mode=ro',uri=True)
ga6_counts=dict(con.execute("select json_extract(definition,'$.genome.niche'),count(*) from chromosomes group by 1"))
ga6_manager_stop_eligible=con.execute("select count(*) from chromosomes where json_extract(definition,'$.genome.stop_loss')<=0.02").fetchone()[0];con.close()
features=sorted({x for g in genomes.values() for x in (g.feature_a,g.feature_b)})
raw=pd.read_parquet(SOURCE,filters=[('date','<',pd.Timestamp('2019-01-01'))]);raw.date=pd.to_datetime(raw.date)
assert raw.ticker.nunique()==77 and not raw.duplicated(['date','ticker']).any()
f=pd.read_parquet(ENRICH,columns=['date','ticker',*features],filters=[('date','>=',pd.Timestamp('2009-01-01')),('date','<',pd.Timestamp('2019-01-01'))]);f.date=pd.to_datetime(f.date)
r=raw[raw.date.ge('2009-01-01')].merge(f,on=['date','ticker'],validate='one_to_one',how='left')
policy=json.loads(POL.read_text());membership={(d,t):bool(v) for d,t,v in policy['membership']}; blocked={t:set(v) for t,v in policy['blocked'].items()};veto=policy['risk_veto']
r['day']=r.date.dt.strftime('%Y-%m-%d')
assert all((d,t) in membership for d,t in zip(r.day,r.ticker))
r['eligible']=[membership[(d,t)] and d not in blocked.get(t,set()) and bool(veto[d]) for d,t in zip(r.day,r.ticker)]
# Match native fold rank semantics: rank over investable DEV79, before RSI screening.
# Native rank_filtered_sessions retains raw feature units for ineligible bars.
for col in features:
 ranked=r[col].where(r.eligible).groupby(r.date).rank(pct=True,method='average')
 r[col]=ranked.where(r.eligible,r[col])
manifest=json.loads(MAN.read_text());models=json.loads(Path(manifest['model_file']).read_text())
assert all(m['trained_through']<m['first_evaluation']<=m['last_evaluation'] for m in models)
dist=pd.read_parquet(manifest['distance_file'],filters=[('date','<','2019-01-01')]);dist.date=pd.to_datetime(dist.date)
dlookup={(pd.Timestamp(row[0]).strftime('%Y-%m-%d'),row[1]):row[2:] for row in dist[['date','ticker',*manifest['ids']]].itertuples(index=False,name=None)}
defense=read_defense_state(TAPE)
selections=pd.read_csv(E/'dev79_rsi_indicator_combinations_20261101/selections.csv');sel=selections[selections.strategy.eq('k2_2-4')]
fx=pd.read_csv(E/'dev79_rsi_winner_characteristics_20261101/stock_month_features.csv',parse_dates=['execution_date','feature_date'])
assert fx.feature_date.lt(fx.execution_date).all()
expected=fx[(fx.ma_distance_20<0)&(fx.acceleration_21>0)]
assert set(zip(expected.execution_date.dt.strftime('%Y-%m-%d'),expected.ticker))==set(zip(sel.execution_date,sel.ticker))
screens={d:set(g.ticker) for d,g in sel.groupby('execution_date')}
days=sorted(r.day.unique());monthstarts={d for i,d in enumerate(days) if i==0 or d[:7]!=days[i-1][:7]}
assert len(monthstarts)==120
assert all(any(m['first_evaluation']<=day<=m['last_evaluation'] and m['trained_through']<day for m in models) for day in days)
# Keep missing screen months explicitly empty.
sessions=[];prev={};niche_counts=Counter()
for day,group in r.groupby('day',sort=True):
 bars={}
 for row in group.to_dict('records'):
  t=row['ticker'];ds=dlookup.get((day,t));ctrl=controlling_niche(ds,[1.]*13,manifest['ids'],prev.get(t))[0] if ds is not None else None
  prev[t]=ctrl;niche_counts[ctrl or 'NON_NICHE']+=1
  bars[t]={**row,'features':{c:row[c] for c in features},'controlling_niche':ctrl}
 sessions.append((day,bars))

def run(mode):
 book=Ledger(); state={}; pending=[];daily=[];fills=[];decisions=[];orders=[];screen=set();closed=0;entries=0;slip=0.;missing=Counter();actions=Counter();maxerr=0.
 if mode=='fixed':
  initial_screen=screens.get(sessions[0][0],set())
  pending=[dict(date='2008-12-31',ticker=t,action='ENTER',target=INITIAL/len(initial_screen),admitted=True) for t in sorted(initial_screen)]
 for i,(day,bars) in enumerate(sessions):
  book.settle();ops={t:b['open'] for t,b in bars.items()};closes={t:b['close'] for t,b in bars.items()}
  assert set(book.q)<=set(bars),'held data disappears: no invented exit'
  open_nav=book.nav({**book.mark,**ops})
  carry=[]
  for o in sorted(pending,key=lambda o:(o['action'] in ('ENTER','ADD'),o['ticker'])):
   t=o['ticker'];action=o['action'];rec={**o,'execution_date':day}
   if t not in ops:rec['status']='MISSING_OPEN';orders.append(rec);continue
   old=book.q.get(t,0.);delta=o['target']/ops[t]-old
   if mode=='ga7' and action=='ADD':delta=o['increment']/ops[t]
   if mode=='ga7' and action=='REDUCE':delta=-old*o['sell_fraction']
   if mode=='ga7' and delta>0:
    if not o['admitted']:rec['status']='SCREEN_BLOCK';orders.append(rec);continue
    if old==0 and len(book.q)>=10:rec['status']='CAPACITY';orders.append(rec);continue
    equity=sum(q*ops[x] for x,q in book.q.items())
    delta=min(delta,max(0.,.10*open_nav-old*ops[t])/ops[t],max(0.,.90*open_nav-equity)/ops[t])
   fill=book.fill(t,delta,ops[t]) if abs(delta*ops[t])>.01 else None
   rec['status']='FILLED' if fill else 'NO_FILL';orders.append(rec)
   if mode=='fixed' and delta>0 and not o.get('retried') and book.due>0 and book.cash<.01:
    carry.append({**o,'retried':True})
   if fill:
    fills.append({**fill,'date':day,'signal_date':o['date'],'action':action,'group':o.get('group','')});slip+=fill['shares']*abs(fill['price']-fill['open'])
    if fill['side']=='BUY':
     if old==0:state[t]=dict(entry=fill['price'],peak=fill['price'],entry_session=i,initial_stop=o.get('stop',.02));entries+=1
     else:state[t]['entry']=(state[t]['entry']*old+fill['price']*fill['shares'])/book.q[t]
    elif t not in book.q:state.pop(t,None);closed+=1
  book.mark.update(closes);nav=book.nav(book.mark);equity=sum(q*book.mark[t] for t,q in book.q.items())
  err=abs(nav-(INITIAL+book.realized+equity-sum(a.open_cost for a in book.accounts.values())));maxerr=max(maxerr,err);assert err<1e-6
  daily.append(dict(date=day,nav=nav,exposure=equity/nav,positions=len(book.q),cash=book.cash,unsettled=book.due,fees=book.fees))
  pending=carry
  # Screen is known at prior close; activate the next month's list before that close's decision.
  nextday=sessions[i+1][0] if i+1<len(sessions) else None
  if nextday in monthstarts:screen=screens.get(nextday,set())
  if mode=='fixed':
   if nextday not in monthstarts:continue
   target={t:nav/len(screen) for t in screen} if screen else {}
   for t in sorted(set(book.q)|set(target)):
    pending.append(dict(date=day,ticker=t,action='ENTER' if target.get(t,0)>book.q.get(t,0)*closes[t] else 'EXIT',target=target.get(t,0),admitted=True))
   continue
  for t in sorted(set(screen)|set(book.q)):
   if t not in bars:missing['missing_candidate_bar']+=1;continue
   b=bars[t];group=b['controlling_niche'] or 'NON_NICHE';g=genomes[group]
   held=None
   if t in book.q:
    state[t]['peak']=max(state[t]['peak'],closes[t]);held={**state[t],'weight':book.q[t]*closes[t]/nav}
   # Missing native features abstain for entry and stop the replay for held positions.
   if any(not np.isfinite(b['features'][c]) for c in (g.feature_a,g.feature_b)):
    missing['held_no_features' if held else 'entry_no_features']+=1
    if held:raise RuntimeError('Held native features unavailable: '+day+' '+t)
    continue
   value=decision(g,b,held,defensive=defense[day]['defensive'])
   if value is None:continue
   action,weight=value;actions[action]+=1
   admitted=t in screen and b['eligible']
   if action in ('ENTER','ADD') and not admitted:actions['SCREEN_BLOCK']+=1;continue
   decisions.append(dict(date=day,ticker=t,group=group,chromosome=bank[group]['identity'],action=action,target_weight=weight,screen=t in screen))
   if action=='HOLD':continue
   o=dict(date=day,ticker=t,action=action,target=nav*weight,admitted=admitted,group=group,stop=g.stop_pct,increment=max(0.,nav*(weight-(held['weight'] if held else 0.))),sell_fraction=1-weight/held['weight'] if held else 0.)
   if nextday is not None:pending.append(o)
   else:orders.append({**o,'execution_date':'','status':'END_UNEXECUTED'})
 # Fixed first screen executes Jan 2 from its saved Dec 31 feature date.
 out=P/mode;out.mkdir(exist_ok=True)
 for name,rows in [('daily',daily),('fills',fills),('decisions',decisions),('orders',orders)]:pd.DataFrame(rows).to_csv(out/(name+'.csv'),index=False)
 vals=np.r_[INITIAL,[z['nav'] for z in daily]];dd=1-vals/np.maximum.accumulate(vals);cagr=(vals[-1]/INITIAL)**(252/len(daily))-1;mdd=float(dd.max())
 return dict(cagr=cagr,mdd=mdd,calmar=cagr/mdd if mdd else None,final_nav=vals[-1],sessions=len(daily),entries=entries,completed_trades=closed,open_trades=len(book.q),fills=len(fills),mean_exposure=float(np.mean([z['exposure'] for z in daily])),active_sessions=sum(z['positions']>0 for z in daily),fees=book.fees,slippage=slip,total_cost=book.fees+slip,actions=dict(actions),missing=dict(missing),max_reconciliation_error=maxerr)

def exact_reference():
 c=raw.pivot(index='date',columns='ticker',values='adj_close').sort_index();rc=raw.pivot(index='date',columns='ticker',values='close').reindex_like(c)
 op=raw.pivot(index='date',columns='ticker',values='open').reindex_like(c)*c/rc
 idx=c.index;starts=[idx.get_loc(pd.Timestamp(d)) for d in sorted(monthstarts)];last=idx.get_loc(pd.Timestamp('2018-12-31'))
 prev=np.zeros(len(c.columns));nav=INITIAL;daily=[INITIAL];fees=0.;buys=sells=0;monthly=[]
 for m,i in enumerate(starts):
  selected=screens.get(str(idx[i].date()),set());target=np.array([1/len(selected) if t in selected else 0. for t in c.columns])
  fee=0.
  for _ in range(12):fee=.001*np.abs(target*(1-fee)-prev).sum()
  delta=target*(1-fee)-prev;buys+=int((delta>1e-12).sum());sells+=int((delta<-1e-12).sum());fees+=nav*fee
  j=starts[m+1] if m<119 else last;mark=c.iloc[j] if m==119 else op.iloc[j]
  rel=(mark/op.iloc[i]-1).fillna(0).to_numpy();gross=1+target@rel
  marks=c.iloc[i:j+1 if m==119 else j]/op.iloc[i]
  daily.extend((nav*(1-fee)*(1+np.nan_to_num(marks.to_numpy()-1)@target)).tolist())
  nav*=((1-fee)*gross);daily.append(nav);prev=target*(1+rel)/gross
  monthly.append(dict(execution_date=str(idx[i].date()),nav=nav,fee_fraction=fee,count=len(selected)))
 v=np.array(daily);cagr=(nav/INITIAL)**(252/2516)-1;mdd=float((1-v/np.maximum.accumulate(v)).max())
 pd.DataFrame(monthly).to_csv(P/'exact_reference_monthly.csv',index=False)
 saved=pd.read_csv(E/'dev79_rsi_indicator_combinations_20261101/monthly.csv');saved=saved[saved.strategy.eq('k2_2-4')&saved.kind.eq('selected')]
 np.testing.assert_allclose(np.array([z['nav'] for z in monthly])/INITIAL,saved.nav,rtol=1e-12)
 return dict(cagr=cagr,mdd=mdd,calmar=cagr/mdd,fees=fees,slippage=0.,total_cost=fees,buys=buys,sells=sells,stock_months=321,active_months=92,mean_monthly_exposure=92/120,final_nav=nav)

results={mode:run(mode) for mode in ('fixed','ga7')}
results['existing_fixed_reference']=exact_reference()
(P/'metrics.json').write_text(json.dumps(results,indent=2))
audit=dict(ga6_counts=ga6_counts,ga6_manager_stop_eligible=ga6_manager_stop_eligible,ga6_status='BLOCKED: all old retrospective niche IDs; no PIT mapping',ga7_groups=list(bank),ga7_archive_complete=cohort['archive_complete'],niche_counts=dict(niche_counts),screen_candidates=len(sel),screen_active_months=len(screens),screen_months=120,source_max=str(raw.date.max()),training_cutoff='not certified for 2009; retrospective feasibility only',sources={str(p):sha(p) for p in [SOURCE,ENRICH,COHORT,CAT,POL,MAN,TAPE,Path(manifest['model_file']),Path(manifest['distance_file']),P/'PLAN.md',P/'replay.py',P/'verify.py',E/'dev79_rsi_indicator_combinations_20261101/selections.csv',E/'dev79_rsi_winner_characteristics_20261101/stock_month_features.csv',E/'mts_v5_manager_repair_20261031/v5_working_copy/discovery/competitive_ga/ga7_native_daily_producer.py',E/'dev79_minimal_manager_20261101/manager.py']})
(P/'audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(results,indent=2))
