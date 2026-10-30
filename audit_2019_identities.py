#!/usr/bin/env python3
"""Identity audit: prevent ticker reuse from corrupting 2019 return ranks."""
import csv,pathlib
p=pathlib.Path(__file__).resolve().parent/'universe_2019'
a={r['symbol']:r for r in csv.DictReader((p/'alphavantage_active_list_20190101.csv').open())}
probes=list(csv.DictReader((p/'same_issuer_recovery_candidates.csv').open()))
flags={'ABC':'REJECT: COR was CoreSite Realty in 2019, not AmerisourceBergen','FB':'PROVISIONAL: META is Facebook successor; verify issuer ID','ANTM':'PROVISIONAL: ELV is Anthem successor; verify issuer ID','BLL':'PROVISIONAL: BALL is Ball Corp; verify issuer ID','CTL':'PROVISIONAL: LUMN is CenturyLink successor; verify issuer ID'}
out=[]
for r in probes:
 old,new=r['historical_symbol'],r['queried_symbol']
 out.append([old,new,a.get(new,{}).get('name','not listed'),flags.get(old,'MANUAL REVIEW'),'NOT_CERTIFIED'])
with (p/'identity_audit_2019.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['historical_symbol','queried_symbol','listing_name','finding','return_status']);w.writerows(out)
for x in out:print(*x,sep=' | ')
