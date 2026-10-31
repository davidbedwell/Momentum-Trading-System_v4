#!/usr/bin/env python3
"""Document provider gaps without misclassifying every missing history as delisted."""
import csv,collections,pathlib
p=pathlib.Path(__file__).resolve().parent/'universe_2019'
rows=list(csv.DictReader((p/'price_coverage_2019.csv').open()))
out=[]
for r in rows:
 if r['status']=='available':continue
 e=r['error']
 cause='yahoo_http_400_provider_rejection' if '400' in e else 'yahoo_http_404_unavailable_or_renamed' if '404' in e else 'other'
 out.append([r['symbol'],cause,e,'requires_second_price_source'])
with (p/'unresolved_price_sources_2019.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['historical_symbol','observed_failure','error','next_action']);w.writerows(out)
print('2019 price coverage:',len(rows)-len(out),'/',len(rows))
print('unresolved by observed error:',dict(collections.Counter(x[1] for x in out)))
print('Warning: 404 does not establish delisting; 400 does not establish invalid symbol.')
