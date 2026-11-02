"""Render persisted outcomes; never modifies analysis source or frozen protocol."""
from pathlib import Path
import json, hashlib
import pandas as pd
R=Path(__file__).resolve().parent;O=R/'outputs/analysis'
def table(d):
 d=d.fillna('—').astype(str)
 return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(r)+' |' for r in d.to_numpy())+'\n'
def pct(x):return f'{x*100:.2f}%'
def f(x):return f'{x:.4f}'
i=pd.concat([pd.read_csv(O/f'{s}_inference.csv') for s in ['discovery','validation']])
p=pd.concat([pd.read_csv(O/f'{s}_performance.csv') for s in ['discovery','validation']])
a=pd.concat([pd.read_csv(O/f'{s}_active_inference.csv') for s in ['discovery','validation']])
h=sum([json.loads((O/f'{s}_h4_paired.json').read_text()) for s in ['discovery','validation']],[])
audit=json.loads((O/'data_audit.json').read_text())
lines=['# Executed sector ETF experiment: STOP / no replication GO',
'Executed on 2026-10-31 using the supplied local parquet files. H1/H2/H3, cash-only H4, discovery, validation, chronological subsplits and full-period descriptive results were calculated. No sector endpoint passes the registered validation Holm threshold; all three top3 portfolios underperform SPY at both costs. Cash-only H4 improves drawdown but fails CAGR and Calmar requirements. Hybrid cash/SGOV H4 is unavailable because no SGOV series was supplied or found in the targeted readable local search. No production GO is permitted by the protocol.',
'## Integrity, sample and data limits',
'The original preregistration and acquisition source `run.py` are unchanged. Protocol SHA256: `23a49749f06cfc44c4c7f5a203e5f18cd04343d5763e7541100c4f977a2f756f`. The frozen four-hour ceiling is 14:37:02 UTC; execution completed before it. Earlier blocked reports and acquisition evidence are preserved. No paid requests, new downloads, main MTS changes, GitHub push or publication were performed.',
'**Incomplete registered sample:** the nine legacy ETFs begin 2005-09-01 and SPY begins 2005-01-03. Thus discovery 2000–2016 is evaluated only where observations and lookback exist; 2000–2004 and earlier warmup cannot be manufactured. Diagnostic early discovery is especially short. Validation covers 2017–2025. All 2026 rows are excluded before strategy calculations. XLRE and XLC enter only when observed and after the required lookback. No pre-inception fills, synthetic history or substitute indexes are used.',
'**Adjustment evidence:** all inputs have an explicit positive finite `adj_close` distinct from raw close. Dates are increasing within ticker, ticker/date keys are unique, and there are zero missing internal SPY-calendar sessions between each ticker’s first and last observed price. No adjusted opens are supplied. Sector files contain OHLCV and adjusted close, but lack dividends/split ledgers and embedded acquisition URL/timestamp. Their vendor adjustment is accepted as the supplied cache field, not independently certified or reconciled. SPY includes dividend/split fields; maximum daily residual between adjusted growth and `(close+dividend)/previous_close` is 0.000252 (reinvestment conventions/rounding can differ). See `data_audit.json` and `adjustment_diagnostics.json` for hashes, schemas and extreme daily returns.',
'**Holdout process:** discovery outputs were persisted and analysis code/discovery hashes sealed in `discovery_seal.json` before the separate explicit validation command; validation verified that seal. During discovery, the signal/label builder constructed all-date diagnostic arrays in memory before restricting persisted results to discovery; validation outcomes were not printed, examined, used to select parameters or persisted until the explicit run. This is a procedural limitation relative to strict computational isolation. The historical holdout was never independently custodial or blind. No code or parameter changes followed holdout inspection.',
'## Source observations']
source=[]
for file in audit['files']:
 for t,z in file['symbols'].items():source.append({'Ticker':t,'First observed':z['first'],'Last in source':z['last'],'Rows ≤2025':z['rows_through_2025']})
lines.append(table(pd.DataFrame(source)))
lines+=['## Timing, accounting and inference',
'Signals use observed month-end closes, trailing 1/6/12 calendar months with the latest trading close on/before the lookback date, no skip, a minimum of nine eligible sectors and deterministic ticker tie-breaks. Monthly targets execute next session close; the first exposed return is the following close-to-close return. Daily H4 uses the same one-session delay and 200 observed sessions including signal day. Holdings drift between rebalances; self-financing transaction costs apply per dollar traded, including entry and final liquidation in every reported period. Long-short spread has 200% gross / zero net target exposure; its cost counts both legs, without borrow or financing. This diagnostic is not a deployable short strategy. Cash earns zero.',
'Each strategy starts only when its required signal can be executed; SPY comparators with matched start dates are included in the performance CSV. Portfolio metrics use actual calendar elapsed time from initial close, initial wealth 1, daily net returns, annualized daily volatility and annual dollars traded divided by wealth (not half turnover). Equal-weight baseline uses observed available sectors monthly without a momentum lookback. Full-period results are descriptive. Forward prediction labels run from signal close to future month-end close; these gross spreads differ from the separately delayed, costed trading portfolios. Labels crossing split/subsplit boundaries are removed.',
'IC and gross forward-spread inference aggregates sectors by month, uses fixed six-lag Newey–West mean SE and two-sided normal p-values, and circular 12-month moving blocks, 2,000 replications, seed 20261031, percentile 95% intervals. Holm correction covers the five IC endpoints per split. Spread and active-return p-values are descriptive. Three-month labels overlap. H4 resamples paired whole daily months in 12-month blocks, preserving within-month drawdowns; bootstrap CAGR uses 252 sessions/year whereas reported point CAGR uses calendar elapsed time. H4 sign-tail p-values use a +1 finite-replication correction and Holm across its two endpoints at each reported cost; 30bps remains sensitivity.',
'## Main split prediction diagnostics']
for split in ['discovery','validation']:
 d=i[i.split==split];out=[]
 for _,z in d.iterrows():out.append({'Endpoint':z.endpoint,'Months':int(z.ic_n),'Mean IC':f(z.ic_mean),'IC block 95% CI':f'[{f(z.ic_ci_low)}, {f(z.ic_ci_high)}]','HAC p':f(z.ic_hac_p),'Holm p':f(z.ic_holm_p),'Gross forward spread':pct(z.spread_mean),'Spread HAC p':f(z.spread_hac_p),'Spread block 95% CI':f'[{pct(z.spread_ci_low)}, {pct(z.spread_ci_high)}]'})
 lines += [f'### {split}',table(pd.DataFrame(out))]
lines+=['## Net investable portfolios and cost sensitivity', 'CAGR and MDD are annual growth and signed peak-to-trough loss. Each cell is `CAGR / MDD / Calmar`. Main SPY row has its available split start; matched SPY rows in CSV provide exact comparisons for shortened discovery strategies.']
for split in ['discovery','validation']:
 out=[]
 for st in ['SPY','equal_weight','H1_top','H2_top','H3_top','H4_cash']:
  row={'Strategy':st}
  for cost in [15,30]:
   z=p[(p.split==split)&(p.strategy==st)&(p.cost_bps==cost)].iloc[0]
   row[f'{cost}bps']=f'{pct(z.cagr)} / {pct(z.mdd)} / {z.calmar:.3f}'
  out.append(row)
 lines += [f'### {split}',table(pd.DataFrame(out))]
lines+=['## Delayed, net long-short spreads and active monthly inference', 'Spread mean and intervals below are monthly net portfolio returns, after both-leg trading costs. Top3 active means compare compounded monthly returns with SPY on exactly the same daily interval.']
for split in ['discovery','validation']:
 out=[]
 for _,z in a[a.split==split].iterrows():
  out.append({'Strategy':z.strategy,'bps':int(z.cost_bps),'Months':int(z.n),'Monthly mean':pct(z['mean']),'HAC p':f(z.hac_p),'Block 95% CI':f'[{pct(z.ci_low)}, {pct(z.ci_high)}]'})
 lines += [f'### {split}',table(pd.DataFrame(out))]
lines+=['## Cash-only H4 paired inference', 'Absolute MDD improvement is SPY loss magnitude minus H4 loss magnitude, in percentage points. Relative drawdown reduction is separately used for the frozen 20% threshold.']
out=[]
for z in h:
 if z['split'] not in ['discovery','validation']:continue
 for endpoint in ['cagr_difference','absolute_mdd_improvement']:
  v=z[endpoint];out.append({'Split':z['split'],'bps':z['cost_bps'],'Endpoint':endpoint,'Block 95% CI':f'[{pct(v["ci_low"])}, {pct(v["ci_high"])}]','Sign-tail p':f(v['bootstrap_p']),'Holm p':f(v['holm_p'])})
lines.append(table(pd.DataFrame(out)))
lines+=['## Frozen decisions', 'All sector hypotheses: **STOP / no replication GO**. Validation Holm p is at least 0.4746, above 0.05. H1 discovery IC is negative at both horizons; H2 discovery IC is positive only at 1m; H3 discovery and validation IC are negative. Every fixed top3 portfolio has lower validation CAGR than SPY at both costs. A positive H2 net spread alone cannot satisfy the conjunctive rule. This combines economic underperformance with imprecise predictive evidence; it does not prove every true IC is zero.',
'Cash-only H4: **STOP / no replication GO**. At 15bps the relative MDD reduction is 23.74%, exceeding 20%, but Calmar is lower than SPY at both costs and the paired intervals do not exclude zero in the desired direction for both endpoints. Hybrid H4: **not evaluated**, missing SGOV after its actual availability; cash is not relabeled as SGOV. Missing early discovery and limited source provenance further constrain conclusions.',
'## Chronological subsplits and full descriptive results', 'All five IC endpoints, both costs, spread portfolios, baselines, matched SPY comparators, volatility, turnover and first/last return dates are retained in CSV. The compact tables below show the 15bps investable portfolios; 30bps values and full uncertainty are in the linked machine-readable artifacts.']
for split in ['discovery_early','discovery_late','validation_early','validation_late','full']:
 d=p[(p.split==split)&(p.cost_bps==15)&p.strategy.isin(['SPY','equal_weight','H1_top','H2_top','H3_top','H4_cash'])]
 out=[]
 for _,z in d.iterrows():out.append({'Strategy':z.strategy,'First return':z.first_return,'CAGR':pct(z.cagr),'MDD':pct(z.mdd),'Calmar':f(z.calmar),'Vol':pct(z.annualized_vol),'Annual turnover':f(z.annual_turnover)})
 lines += [f'### {split}',table(pd.DataFrame(out))]
lines += ['## Artifacts and reproduction',
'Run from the repository root with `/opt/mts/.venv/bin/python` (NumPy, pandas, SciPy, PyArrow):',
'```bash\n/opt/mts/.venv/bin/python -m unittest discover -s experiments/sector_etf_20261031/tests -v\n/opt/mts/.venv/bin/python experiments/sector_etf_20261031/analyze.py discovery\n/opt/mts/.venv/bin/python experiments/sector_etf_20261031/analyze.py validation\n/opt/mts/.venv/bin/python experiments/sector_etf_20261031/build_report.py\n```',
'Fourteen tests pass, covering frozen integrity, admission, delayed execution, entry/exit accounting, drifting holdings, deterministic bootstrap and Holm correction. The acquisition tests use mocked failures; their printed offline output is a test fixture, not a new acquisition attempt. Tests log: `outputs/analysis_tests.log`.',
'All outputs: [analysis directory](outputs/analysis/). Main files: [discovery inference](outputs/analysis/discovery_inference.csv), [validation inference](outputs/analysis/validation_inference.csv), [discovery performance](outputs/analysis/discovery_performance.csv), [validation performance](outputs/analysis/validation_performance.csv), [validation active/spread inference](outputs/analysis/validation_active_inference.csv), [H4 paired intervals](outputs/analysis/validation_h4_paired.json), [data audit](outputs/analysis/data_audit.json), [discovery seal](outputs/analysis/discovery_seal.json). Individual daily return/turnover paths and monthly forward diagnostics are also saved.',
'Existing limitations remain: only 9–11 related ETFs; sector classification and family-selection changes; overlapping labels; one historical holdout; retrospective vendor adjustments; zero-interest cash; no tax, impact, financing or borrow model. The shortened discovery is not the full registered sample. No retuning or deployment follows this result.']
old=R/'REPORT.md';backup=R/'outputs/REPORT_original_blocked.md'
if not backup.exists():backup.write_bytes(old.read_bytes())
old.write_text('\n\n'.join(lines)+'\n')
(R/'README.md').write_text('# Independent sector ETF experiment\n\nStatus: **EXECUTED — STOP / no replication GO**. Local adjusted-close caches support H1/H2/H3 and cash-only H4. Discovery is shortened by missing pre-September-2005 sector history; hybrid cash/SGOV H4 is unavailable. See [REPORT.md](REPORT.md) for concrete results, costs, significance and reproduction. The [frozen protocol](PREREGISTRATION.md), original acquisition source and earlier evidence are preserved.\n')
# Verify sealed inputs and discovery outputs after validation and rendering.
seal=json.loads((O/'discovery_seal.json').read_text())
assert all(hashlib.sha256((R/f).read_bytes()).hexdigest()==v for f,v in seal['hashes'].items())
manifest={'completed_utc':pd.Timestamp.now(tz='UTC').isoformat(),'discovery_seal_verified':True,'hashes':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [R/'analyze.py',R/'build_report.py',R/'REPORT.md',R/'README.md',*O.glob('*')] if f.is_file() and f.name!='completion_manifest.json'}}
(O/'completion_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Report written; discovery seal verified; completed',manifest['completed_utc'])
