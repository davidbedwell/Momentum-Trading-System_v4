#!/usr/bin/env python3
"""Exploratory B-only two-stage slow-bear test; frozen A/C/R1. Not certified."""
import csv,datetime,json,hashlib,urllib.request
from pathlib import Path
s=Path('/home/ubuntu/Momentum-Trading-System_v4/Research/State/MTS_ABC_DEFENSIVE_R1_STATE_TAPE_20261005.csv')
r=list(csv.DictReader(s.open())); n=len(r); ds=[z['date'] for z in r]
assert hashlib.sha256(s.read_bytes()).hexdigest()=='e827b8beed7d3a0a0512990b5c77eb94618fb52f8739695f16509008f1f920fe'
u='https://query1.finance.yahoo.com/v8/finance/chart/SPY?period1=1126656000&period2=1791504000&interval=1d'
j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))['chart']['result'][0]
p={datetime.datetime.fromtimestamp(t,datetime.timezone.utc).date().isoformat():v for t,v in zip(j['timestamp'],j['indicators']['quote'][0]['close']) if v is not None};c=[p[d] for d in ds]
a=[x['A']=='True' for x in r];b=[x['B']=='True' for x in r];cc=[x['C']=='True' for x in r];re=[x['R1_evidence']=='True' for x in r]
ma200=[sum(c[i-199:i+1])/200 if i>=199 else None for i in range(n)]
trend=[i>=208 and all(c[k]<ma200[k] for k in range(i-9,i+1)) for i in range(n)]
def ge(row,k,t):return bool(row[k]) and float(row[k])>=t
# Confirmation is causal market-wide OFR funding stress or broad-market breadth; not credit spread/housing data.
confirm={
 'funding_percentile_70': [ge(x,'funding_pct',.70) for x in r],
 'breadth_damage_70': [ge(x,'b20_badpct',.70) for x in r],
 'funding_or_breadth_70': [ge(x,'funding_pct',.70) or ge(x,'b20_badpct',.70) for x in r],
 'funding_or_breadth_80': [ge(x,'funding_pct',.80) or ge(x,'b20_badpct',.80) for x in r],
 'funding_and_breadth_60': [ge(x,'funding_pct',.60) and ge(x,'b20_badpct',.60) for x in r],
}
def simulate(name,bnew):
 state=False;flags=[];entries=[];exits=[]
 for i in range(n):
  if not state and (a[i] or bnew[i] or cc[i]):state=True;entries.append(ds[i])
  elif state and re[i]:state=False;exits.append(ds[i])
  flags.append(state)
 wealth=1;hi=1;dd=0
 for i in range(1,n):
  if not flags[i-1]:wealth*=c[i]/c[i-1]
  hi=max(hi,wealth);dd=max(dd,1-wealth/hi)
 episodes={'GFC':('2007-10-01','2009-03-09'),'COVID':('2020-02-01','2020-03-23'),'2022':('2022-01-01','2022-10-12')}
 return dict(name=name,entries=len(entries),defensive_pct=round(sum(flags)*100/n,2),wealth_multiple=round(wealth,3),max_drawdown_pct=round(dd*100,2),first_entries={k:next((d for d in entries if lo<=d<=end),None) for k,(lo,end) in episodes.items()},all_entries=entries)
results=[simulate('frozen',b),simulate('price_only_200d_10d',trend),simulate('original_B_OR_price_only',[b[i] or trend[i] for i in range(n)])]
for name,co in confirm.items():
 for sustained in (1,3):
  sig=[trend[i] and i>=sustained-1 and all(co[k] for k in range(i-sustained+1,i+1)) for i in range(n)]
  results.append(simulate('B_two_stage_'+name+'_'+str(sustained)+'d',sig))
  results.append(simulate('original_B_OR_two_stage_'+name+'_'+str(sustained)+'d',[b[i] or sig[i] for i in range(n)]))
out={'status':'EXPLORATORY_NOT_CERTIFIED','scope':'A C R1 identical to frozen source; only B replaced','sources':{'state_tape_sha256':hashlib.sha256(s.read_bytes()).hexdigest(),'SPY':'Yahoo chart daily unadjusted close'},'warning':'OFR funding percentile and broad-market breadth are market-wide proxies, not new independent Baa credit spread or housing data. Candidate configurations are in-sample. Close-to-close next-session 0%-cash proxy omits costs, dividends and interest; future price series unavailable at decision time is not used in signals.','results':results}
assert results[0]['entries']==12 and results[0]['defensive_pct']==29.0
path=Path('Research/Reports/MTS_B_TWO_STAGE_TREND_STRESS_20261009.json');path.write_text(json.dumps(out,indent=2)+'\n')
for x in results:print(x['name'],'GFC',x['first_entries']['GFC'],'2022',x['first_entries']['2022'],'cash%',x['defensive_pct'],'wealth',x['wealth_multiple'],'DD%',x['max_drawdown_pct'])
print('REPORT',path)
