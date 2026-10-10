#!/usr/bin/env python3
"""Exploratory, not certified: causal feature candidates with fixed historical R1."""
import csv,json,datetime,urllib.request,hashlib
from pathlib import Path
src=Path('/home/ubuntu/Momentum-Trading-System_v4/Research/State/MTS_ABC_DEFENSIVE_R1_STATE_TAPE_20261005.csv')
rows=list(csv.DictReader(src.open())); dates=[r['date'] for r in rows]
url='https://query1.finance.yahoo.com/v8/finance/chart/SPY?period1=1126656000&period2=1791504000&interval=1d'
j=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))['chart']['result'][0]
prices={datetime.datetime.fromtimestamp(t,datetime.timezone.utc).date().isoformat():v for t,v in zip(j['timestamp'],j['indicators']['quote'][0]['close']) if v is not None}
assert all(d in prices for d in dates), 'SPY history incomplete'
def yes(r,k):return r[k]=='True'
def ge(r,k,x):return r[k]!='' and float(r[k])>=x
def trial(label,signal):
 state=False;entries=[];exits=[];defdays=0
 for i,r in enumerate(rows):
  if not state and signal(i,r):state=True;entries.append(r['date'])
  elif state and yes(r,'R1_evidence'):state=False;exits.append(r['date'])
  defdays+=state
 return dict(label=label,entries=entries,exits=exits,defensive_sessions=defdays)
base=trial('frozen_ABC',lambda i,r:any(yes(r,k) for k in ('A','B','C')))
assert base['entries']==[r['date'] for r in rows if yes(r,'entry')]
# Pre-specified illustrative candidates; no optimization or portfolio outcome fitting.
candidates=[
 trial('B_early_neg40_80_and_funding30_80',lambda i,r:ge(r,'negfrac40_pct',.80) and ge(r,'fundingchg30_pct',.80)),
 trial('C_early_three_of_four_85',lambda i,r:sum(ge(r,k,.85) for k in ('negfrac20_pct','failed30_pct','negfrac40_pct','fundingchg30_pct'))>=3),
 trial('B_or_C_early',lambda i,r:(ge(r,'negfrac40_pct',.80) and ge(r,'fundingchg30_pct',.80)) or sum(ge(r,k,.85) for k in ('negfrac20_pct','failed30_pct','negfrac40_pct','fundingchg30_pct'))>=3),
 trial('ABC_plus_early_BC',lambda i,r:any(yes(r,k) for k in ('A','B','C')) or (ge(r,'negfrac40_pct',.80) and ge(r,'fundingchg30_pct',.80)) or sum(ge(r,k,.85) for k in ('negfrac20_pct','failed30_pct','negfrac40_pct','fundingchg30_pct'))>=3),
]
# Evaluation across known episodes; earliest entry in a declared window, plus nuisance cost.
episodes={'GFC':('2007-10-01','2009-03-09'),'2010':('2010-04-01','2010-07-02'),'2011':('2011-04-01','2011-10-03'),'2015_16':('2015-05-01','2016-02-11'),'2018':('2018-01-01','2018-12-24'),'COVID':('2020-02-01','2020-03-23'),'2022':('2022-01-01','2022-10-12')}
for c in [base]+candidates:
 c['episode_first_entry']={k:next((d for d in c['entries'] if a<=d<=b),None) for k,(a,b) in episodes.items()}
 c['entry_count']=len(c['entries']);c['defensive_share_pct']=round(100*c['defensive_sessions']/len(rows),2)
 c['episode_decline_after_entry_pct']={k:round(max(0,(prices[d]-prices[b])/prices[d]*100),2) if (d:=c['episode_first_entry'][k]) else None for k,(a,b) in episodes.items()}
out={'status':'EXPLORATORY_NOT_CERTIFIED','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'rows':len(rows),'note':'Candidate thresholds are illustrative; frozen R1 and historical features only. 3-of-4 candidate is not sustained three sessions. Episodes are descriptive and not independent validation. Endpoint metric uses specified reference trough, not a full execution backtest.','baseline':base,'candidates':candidates}
p=Path('Research/Reports/MTS_ABC_EARLIER_ENTRY_EXPLORATORY_20261009.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2)+'\n')
for c in [base]+candidates:print(c['label'],'entries',c['entry_count'],'defensive%',c['defensive_share_pct'],'GFC',c['episode_first_entry']['GFC'],'COVID',c['episode_first_entry']['COVID'],'2022',c['episode_first_entry']['2022'])
print('REPORT',p)
