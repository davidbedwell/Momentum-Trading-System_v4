[Reading 46 lines from start (total: 46 lines, 0 remaining)]

"""Create reproducible 80/37 stratified membership from consumed DEV117 only.

Sector metadata is contemporary, not point-in-time. This is a NEW freeze,
not a reconstruction of an earlier split. No market outcomes are read.
"""
import json,hashlib,random
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/cache/dev117_raw_aligned_v3.parquet'
SECTORS=ROOT/'Research/Runs/layered/sector_metadata_dev117_20261007.json'
DEST=ROOT/'Research/Partitions/GA4_DEV80_DEV37_FROZEN_SPLIT.json'
SEED=20261008

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def make():
    identities=pd.read_parquet(RAW,columns=['security_id','ticker']).drop_duplicates()
    if len(identities)!=117 or identities.security_id.nunique()!=117 or identities.ticker.nunique()!=117:raise ValueError('expected 117 unique security/ticker pairs')
    metadata=json.loads(SECTORS.read_text());mapping={r['ticker']:r['sector'] for r in metadata['rows']}
    if len(mapping)!=117 or set(identities.ticker)!=set(mapping):raise ValueError('incomplete sector coverage')
    buckets=defaultdict(list)
    for r in identities.itertuples(index=False):buckets[mapping[r.ticker]].append(str(r.security_id))
    # Hamilton apportionment: floor proportional quota, then largest remainder.
    exact={k:len(v)*80/117 for k,v in buckets.items()}
    quotas={k:int(exact[k]) for k in buckets}
    for k in sorted(buckets,key=lambda k:(-(exact[k]-quotas[k]),k))[:80-sum(quotas.values())]:quotas[k]+=1
    rng=random.Random(SEED);train=[];held=[]
    for sector in sorted(buckets):
        ids=sorted(buckets[sector]);rng.shuffle(ids)
        train.extend(ids[:quotas[sector]]);held.extend(ids[quotas[sector]:])
    if len(train)!=80 or len(held)!=37 or set(train)&set(held):raise AssertionError('invalid partition')
    return {'DEV80':sorted(train),'DEV37':sorted(held),'frozen_before_selection':True,
            'freeze_semantics':'NEW_FOLD_MEMBERSHIP_FROM_CONSUMED_DEV117_NOT_HISTORICAL_RECONSTRUCTION',
            'seed':SEED,'algorithm':'Hamilton proportional sector allocation + seeded shuffle within sectors',
            'sector_quotas':{k:{'total':len(buckets[k]),'DEV80':quotas[k],'DEV37':len(buckets[k])-quotas[k]} for k in sorted(buckets)},
            'source_hashes':{'raw_parquet_sha256':sha(RAW),'sector_metadata_sha256':sha(SECTORS)},
            'sector_metadata_limitation':'Yahoo 2026-10-07 sector labels, not historical PIT sector membership',
            'governance':'DEV80 design only; DEV37 sealed transport, no design feedback; DEV50, Verification A/B, BLIND17 untouched'}
if __name__=='__main__':
    data=make();DEST.parent.mkdir(parents=True,exist_ok=True)
    if DEST.exists():
        if json.loads(DEST.read_text())!=data:raise SystemExit('Existing freeze differs: refusing overwrite')
    else:DEST.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'DEV80':len(data['DEV80']),'DEV37':len(data['DEV37']),'sector_quotas':data['sector_quotas'],'freeze_sha256':sha(DEST)},indent=2))
