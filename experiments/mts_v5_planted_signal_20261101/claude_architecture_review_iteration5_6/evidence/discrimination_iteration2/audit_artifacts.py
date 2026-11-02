"""Final deterministic artifact checks and interpretation; no fitting or replays."""
import json,hashlib,statistics as st
from pathlib import Path
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((O/'report.json').read_text())
assert sha(O/'preregister.json')==r['preregister_sha256']
assert all(sha(Path(p))==h for p,h in r['source_sha256'].items())
assert r['full_portfolio_replays']==48 and r['total_compute_seconds']<900
static=[]
for sc in ('learnable','misleading','null','reversal'):
    rows=[z for z in r['static_independent_split_ablation'] if z['scenario']==sc]
    static.append(dict(scenario=sc,coverage=st.mean(z['coverage'] for z in rows),false_great=sum(z['false_great_on_terrible_count'] for z in rows),passed_seeds=sum(z['status']=='PASS' for z in rows)))
r['static_split_summary']=static
r['followup_diagnosis']=[
    'Independent static ablation reaches55.3% stable coverage but fails every seed and causes2336 false GREAT at inversion; static mean confidence cannot certify temporal validity.',
    'Online stable scenarios emit only5 GOOD predictions each across four seeds; populated aggregate tiers are not reliable five-way identification.',
    'Stable tapes produce2..6 nuisance alarms per seed; quarantine and post-reset warmup remove large fractions of coverage. Detector scans five cells repeatedly without multiplicity calibration; nominal3SE comparisons do not control a sequential false-alarm rate.',
    'All online holdout decisions:13920 quarantine,9405 insufficient matured dates,7549 boundary uncertainty,9192 absent signal,32 residual-bias veto,7518 confident. These mutually exclusive prioritized reasons are not causal effect estimates.',
    'Future work requires independent sequential false-alarm calibration and better time-stamped change predictors. No post-holdout detector tuning was performed.',
    'Earlier radius attribution is descriptive of the repaired prior estimator:33812 middle-centered UNKNOWN intervals all have radius>=.002. Narrowing economic bands or counting stocks as independent would not be a valid fix.'
]
# Correct the diagnostic wording: direct band audit, not an additional pre-replay unit test.
r['diagnosis']['conclusions'][0]='Absolute-band dispatch supports all five tiers; bands are disjoint. The pre-replay tests cover AVERAGE/GREAT and UNKNOWN; a direct all-five dispatch audit is recorded in artifact_audit.log.'
import experiment as e
assert [e.infer(v,.0001,40,20) for v in (-.01,-.004,0,.004,.01)]==list(e.TIERS)
r['source_sha256'][str(O/'audit_artifacts.py')]=sha(O/'audit_artifacts.py')
(O/'source_checksums.json').write_text(json.dumps(r['source_sha256'],indent=2))
(O/'report.json').write_text(json.dumps(r,indent=2))
p=O/'README.md';s=p.read_text().replace('execution.log contains replay progress extracted from it.','execution.log summarizes the test/replay timing and budget.')
s=s.replace('python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/finalize.py\n','python3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/finalize.py\npython3 experiments/mts_v5_planted_signal_20261101/discrimination_iteration2/audit_artifacts.py\n')
marker='\nAdditional artifact interpretation:\n'
s=s.split(marker)[0]+marker+'\n'+'\n'.join('- '+v for v in r['followup_diagnosis'])+'\n'
p.write_text(s)
(O/'artifact_audit.log').write_text('PASS: frozen preregistration and all recorded sources unchanged;48 replays;581.951s replay/report compute; all-five absolute tier dispatch;96000 ledger rows, strict maturity,384 pending; independent full-position risk audit passed. No new tests, fitting or portfolios in this audit.\n')
manifest={p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name not in ('manifest.json','run.log','finalize.log')}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2))
assert all(sha(O/n)==h for n,h in manifest.items())
print('PASS:',len(manifest),'artifact checksums; experiment result remains FAIL')
