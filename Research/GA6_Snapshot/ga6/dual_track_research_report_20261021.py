import json,sys
from pathlib import Path
sys.path.insert(0,'/opt/mts')
from ga6.dual_track_research_20261021 import rank_tracks,trade_quality
p=Path('/opt/mts/ga6/runs/ga6_production_200_v1/all_evaluations.jsonl')
rows=[json.loads(s) for s in p.open()]
generation=max(r['generation'] for r in rows)
current=[r for r in rows if r['generation']==generation]
niches=sorted(current[0]['result']['ga6_niche_evidence'])
tracks=rank_tracks(current,niches)
out=Path('/opt/mts/ga6/runs/GA6_DUAL_TRACK_REDESIGN_20261021')
out.mkdir(exist_ok=True)
summary={'generation':generation,'population':len(current),'generalist_eligible':len(tracks['generalist']),
'specialist_eligible':{n:len(v) for n,v in tracks['specialists'].items()},
'generalist_top':tracks['generalist'][:10],
'specialist_top':{n:v[:5] for n,v in tracks['specialists'].items()},
'status':'SHADOW RESEARCH RANKING ONLY; no evolution, no trade replay, no new risk enforcement',
'limitations':['Uses existing shadow trades, not cash-constrained realized portfolio fills','Existing 13 labels require PIT validation','Niche months counted from existing episode field','2-20 session target and 1%/2% portfolio loss rules require evaluator changes and tests']}
(out/'ranking_report.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k not in ('generalist_top','specialist_top')},indent=2))
assert len(tracks['generalist'])<=200
assert all(x['origin']==n for n,v in tracks['specialists'].items() for x in v)
assert trade_quality({'count':100,'episodes':20,'net_ev':.5,'log_ev':.02,'tail_5pct':-.9})['eligible']
assert not trade_quality({'count':5,'episodes':1,'net_ev':.5,'log_ev':.02,'tail_5pct':-.9})['eligible']
print('TESTS PASSED')
