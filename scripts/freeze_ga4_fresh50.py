import json,random,collections,hashlib
from pathlib import Path
root=Path('/home/ubuntu/mts-layered-run-20261007')
p=root/'Research/Partitions/MTS_V4_REPAIRED_UNTOUCHED_PARTITION_A100_B100_DISCOVERY136_20261007.json'
s=json.loads(p.read_text()); pool=s['DISCOVERY_UNTOUCHED']
counts=collections.Counter(x['sector_id'] for x in pool)
quota={k:50*v//136 for k,v in counts.items()}
for k in sorted(counts,key=lambda k:(-(50*counts[k]/136-quota[k]),k))[:50-sum(quota.values())]:quota[k]+=1
rng=random.Random('MTS_GA4_FRESH50_SECTOR_STRATIFIED_20261008_V1')
selected=[]
for k in sorted(counts):
 names=sorted((x for x in pool if x['sector_id']==k),key=lambda x:x['security_id'])
 rng.shuffle(names)
 selected.extend(names[:quota[k]])
selected.sort(key=lambda x:x['security_id'])
ids={x['security_id'] for x in selected}
assert len(ids)==50
assert not ids.intersection(x['security_id'] for g in ('VERIFICATION_A','VERIFICATION_B') for x in s[g])
out=root/'Research/Partitions/GA4_FRESH50_DISCOVERY_VALIDATION_FREEZE_20261008.json'
assert not out.exists(),'refusing to overwrite existing freeze'
data={'status':'FROZEN_OUTCOMES_UNOPENED','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'selection_policy_commit':'4410bcc5a05a5771443648911ccf047a3f71252f','seed':'MTS_GA4_FRESH50_SECTOR_STRATIFIED_20261008_V1','sector_quotas':quota,'members':selected,'count':50,'remaining_discovery':86,'outcomes_accessed':False}
out.write_text(json.dumps(data,indent=2)+'\n')
print('FROZEN',len(selected),'SHA256',hashlib.sha256(out.read_bytes()).hexdigest(),'SECTORS',quota)
