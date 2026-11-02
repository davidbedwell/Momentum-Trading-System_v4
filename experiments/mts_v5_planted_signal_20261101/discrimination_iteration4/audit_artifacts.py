"""Read-only replay validation; writes only audit result."""
import gzip,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
r=json.loads((P/'report.json').read_text())
assert r['execution_status']=='COMPLETE' and r['full_portfolio_replays']==32
assert r['preregister_sha256']==hashlib.sha256((P/'preregister.json').read_bytes()).hexdigest()
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in r['source_sha256'].items())
assert all(hashlib.sha256((P/p).read_bytes()).hexdigest()==h for p,h in json.loads((P/'checksums.json').read_text()).items())
n=0;buys=0
with gzip.open(P/'replays.jsonl.gz','rt') as f:
    for line in f:
        z=json.loads(line);n+=1
        for v in z['nav']:assert v[2]>=-1e-8
        for fill in z['ledger']:
            assert fill[3]>=0 and fill[5]>=0
            buys+=fill[2]=='BUY'
assert n==32 and buys==r['independent_risk_audit']['actual_buys']
assert r['independent_risk_audit']['max_candidate_modeled_loss']<=.02+1e-10
out=dict(status='PASS',replay_archives=n,actual_buys=buys,source_and_artifact_checksums=True,preregistration_unchanged=True,cash_nonnegative=True,modeled_risk_pass=True)
(P/'artifact_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
