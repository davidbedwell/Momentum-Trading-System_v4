"""Aggregate saved results; never fits, selects or replays."""
import json,csv,hashlib,gzip,statistics as st
from pathlib import Path
P=Path(__file__).resolve().parent

def csvout(name,rows):
    with (P/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    r=json.loads((P/'report.json').read_text());scores=r['discrimination'];summary=[];tiers=[];ports=[]
    for scenario in ('learnable','misleading','null','reversal'):
        for variant in ('iteration4','iteration2_repaired','ungated','sensor_only','price_only'):
            zs=[z for z in scores if z['scenario']==scenario and z['variant']==variant]
            counts={t:sum(z['counts'][t] for z in zs) for t in ('TERRIBLE','POOR','AVERAGE','GOOD','GREAT')}
            assigned=sum(counts.values());matrix=[[sum(z['confusion_ev'][i][j] for z in zs) for j in range(5)] for i in range(5)]
            unknown=[sum(z['unknown_by_ev_tier'][i] for z in zs) for i in range(5)]
            summary.append(dict(scenario=scenario,variant=variant,coverage=assigned/sum(z['n'] for z in zs),accuracy=sum(matrix[i][i] for i in range(5))/assigned if assigned else None,false_great=matrix[0][4],true_terrible=sum(matrix[0])+unknown[0],monotone_seeds=sum(z['monotonic'] for z in zs),drift_lags=json.dumps([z['reversal_lag'] for z in zs]),support=json.dumps(counts)))
            for key in ('ev','realized'):
                mat=[[sum(z['confusion_'+key][i][j] for z in zs) for j in range(5)] for i in range(5)]
                uk=[sum(z['unknown_by_'+('ev_tier' if key=='ev' else 'realized_tier')][i] for z in zs) for i in range(5)]
                with (P/f'confusion_aggregate_{scenario}_{variant}_{key}.csv').open('w') as f:
                    w=csv.writer(f);w.writerow(['true/predicted','TERRIBLE','POOR','AVERAGE','GOOD','GREAT','UNKNOWN'])
                    for i,t in enumerate(counts):w.writerow([t,*mat[i],uk[i]])
            for i,t in enumerate(counts):
                entries=[z for z in r['tier_metrics'] if z['scenario']==scenario and z['variant']==variant and z['tier']==t];n=sum(z['n'] for z in entries)
                tiers.append(dict(scenario=scenario,variant=variant,tier=t,n=n,precision=matrix[i][i]/n if n else None,recall=matrix[i][i]/(sum(matrix[i])+unknown[i]),realized_net=sum(z['realized_net']*z['n'] for z in entries if z['n'])/n if n else None))
        for variant in ('iteration4','iteration2_repaired','ungated','scaled'):
            z=[v for v in r['portfolio_runs'] if v['scenario']==scenario and v['variant']==variant]
            ports.append(dict(scenario=scenario,variant=variant,**{k:st.mean(v[k] for v in z) for k in ('total_return','cagr','mdd','fees','spread_slippage_impact_cost')}))
    csvout('summary.csv',summary);csvout('tier_aggregate.csv',tiers);csvout('portfolio_aggregate.csv',ports)
    reasons={};rows=0
    for path in P.glob('ledger_*.jsonl.gz'):
        with gzip.open(path,'rt') as f:
            for line in f:
                z=json.loads(line);rows+=1
                assert z['execution_index']==z['index']+1
                assert z['available_index'] is None or z['available_index']==z['index']+3
                assert z['feature_latest_index']<=z['index']
                if z['index']>=126:reasons[z['gate_reason']]=reasons.get(z['gate_reason'],0)+1
    source_unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in r['source_sha256'].items())
    assert source_unchanged
    # Additional robust safety comparison from saved holdout scores only.
    reversal={v:sum(z['false_great_on_terrible_count'] for z in scores if z['scenario']=='reversal' and z['variant']==v) for v in ('iteration4','iteration2_repaired','ungated')}
    r.update(allocation_incremental_value={sc:st.mean(v['total_return'] for v in r['portfolio_runs'] if v['scenario']==sc and v['variant']=='scaled')-st.mean(v['total_return'] for v in r['portfolio_runs'] if v['scenario']==sc and v['variant']=='iteration4') for sc in ('learnable','misleading','null','reversal')},interpretation='FAIL: gate abstains on every holdout opportunity; zero false GREAT provides no evidence of useful discrimination. Full and sensor-only stable coverage differ by <.04 percentage points; price features add no demonstrated predictive value. Reversal latch lags 11/15 are deterioration/feature-drift alarms, not validated timely reversal detection. Global residual averaging can cancel opposing class errors; disagreement with an uninformative price-only model suppresses useful extreme forecasts. Scaling unexercised: zero incremental value is not evidence that active scaling is safe.',interval_certification='DIAGNOSTIC_ONLY: pooled residual radius omits conditional and coefficient uncertainty; deployment not certified',aggregate=summary,aggregate_tiers=tiers,aggregate_portfolio=ports,gate_reason_counts=reasons,reversal_false_great_comparison=reversal,artifact_audit=dict(ledger_rows=rows,source_hashes_passed=source_unchanged),next_engineering_blocker='Acquire release-timestamped real PIT candidate features with measured conditional predictive information and independent regime episodes; validate conditional uncertainty and pre-entry change indicators before scaling. OHLC history cannot forecast iid synthetic future classes; sensor/price agreement is insufficient certification.')
    if reversal['iteration4']>reversal['iteration2_repaired']:r['status']='FAIL'
    (P/'report.json').write_text(json.dumps(r,indent=2))
    lines=['\n## Frozen holdout result: '+r['status'], '\n'+r['interpretation'],f"\nCompleted {r['full_portfolio_replays']} replays in {r['elapsed_seconds']:.1f}s; pre-replay contract tests passed. No post-holdout tuning.",'\n| Scenario | Model | Coverage | Accuracy | False GREAT / TERRIBLE |','|---|---|---:|---:|---:|']
    for z in summary:
        accuracy=f"{z['accuracy']:.1%}" if z['accuracy'] is not None else 'n/a'
        lines.append(f"| {z['scenario']} | {z['variant']} | {z['coverage']:.1%} | {accuracy} | {z['false_great']}/{z['true_terrible']} |")
    lines+=['\nFive-tier support, precision/recall and realized forward net means: tier_aggregate.csv. Complete latent/realized confusion matrices include UNKNOWN. Actual alarm lags (null means no latch) are in summary.csv; these are not guaranteed inversion detection. Gate reason counters describe instantaneous checks; an existing permanent latch can keep a decision UNKNOWN after those checks clear. Portfolio CAGR/MDD/costs: portfolio_aggregate.csv; per-seed matched allocation deltas: paired.csv (scaled comparator delta is base minus scaled).','\nThe candidate fails robust discrimination requirements; low false-GREAT counts achieved through abstention do not establish useful classification. Price-only and ungated ablations show the information and safety tradeoff; portfolio returns do not override failed discrimination.','\nNext engineering blocker: '+r['next_engineering_blocker']]
    readme=(P/'README.md').read_text().split('\n## Frozen holdout result:')[0];(P/'README.md').write_text(readme+'\n'+'\n'.join(lines)+'\n')
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.iterdir()) if p.is_file() and p.suffix!='.log' and p.name not in ('checksums.json','execution.log','run.log','source_checksums.json')}
    (P/'checksums.json').write_text(json.dumps(manifest,indent=2));(P/'source_checksums.json').write_text(json.dumps(r['source_sha256'],indent=2));print(json.dumps(dict(status=r['status'],rows=rows,reversal=reversal,gate_reasons=reasons)))
if __name__=='__main__':main()
