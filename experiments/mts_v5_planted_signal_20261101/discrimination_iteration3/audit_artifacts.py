"""Read-only comparison, ledger provenance, replay and checksum audit. No tuning."""
import json,gzip,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((O/'report.json').read_text());prior=json.loads((O.parent/'discrimination_iteration2/report.json').read_text())
assert r['execution_status']=='COMPLETE' and r['full_portfolio_replays']==48
assert r['elapsed_seconds']<900
assert sha(O/'preregister.json')==r['preregister_sha256']
for p,h in r['source_sha256'].items():assert sha(Path(p))==h,p
comparisons=0
for z in r['discrimination']:
    if z['variant']!='iteration2_repaired':continue
    old=next(v for v in prior['discrimination'] if v['seed']==z['seed'] and v['scenario']==z['scenario'] and v['variant']=='iteration2')
    for key in ('confusion_ev','confusion_realized','counts','coverage','alarms','reversal_lag'):assert z[key]==old[key],(key,z['seed'],z['scenario'])
    comparisons+=1
same_rows=0
for p in sorted(O.glob('ledger_*.jsonl.gz')):
    with gzip.open(p,'rt') as f,gzip.open(O.parent/'discrimination_iteration2'/p.name,'rt') as old:
        for a,b in zip(f,old,strict=True):
            a,b=json.loads(a),json.loads(b)
            for key in ('index','j','signal','execution_index','maturity_index','available_index','realized_net'):assert a[key]==b[key],(p.name,key)
            same_rows+=1
portfolios=buys=0
with gzip.open(O/'replays.jsonl.gz','rt') as f:
    for line in f:
        z=json.loads(line);portfolios+=1
        assert all(v[2]>=-1e-7 for v in z['nav'])
        assert all(v['modeled_equity_loss']<=.02+1e-10 for v in z['risk'] if v.get('accepted'))
        buys+=sum(v[2]=='BUY' for v in z['ledger'])
assert portfolios==48 and same_rows==96000 and comparisons==16
for z in r['portfolio_runs']:
    if z['variant'] not in ('iteration2_repaired','existing_ev10'):continue
    variant='iteration2' if z['variant']=='iteration2_repaired' else 'existing_ev10'
    old=next(v for v in prior['portfolio_runs'] if v['seed']==z['seed'] and v['scenario']==z['scenario'] and v['variant']==variant)
    for key in ('total_return','mdd','exposure'):assert abs(z[key]-old[key])<1e-12,(key,z)
audit=dict(passed=True,identical_ledger_rows=same_rows,identical_iteration2_scores=comparisons,portfolios=portfolios,buy_fills=buys,checksums_match=True,paired_comparator_portfolios_identical=True)
(O/'artifact_audit.json').write_text(json.dumps(audit,indent=2))
manifest={p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name not in ('manifest.json','execution.log','run.log','artifact_audit.log')}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(audit,indent=2))
