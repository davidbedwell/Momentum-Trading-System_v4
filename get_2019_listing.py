#!/usr/bin/env python3
import csv,pathlib,urllib.parse,urllib.request,collections
root=pathlib.Path(__file__).resolve().parent
key=(root/'secrets/alphavantage.key').read_text().strip()
url='https://www.alphavantage.co/query?'+urllib.parse.urlencode({'function':'LISTING_STATUS','date':'2019-01-01','state':'active','apikey':key})
req=urllib.request.Request(url)
raw=urllib.request.urlopen(req,timeout=45).read()
out=root/'universe_2019'/'alphavantage_active_list_20190101.csv'
out.write_bytes(raw)
with out.open() as f: rows=list(csv.DictReader(f))
print('rows',len(rows),'types',collections.Counter(r.get('assetType') for r in rows),'exchanges',collections.Counter(r.get('exchange') for r in rows).most_common(6),flush=True)
members={r['symbol'] for r in csv.DictReader((root/'universe_2019'/'members_2019_start.csv').open())}
listed={r['symbol'] for r in rows}
print('S&P membership found in AV historical listing',len(members & listed),'not found',len(members-listed),flush=True)
print('Missing examples',sorted(members-listed)[:35],flush=True)
