"""GA6 Pareto/weighted selector comparison, frozen existing population."""
import json,sys
from pathlib import Path
sys.path.insert(0,'/opt/mts')
from ga6.dual_track_research_20261021 import rank_tracks
from ga6.pareto_library_20261021 import compare,rank,dominates
from ga6 import pareto_library_20261021 as pl
p=Path('/opt/mts/ga6/runs/ga6_production_200_v1/all_evaluations.jsonl')
rows=[json.loads(s) for s in p.open()]
generation=max(x['generation'] for x in rows)
current=[x for x in rows if x['generation']==generation]
niches=sorted(current[0]['result']['ga6_niche_evidence'])
tracks=rank_tracks(current,niches)
report={'generation':generation,'generalist':compare(tracks['generalist']),
        'specialists':{},'status':'READ ONLY SELECTION COMPARISON; NO EVOLUTION'}
original=pl.objectives
try:
    pl.objectives=lambda x:(x['metrics']['log_ev'],x['metrics']['tail_5pct'],float(x['metrics']['months']))
    for niche,items in tracks['specialists'].items():
        report['specialists'][niche]=compare(items,min(5,len(items)))
finally:
    pl.objectives=original
out=Path('/opt/mts/ga6/runs/GA6_DUAL_TRACK_REDESIGN_20261021')
out.mkdir(exist_ok=True)
(out/'pareto_vs_weighted.json').write_text(json.dumps(report,indent=2))
assert dominates((2,1),(1,1))
assert not dominates((1,1),(2,1))
assert len(rank([{'id':'a','metrics':{'log_ev':.1,'ev_per_session':.02,'tail_5pct':-.1,'months':12}},{'id':'b','metrics':{'log_ev':.2,'ev_per_session':.01,'tail_5pct':-.2,'months':12}}]))==2
print('SELECTOR TESTS PASSED')
print(json.dumps({'generation':generation,'generalist':report['generalist'],'specialist_front_sizes':{n:r['pareto_front_one'] for n,r in report['specialists'].items()}},indent=2))
