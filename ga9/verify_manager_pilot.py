"""Verify persisted bounded synthetic manager evolution and deterministic replay."""
import argparse, hashlib, json
from collections import Counter
from dataclasses import replace
from pathlib import Path
from .manager_pilot import fixture, evaluate, Manager, ident


def verify(path):
    out=Path(path);r=json.loads((out/'report.json').read_text());p,g=fixture();m=Manager(**r['winner'])
    assert r['generations']==25 and r['population']==100 and r['workers']<=2
    rows=[json.loads((out/f'generation_{i:02}.json').read_text()) for i in range(1,26)]
    assert all(len(x['candidates'])==100 for x in rows)
    assert all(x['summary']['unique_decisions']>1 for x in rows)
    a=evaluate(p,g,m,0,756,True);saved=json.loads((out/'winner_train.json').read_text())
    assert a==saved,'deterministic replay mismatch'
    assert ident(m)==r['history'][-1]['best_id']
    # Deliberately destroy holdout inputs: training must remain identical.
    for f in p.features.values(): f[756:]=999.
    p.close[756:]*=2;p.open[756:]*=2
    assert evaluate(p,g,m,0,756,True)==saved
    def fingerprint(z): return hashlib.sha256(json.dumps(z['fills'],sort_keys=True).encode()).hexdigest()
    p,g=fixture();controls={}
    base=Manager(slots=6,reserve=.1,specialist_bias=(0.,)*6)
    groups=dict(ranking=dict(niche_bias=base.niche_bias,specialist_bias=base.specialist_bias,entry_floor=base.entry_floor),allocation=dict(size_scale=base.size_scale,score_size=base.score_size,reserve=base.reserve,risk_cap=base.risk_cap,slots=base.slots),position_management=dict(allow_add=base.allow_add,reduce_floor=base.reduce_floor,exit_floor=base.exit_floor))
    for name,changes in groups.items():
        z=evaluate(p,g,replace(m,**changes),0,756,True)
        controls[name]=dict(changed_fills=fingerprint(z)!=fingerprint(saved),metrics=z['metrics'])
        assert controls[name]['changed_fills']
    result=dict(status='PASS',candidate_slots=2500,unique_evaluations=r['unique_evaluations'],deterministic_replay=True,holdout_perturbation_preserves_training=True,control_ablations=controls,
                generation1_to_25_best_fitness_gain=r['history'][-1]['best']-r['history'][0]['best'],
                generation1_to_25_median_fitness_gain=r['history'][-1]['median']-r['history'][0]['median'],
                distinct_trade_fingerprints_per_generation=[x['summary']['unique_decisions'] for x in rows],
                actions={name:dict(Counter(f['action'] for f in json.loads((out/f'{name}.json').read_text())['fills'])) for name in ['baseline_train','winner_train','baseline_holdout','winner_holdout']})
    (out/'verification.json').write_text(json.dumps(result,indent=2))
    files=[*out.glob('*.json'),out/'fixture.npz',out/'tests.log',out/'run.log',Path(__file__),Path('ga9/manager_pilot.py'),Path('ga9/execution.py'),Path('ga9/test_manager_pilot.py')]
    (out/'sha256.json').write_text(json.dumps({str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files if f.name!='sha256.json'},indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('path');verify(ap.parse_args().path)
