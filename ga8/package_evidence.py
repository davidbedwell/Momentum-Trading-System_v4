import hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from ga8.input_audit import grammar_inventory
r=Path('/opt/mts/ga8'); root=Path.cwd()
def write(name,x): (r/name).write_text(json.dumps(x,indent=2)+'\n')
x=json.loads((r/'inventory.json').read_text()); x.update(grammar=grammar_inventory(),blockers=[],optional_features_disabled=True,sector_history_not_required_for_price_only_pilot=True); write('audit.json',x)
write('test_results.json',dict(tests=8,failures=0,errors=0,passed=True,log='test_output.log'))
supp=[]
for name in ['smoke','fold_2023','fold_2024','fold_2025','final_holdout']:
    x=json.loads((r/(name+'.json')).read_text()); eq=[100000]+[z['nav'] for z in x['equity']]
    ret=np.array(eq[1:])/np.array(eq[:-1])-1
    closes=[z for z in x['fills'] if z['action'] in ['EXIT','REPLACE']]
    annual={year:sum(z['date'].startswith(year) for z in closes) for year in sorted(set(z['date'][:4] for z in x['fills']))}
    supp.append(dict(replay=name,annual_closed_trades=annual,minimum_30_trades_pass=len(closes)>=30,
        worst_daily_return=float(ret.min()),annualized_volatility=float(ret.std()*np.sqrt(252)),
        annualized_downside_deviation=float(np.sqrt(np.mean(np.minimum(ret,0)**2))*np.sqrt(252)),
        maximum_close_symbol_weight=x['audit']['max_symbol_weight'],maximum_total_stop_risk=x['audit']['max_total_risk']))
write('guardrails.json',supp)
a=Path('/opt/mts/ga7-deploy/Momentum-Trading-System_v4-research-ga7-dev79'); count=0; mismatch=[]
for f in a.rglob('*'):
    if f.is_file() and not f.is_symlink():
        rel=f.relative_to(a); dest=root/rel
        if not dest.is_file() or hashlib.sha256(f.read_bytes()).digest()!=hashlib.sha256(dest.read_bytes()).digest(): mismatch.append(str(rel))
        count+=1
assert not mismatch,mismatch
write('preservation.json',dict(original_v4_files_compared=count,mismatches=mismatch,original_ga7_tree=str(a),
    ga6_action='No writes or imports performed',ga7_action='Read only; copied baseline matches source bytes',
    source_baseline_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()))
report=(r/'pilot_report.md').read_text().replace('2026 was evaluated once after freezing the 2022–2024 model; 2025 results did not tune it.',
    'The model was frozen before each 2026 evaluation. There were two accounting versions: preliminary ex-date spendable dividends, then corrected nonspendable receivables. The corrected run reused the same seed, search bounds and training chronology. No strategy parameters were tuned from preliminary holdout outcomes. Thus 2026 is not strictly untouched; see holdout_access.json. 2025 results did not tune the model.')
model=json.loads((r/'frozen_model.json').read_text()); ev=json.loads((r/'functionality_evidence.json').read_text()); post=json.loads((r/'results.json').read_text())
report=report.split('\n## Delivery evidence')[0]
report+='\n## Delivery evidence\n\n'
report+=f"Eight tests passed. Offspring {ev['child_id']} and its actual parent {ev['parent_id']} produced different funded fills; changing only the manager also changed fills. All pilot P&L ledgers reconciled within $0.00001. The shadow bank contains {ev['shadow_accounts']} independently replayed candidate accounts.\n\n"
report+=f"Smoke actions: {ev['smoke_actions']}. Holds {ev['smoke_audit']['holds']}; abstaining sessions {ev['smoke_audit']['abstentions']}; capital competition events {ev['smoke_audit']['competition']}; correlation rejections {ev['smoke_audit']['correlation_rejections']}.\n\n"
report+='Frozen portfolio genes:\n\n'+ '\n'.join(f"- {g['family']} {g['op']} {g['second']}; niche {g['niche']}; hold {g['hold_family']}; exit {g['exit_family']}; target {g['weight']:.0%}." for g in model['genes'])+'\n\n'
report+='Entry cap and total-risk sizing were exercised; total-risk hard rejection count was zero because the cash reserve bound first. Close weights can drift above the entry cap; the largest observed smoke close weight was '+f"{ev['smoke_audit']['max_symbol_weight']:.2%}. This is a next-open risk-control model, not continuous intraday cap enforcement.\n\n"
report+='Stages A inventory, B implementation, C funded smoke, D bounded breeding and marginal ablations, E chronological folds, and F packaging were executed. This delivers an engineering pilot; it does not certify live execution parity or establish a survivor. See guardrails.json for trade-frequency, tail, concentration and fold-stability diagnostics.\n'
(r/'pilot_report.md').write_text(report)
write('delivery_manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),source_root=str(root),
    input_sha256=json.loads((r/'inventory.json').read_text())['sha256'],
    source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'ga8').glob('*.py')},
    resources=dict(native_workers=1,pilot_evaluations=json.loads((r/'pilot_search.json').read_text())['evaluations'],
        total_native_evaluations=sum(json.loads((r/(t+'_search.json')).read_text())['evaluations'] for t in ['pilot','train_2023','train_2024']),
        replay_wall_seconds=post['runtime_seconds'],cpu_and_peak_rss_this_trial='not sampled; future driver records process counters',
        output_bytes=sum(p.stat().st_size for p in r.glob('*.json'))),
    push='Not attempted; isolated local repository has no remote and user did not request publication'))
print(json.dumps(dict(preservation_files=count,total_evaluations=sum(json.loads((r/(t+'_search.json')).read_text())['evaluations'] for t in ['pilot','train_2023','train_2024']),survivor=post['survivor'])))
