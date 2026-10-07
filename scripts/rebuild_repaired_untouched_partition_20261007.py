import csv,json,hashlib,random,collections,os
U='Reconstruction/Manifests/mts-v4-current-sp500-calibration-20260915.RECONSTRUCTED.csv'
rows=list(csv.DictReader(open(U))); assert len(rows)==503
by={r['ticker']:r for r in rows}; universe=set(by)
state=json.load(open('Research/State/MTS_FROZEN_ARCH_GA_V2_INPUT_MANIFEST_20261005.json'))
dev117=set(state['dev117']); assert len(dev117)==117
G='Reconstruction/Recovered-GitHub/october-original-code/governance/'
a1raw=json.load(open(G+'MTS_VERIFICATION_A1_FROZEN_SELECTION_20260930.json'))['a1']; a1=set(x['ticker'] if isinstance(x,dict) else x for x in a1raw)
a2raw=json.load(open(G+'MTS_V4_CAPITAL_SIZING_VERIFICATION_A2_INPUT_FROZEN_20261002.json'))['verification_a_targets']; a2=set(x['ticker'] if isinstance(x,dict) else x for x in a2raw)
a3raw=json.load(open(G+'MTS_V4_GENERAL_WINNER_RULE_VERIFICATION_A3_INPUT_FROZEN_20261002.json'))['verification_a_targets']; a3=set(x['ticker'] if isinstance(x,dict) else x for x in a3raw)
a4={'ED','EXE','FAST','GM','GRMN'} # recovered from MTS_V4_RELATIVE_CAPITAL_VERIFICATION_A4 report ticker_contribution_delta
old_a_touched=a1|a2|a3|a4
assert [len(x) for x in (a1,a2,a3,a4,old_a_touched)]==[20,20,5,5,50]
touched=dev117|old_a_touched
assert len(touched)==167 and touched<=universe
untouched=universe-touched; assert len(untouched)==336
# Full-market sector quotas for each 100-stock bank: Hamilton largest-remainder allocation.
sec_full=collections.Counter(by[t]['sector_id'] for t in universe)
raw={s:100*n/503 for s,n in sec_full.items()}; q={s:int(v) for s,v in raw.items()}
for s in sorted(raw,key=lambda s:(-(raw[s]-q[s]),s))[:100-sum(q.values())]: q[s]+=1
assert sum(q.values())==100
sec_unt=collections.Counter(by[t]['sector_id'] for t in untouched)
assert all(sec_unt[s]>=2*q[s] for s in q),(q,sec_unt)
seed='MTS_REPAIRED_UNTOUCHED_AB_20261007_V1'
rng=random.Random(int(hashlib.sha256(seed.encode()).hexdigest(),16))
A=[];B=[]
for s in sorted(q):
 pool=sorted(t for t in untouched if by[t]['sector_id']==s); rng.shuffle(pool)
 A += pool[:q[s]]; B += pool[q[s]:2*q[s]]
A=sorted(A);B=sorted(B); D=sorted(untouched-set(A)-set(B))
assert len(A)==len(B)==100 and len(D)==136 and not(set(A)&set(B))
def records(ts): return [{k:by[t][k] for k in ('security_id','ticker','sector_id','industry_id')} for t in ts]
def sha(ts): return hashlib.sha256(('\n'.join(sorted(ts))+'\n').encode()).hexdigest()
out={
 'format':'MTS_V4_REPAIRED_SCIENTIFIC_PARTITION_UNTOUCHED_AB_V1','date':'2026-10-07','status':'FROZEN_REPAIR',
 'scientific_boundary':'Original 303/100/100 partition membership file was lost. This is a new partition, not a reconstruction of the lost A/B assignment. Only demonstrably untouched canonical-universe names were eligible for new Verification A/B.',
 'canonical_universe':{'count':503,'source':U,'ticker_sha256':sha(universe)},
 'audit':{'touched_count':167,'untouched_count_before_repartition':336,'touched_dev117_count':117,'touched_old_verification_a_count':50,'old_verification_b_evidence':'No access found; historical protocols repeatedly record Verification B sealed. Because original B membership was lost, eligibility is determined by demonstrable ticker-level non-use, not presumed old-bank identity.',
          'touched_sources':['Research/State/MTS_FROZEN_ARCH_GA_V2_INPUT_MANIFEST_20261005.json:dev117',G+'MTS_VERIFICATION_A1_FROZEN_SELECTION_20260930.json:a1',G+'MTS_V4_CAPITAL_SIZING_VERIFICATION_A2_INPUT_FROZEN_20261002.json:verification_a_targets',G+'MTS_V4_GENERAL_WINNER_RULE_VERIFICATION_A3_INPUT_FROZEN_20261002.json:verification_a_targets','Research/Reports/MTS_V4_RELATIVE_CAPITAL_VERIFICATION_A4_20261002.json:ticker_contribution_delta'],
          'touched_tickers':sorted(touched),'touched_ticker_sha256':sha(touched)},
 'selection':{'eligible_pool':'canonical 503 minus demonstrably touched 167','eligible_count':336,'stratification':'GICS sector_id from canonical calibration manifest','target':'Each A/B bank independently matches the canonical 503 sector proportions using Hamilton largest-remainder quotas','randomization':'Within each sector, deterministic PRNG shuffle; first quota -> A, next quota -> B','seed':seed,'seed_sha256':hashlib.sha256(seed.encode()).hexdigest(),'sector_quotas_each_bank':dict(sorted(q.items())),'full_universe_sector_counts':dict(sorted(sec_full.items())),'eligible_sector_counts':dict(sorted(sec_unt.items()))},
 'VERIFICATION_A':records(A),'VERIFICATION_B':records(B),'DISCOVERY_UNTOUCHED':records(D),
 'counts':{'VERIFICATION_A':100,'VERIFICATION_B':100,'DISCOVERY_UNTOUCHED':136,'TOUCHED_EXCLUDED':167},
 'hashes':{'VERIFICATION_A_tickers_sha256':sha(A),'VERIFICATION_B_tickers_sha256':sha(B),'DISCOVERY_UNTOUCHED_tickers_sha256':sha(D)}
}
os.makedirs('Research/Partitions',exist_ok=True)
p='Research/Partitions/MTS_V4_REPAIRED_UNTOUCHED_PARTITION_A100_B100_DISCOVERY136_20261007.json'
open(p,'w').write(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(p); print('counts',out['counts']); print('quotas',dict(sorted(q.items()))); print('A',A); print('B',B); print('D_count',len(D))
