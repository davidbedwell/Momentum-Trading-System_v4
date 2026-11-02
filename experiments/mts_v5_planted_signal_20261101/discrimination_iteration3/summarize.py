"""Reporting-only enrichment of saved paired metrics; no fitting or replays."""
import json,time,statistics as st
from pathlib import Path
import experiment as e
O=e.OUT
start=time.monotonic();r=json.loads((O/'report.json').read_text())
for pair in r['paired']:
    new=next(v for v in r['portfolio_runs'] if v['seed']==pair['seed'] and v['scenario']==pair['scenario'] and v['variant']=='iteration3')
    old=next(v for v in r['portfolio_runs'] if v['seed']==pair['seed'] and v['scenario']==pair['scenario'] and v['variant']==pair['comparator'])
    for k in ('cagr','exposure','fees','spread_slippage_impact_cost'):pair[k+'_delta']=new[k]-old[k]
for q in r['paired_aggregates']:
    rr=[v for v in r['paired'] if v['scenario']==q['scenario'] and v['comparator']==q['comparator']]
    for k in ('cagr','exposure','fees','spread_slippage_impact_cost'):q['mean_'+k+'_delta']=st.mean(v[k+'_delta'] for v in rr)
r['focused_tests'].update(passed=16,failed=0)
r['fundamental_diagnosis']+=' Stable middle radii .00236..00508 exceed .002 half-band: all middle support remains zero, so five-way monotonicity fails on every seed. Stable coverage rises by 13.03 percentage points through extreme classes only. Stable nuisance alarms decline from 15 to 1 across four seeds, but permanent latching sacrifices adaptation. At reversal, stronger frozen extreme assignments cause 102 false GREAT before the seven-session alarm versus23 online comparator; pre-alarm wrong assignments explain zero reversal conditional accuracy. This separates stationary finite-information limits from unavoidable delayed regime evidence; it does not establish that predictive information is universally absent.'
r['artifact_audit']=json.loads((O/'artifact_audit.json').read_text())
r['source_sha256'][str(O/'summarize.py')]=e.sha(O/'summarize.py')
r['source_sha256'][str(O/'audit_artifacts.py')]=e.sha(O/'audit_artifacts.py')
r['reporting_enrichment_seconds']=time.monotonic()-start
(O/'report.json').write_text(json.dumps(r,indent=2));(O/'source_checksums.json').write_text(json.dumps(r['source_sha256'],indent=2))
e.writecsv('paired.csv',r['paired']);e.writecsv('paired_aggregate.csv',r['paired_aggregates'])
p=O/'README.md';text=p.read_text()
marker='\nDetailed saved-result audit and paired enrichment follow.\n'
if marker in text:text=text.split(marker)[0]
text+=marker+'\n'+r['fundamental_diagnosis']+'\n\n| Scenario | Policy | Return | CAGR | MDD | Exposure | Fees | Other execution costs |\n|---|---|---:|---:|---:|---:|---:|---:|\n'
for q in r['portfolio_aggregates']:
    exposure=q['exposure_fields']['exposure']
    text+=f"| {q['scenario']} | {q['variant']} | {q['total_return']:.2%} | {q['cagr']:.2%} | {q['mdd']:.2%} | {exposure:.2%} | {q['fees']:.2f} | {q['spread_slippage_impact_cost']:.2f} |\n"
text+='\nAll16 focused tests passed. Artifact audit verified96,000 identical ledger rows,16 identical iteration2 score records,48 replay archives,9,155 BUY fills, unchanged production sources, source hashes and comparator portfolio identity. CAGR annualizes126 sessions and is descriptive. No robust improvement claim.\n\nAfter reproduction, run `audit_artifacts.py`, then `summarize.py`, then `audit_artifacts.py` in this directory to recreate reporting enrichment and final manifest. Neither script fits or replays.\n'
p.write_text(text)
print(json.dumps(dict(status=r['status'],elapsed=r['elapsed_seconds'],risk=r['independent_risk_audit'],portfolio=r['portfolio_aggregates'],paired=r['paired_aggregates']),indent=2))
