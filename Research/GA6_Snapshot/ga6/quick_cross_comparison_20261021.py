"""Quick paired selector comparison on frozen GA6 generation; descriptive only."""
import json,sys,statistics
from pathlib import Path
sys.path.insert(0,'/opt/mts')
from ga6.dual_track_research_20261021 import rank_tracks
from ga6.pareto_library_20261021 import rank
p=Path('/opt/mts/ga6/runs/ga6_production_200_v1/all_evaluations.jsonl')
rows=[json.loads(s) for s in p.open()]
g=max(x['generation'] for x in rows)
rows=[x for x in rows if x['generation']==g]
tracks=rank_tracks(rows,sorted(rows[0]['result']['ga6_niche_evidence']))
items=tracks['generalist']
pareto=rank(items)[:20]
weighted=sorted(items,key=lambda x:(-x['metrics']['score'],x['id']))[:20]
byid={x['chromosome_id']:x for x in rows}
def report(selected):
    ids={x['id'] for x in selected}
    def avg(vals):return sum(vals)/len(vals) if vals else None
    results=[byid[i]['result'] for i in ids]
    metrics=[r['ga6_trade_metrics'] for r in results]
    return {'count':len(ids),'arithmetic_ev_pct':avg([m['net_ev']*100 for m in metrics]),
    'geometric_log_ev_pct':avg([m['geometric_log_ev']*100 for m in metrics]),
    'worst_5pct_mean_pct':avg([m['worst_5pct_mean']*100 for m in metrics]),
    'ev_per_session_pct':avg([m['ev_per_session']*100 for m in metrics]),
    'win_rate_pct':avg([m['win_rate']*100 for m in metrics]),
    'avg_trades':avg([m['count'] for m in metrics]),
    'portfolio_mdd_pct':avg([r['mdd_diagnostic']*100 for r in results]),
    'portfolio_cagr_pct':avg([r['cagr_diagnostic']*100 for r in results]),
    'niches':len({byid[i]['origin_niche'] for i in ids})}
both={x['id'] for x in pareto}&{x['id'] for x in weighted}
res={'generation':g,'comparison':'IN-SAMPLE DESCRIPTIVE ONLY; NOT A PERFORMANCE VALIDATION',
     'pareto_top20':report(pareto),'weighted_top20':report(weighted),
     'pareto_only':report([x for x in pareto if x['id'] not in both]),
     'weighted_only':report([x for x in weighted if x['id'] not in both]),
     'overlap':len(both)}
out=Path('/opt/mts/ga6/runs/GA6_DUAL_TRACK_REDESIGN_20261021')
out.mkdir(exist_ok=True)
(out/'quick_cross_comparison.json').write_text(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
