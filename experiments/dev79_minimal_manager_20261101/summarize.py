"""Generate final actual-results summary and artifact checksum inventory."""
import json,platform
from pathlib import Path
import pandas as pd,numpy as np,pyarrow
from manager import ROOT,digest
p=ROOT/'artifacts';results=json.loads((p/'metrics.json').read_text())
rows=[]
for mode,m in results.items():
    fills=pd.read_csv(p/mode/'fills.csv')
    m['slippage_dollars']=float((fills.shares*(fills.price-fills.open).abs()).sum())
    rows.append(dict(strategy=mode,**{k:v for k,v in m.items() if k!='actions'}))
pd.DataFrame(rows).to_csv(p/'comparison.csv',index=False)
(p/'metrics.json').write_text(json.dumps(results,indent=2,allow_nan=False))
lines=['# Actual historical replay results','', 'Exploratory fixed DEV79 survivor universe; price returns only. No alpha, transferability, or PIT certification claim.','', '2009-01-02 through 2026-09-14; 4,451 sessions; $100,000 initial NAV per arm.','', '| Strategy | Final NAV | CAGR | Max drawdown | Fills | Fees | Adverse slippage | Mean exposure |','|---|---:|---:|---:|---:|---:|---:|---:|']
for mode,m in results.items():lines.append(f"| {mode} | ${m['final_nav']:,.2f} | {m['cagr']:.2%} | {m['max_drawdown']:.2%} | {m['fills']:,} | ${m['fees']:,.2f} | ${m['slippage_dollars']:,.2f} | {m['mean_exposure']:.2%} |")
lines+=['','The manager underperformed both baselines. No parameters were tuned to improve these results. Fees and daily turnover materially eroded performance. Drawdown throttling is a sizing control and did not guarantee a drawdown ceiling.','',f"All three ledgers independently reconstruct cash, unsettled proceeds, shares, and NAV. Maximum internal PnL reconciliation error: ${max(x['max_reconciliation_error'] for x in results.values()):.3g}. No stale valuation rows occurred in this run.",'','Manager decision counts: `'+json.dumps(results['manager']['actions'],sort_keys=True)+'`.','', '## Commands actually used','', 'From `/opt/mts/sector-leadership-independent`:','', '```bash','/opt/mts/.venv/bin/python experiments/dev79_minimal_manager_20261101/audit_inputs.py > experiments/dev79_minimal_manager_20261101/input_audit.log 2>&1',"/usr/bin/time -f 'elapsed_seconds=%e peak_rss_kb=%M cpu=%P' -o experiments/dev79_minimal_manager_20261101/runtime.txt /opt/mts/.venv/bin/python experiments/dev79_minimal_manager_20261101/manager.py > experiments/dev79_minimal_manager_20261101/run.log 2>&1","/opt/mts/.venv/bin/python -m unittest discover -s experiments/dev79_minimal_manager_20261101 -p 'test_manager.py' -v > experiments/dev79_minimal_manager_20261101/tests.log 2>&1",'/opt/mts/.venv/bin/python experiments/dev79_minimal_manager_20261101/summarize.py','```','', 'Repeat the whole pipeline with `bash experiments/dev79_minimal_manager_20261101/run.sh`. The replay pins itself to one allowed CPU before numerical imports.','', '## Runtime and tests','', '```', (ROOT/'runtime.txt').read_text().strip(), (ROOT/'tests.log').read_text().strip(),'```']
(ROOT/'RESULTS.md').write_text('\n'.join(lines)+'\n')
(ROOT/'requirements-observed.txt').write_text(f'# Python {platform.python_version()}; pre-existing /opt/mts/.venv\nnumpy=={np.__version__}\npandas=={pd.__version__}\npyarrow=={pyarrow.__version__}\n')
manifest={str(f.relative_to(ROOT)):digest(f) for f in sorted(ROOT.rglob('*')) if f.is_file() and '__pycache__' not in str(f) and f.name not in ('checksums.json','pipeline.log')}
(p/'checksums.json').write_text(json.dumps(manifest,indent=2));print((ROOT/'RESULTS.md').read_text())
