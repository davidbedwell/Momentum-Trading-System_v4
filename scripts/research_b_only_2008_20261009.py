#!/usr/bin/env python3
"""B-only exploratory causal trend study. A, C, R1 sourced unchanged."""
import csv,json,hashlib,datetime,urllib.request
from pathlib import Path
src=Path('/home/ubuntu/Momentum-Trading-System_v4/Research/State/MTS_ABC_DEFENSIVE_R1_STATE_TAPE_20261005.csv')
rows=list(csv.DictReader(src.open()));ds=[r['date'] for r in rows];N=len(rows)
u='https://query1.finance.yahoo.com/v8/finance/chart/SPY?period1=1126656000&period2=1791504000&interval=1d'
j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))['chart']['result'][0]
p={datetime.datetime.fromtimestamp(t,datetime.timezone.utc).date().isoformat():v for t,v in zip(j['timestamp'],j['indicators']['quote'][0]['close']) if v is not None};assert all(d in p for d in ds)
close=[p[d] for d in ds]; A=[r['A']=='True' for r in rows];C=[r['C']=='True' for r in rows];B=[r['B']=='True' for r in rows];R=[r['R1_evidence']=='True' for r in rows]
assert hashlib.sha256(src.read_bytes()).hexdigest()=='e827b8beed7d3a0a0512990b5c77eb94618fb52f8739695f16509008f1f920fe'
def run(b):
 state=False;entries=[];exits=[];flags=[]
 for i in range(N):
  if not state and (A[i] or b[i] or C[i]):state=True;entries.append(ds[i])
  elif state and R[i]:state=False;exits.append(ds[i])
  flags.append(state)
 return {'entries':entries,'exits':exits,'defensive_sessions':sum(flags),'defensive_pct':round(100*sum(flags)/N,2),'flags':flags}
base=run(B);assert base['entries']==[r['date'] for r in rows if r['entry']=='True']
assert base['defensive_sessions']==1532
assert len(A)==len(C)==len(R)==N
# Rolling, past-only price features. No future data, no protected stock bank.
ret=[None]+[close[i]/close[i-1]-1 for i in range(1,N)]
ma={w:[None if i<w-1 else sum(close[i-w+1:i+1])/w for i in range(N)] for w in (50,100,150,200)}
peak=[max(close[max(0,i-125):i+1]) for i in range(N)]
conditions={
 'B_trend_50_below_200_5d':[i>=204 and all(ma[50][k]<ma[200][k] for k in range(i-4,i+1)) for i in range(N)],
 'B_trend_100_below_200_5d':[i>=204 and all(ma[100][k]<ma[200][k] for k in range(i-4,i+1)) for i in range(N)],
 'B_price_below_200_10d':[i>=208 and all(close[k]<ma[200][k] for k in range(i-9,i+1)) for i in range(N)],
 'B_125d_drawdown_12pct_3d':[i>=2 and all(close[k]/peak[k]-1<=-.12 for k in range(i-2,i+1)) for i in range(N)],
 'B_price_below_200_and_125d_dd8_3d':[i>=201 and all(close[k]<ma[200][k] and close[k]/peak[k]-1<=-.08 for k in range(i-2,i+1)) for i in range(N)],
 'B_price_below_150_and_125d_dd8_3d':[i>=151 and all(close[k]<ma[150][k] and close[k]/peak[k]-1<=-.08 for k in range(i-2,i+1)) for i in range(N)],
}
# Note: price drawdown from trailing 126-day high cannot measure a full GFC drawdown.
episodes={'GFC':('2007-10-01','2009-03-09'),'2010':('2010-04-01','2010-07-02'),'2011':('2011-04-01','2011-10-03'),'2015_16':('2015-05-01','2016-02-11'),'2018':('2018-01-01','2018-12-24'),'COVID':('2020-02-01','2020-03-23'),'2022':('2022-01-01','2022-10-12')}
def assess(label,b):
 r=run(b);r['name']=label;r['first_entry_by_episode']={name:next((d for d in r['entries'] if a<=d<=z),None) for name,(a,z) in episodes.items()}
 # Cash-vs-SPY hypothetical: next close to next close, 0% cash yield, no costs. Deliberately no investment performance claim.
 wealth=1.;buyhold=1.;maxdd=0.;high=1.
 for i in range(1,N):
  x=close[i]/close[i-1]
  buyhold*=x
  if not r['flags'][i-1]:wealth*=x
  high=max(high,wealth);maxdd=max(maxdd,1-wealth/high)
 r['hypothetical_wealth_multiple']=round(wealth,4);r['spy_buyhold_multiple']=round(buyhold,4);r['hypothetical_max_drawdown_pct']=round(100*maxdd,2)
 del r['flags'];return r
out={'status':'EXPLORATORY_NOT_CERTIFIED','method':'Only B varied; A C R1 exact source tape; price indicators computed past-only. Hypothetical next-close exposure and zero cash yield, excludes slippage, financing, dividends, costs, and intraday fills. Not independent episode validation.','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'baseline':assess('FROZEN_ABC',B),'candidates':[assess(k,v) for k,v in conditions.items()]}
path=Path('Research/Reports/MTS_B_ONLY_2008_STYLE_EXPLORATORY_20261009.json');path.write_text(json.dumps(out,indent=2)+'\n')
for x in [out['baseline']]+out['candidates']:print(x['name'],'GFC',x['first_entry_by_episode']['GFC'],'2020',x['first_entry_by_episode']['COVID'],'2022',x['first_entry_by_episode']['2022'],'cash%',x['defensive_pct'],'wealth',x['hypothetical_wealth_multiple'],'maxDD%',x['hypothetical_max_drawdown_pct'])
print('REPORT',path)
