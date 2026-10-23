"""Independent single-entry/single-exit forward-horizon diagnostic; NO portfolio or scaling.
Development-only discovery; forward outcomes never available to live decision rules.
"""
import json,math,hashlib,sys
from pathlib import Path
from statistics import mean
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from ga5_feature_adapter import LEGACY
from ga5_earnings_entry_embargo import entry_allowed

ROOT=Path(__file__).parent
OUT=ROOT/'dev79_trade_discovery_stage_a_20261019';OUT.mkdir(exist_ok=True)
frame=pd.read_parquet(ROOT/'exploratory79_ga4_enriched.parquet').sort_values(['ticker','date'])
policy=json.loads((ROOT/'exploratory79_policy.json').read_text())
member={(str(d)[:10],str(t)):bool(v) for d,t,v in policy['membership']}
veto=policy['risk_veto'];blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
source=json.loads((ROOT/'dev79_success_gt5_v2_20261019/checkpoint_unified.json').read_text())
# Genome entries are seeds for this independent entry-only search; exits/sizing ignored.
seeds=source['members']
seen=set();candidates=[]
for g in seeds:
 k=(g['entry_feature'],g['entry_threshold'],g['regime_feature'],g['regime_threshold'])
 if k not in seen:seen.add(k);candidates.append(k)
print('CANDIDATES',len(candidates),flush=True)
HORIZONS=(2,5,10,20,40,63)
# A signal is observed at close on session i; entry occurs open i+1; exit open i+1+h.
# Next signal in same stock is ignored until the prior trade is closed.
by_stock=[]
for ticker,part in frame.groupby('ticker',sort=False):
 part=part.reset_index(drop=True);dates=part.date.dt.strftime('%Y-%m-%d').to_numpy();opens=part.open.to_numpy(float);lows=part.low.to_numpy(float)
 valid=np.array([member.get((d,str(ticker)),False) and veto.get(d) is True and entry_allowed(str(ticker),d,blocked) for d in dates],dtype=bool)
 by_stock.append((str(ticker),part,dates,opens,lows,valid))
rows=[]
for ci,(entry,eth,reg,rth) in enumerate(candidates):
 e=LEGACY.get(entry,entry);r=LEGACY.get(reg,reg)
 if any(e not in part.columns or r not in part.columns for _,part,*_ in by_stock):continue
 for horizon in HORIZONS:
  trades=[]
  for ticker,part,dates,opens,lows,valid in by_stock:
   signal=(part[e].to_numpy(float)>=eth)&(part[r].to_numpy(float)>=rth)&valid
   i=0;n=len(part)
   while i+horizon+1<n:
    if not signal[i] or not valid[i+1] or not valid[i+horizon+1] or not np.isfinite(opens[i+1]) or not np.isfinite(opens[i+horizon+1]) or opens[i+1]<=0:
     i+=1;continue
    ret=opens[i+horizon+1]/opens[i+1]-1-.002
    mae=np.nanmin(lows[i+1:i+horizon+2])/opens[i+1]-1
    if np.isfinite(ret) and np.isfinite(mae):trades.append((ret,mae,ticker,dates[i+1],dates[i+horizon+1]))
    i+=horizon+1
  n=len(trades)
  if not n:continue
  a=np.array([t[0] for t in trades]);ad=np.array([t[1] for t in trades]);s=int((a>.05).sum());p=s/n;z=1.96
  wilson=(p+z*z/(2*n)-z*math.sqrt((p*(1-p)+z*z/(4*n))/n))/(1+z*z/n)
  unique_tickers=len(set(t[2] for t in trades));years=len(set(t[3][:4] for t in trades))
  rows.append(dict(entry_feature=entry,entry_threshold=eth,regime_feature=reg,regime_threshold=rth,horizon=horizon,trades=n,win_rate=float((a>0).mean()),success_gt5_rate=float(p),success_gt5_wilson95_lower=float(wilson),mean_net_return=float(a.mean()),median_net_return=float(np.median(a)),mean_loss=float(a[a<0].mean()) if (a<0).any() else 0.,worst5_mean=float(np.sort(a)[:max(1,int(n*.05))].mean()),mean_mae=float(ad.mean()),p95_adverse_excursion=float(np.quantile(ad,.05)),tickers=unique_tickers,years=years,eligibility=(n>=100 and unique_tickers>=15 and years>=5 and a.mean()>0)))
 if (ci+1)%10==0:print('PROGRESS',ci+1,len(candidates),flush=True)
result=pd.DataFrame(rows).sort_values(['eligibility','success_gt5_wilson95_lower','mean_net_return'],ascending=[False,False,False]);result.to_csv(OUT/'entry_horizon_rankings.csv',index=False)
summary={'status':'DIAGNOSTIC_ONLY_NOT_OUT_OF_SAMPLE','single_entry_single_exit':True,'scaling':False,'portfolio_sizing':False,'candidates':len(candidates),'evaluations':len(rows),'eligible':int(result.eligibility.sum()),'top10':result.head(10).to_dict('records'),'note':'Fixed-horizon entry screening, not final exit GA or independent certification. No look-ahead in entry signals; forward returns are labels used for retrospective ranking.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,default=str))
print('COMPLETE',json.dumps({k:v for k,v in summary.items() if k!='top10'}),flush=True)
