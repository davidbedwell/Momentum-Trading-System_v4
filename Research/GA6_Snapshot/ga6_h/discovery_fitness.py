"""GA6-H discovery-only fitness contract and persistent epsilon Pareto archive.
All metrics are maximized. No CAGR, MDD or held-out performance is admitted.
"""
import math
from dataclasses import asdict
OBJECTIVES=('net_ev','ev_per_session','reliability','training_consistency','opportunity_coverage')
EPS={'net_ev':0.0001,'ev_per_session':0.00001,'reliability':0.01,
     'training_consistency':0.01,'opportunity_coverage':0.01}
def validate(metrics):
    if set(metrics)!=set(OBJECTIVES):raise ValueError('discovery fitness schema mismatch')
    if any(type(metrics[k]) not in (int,float) or not math.isfinite(metrics[k]) for k in OBJECTIVES):
        raise ValueError('nonfinite discovery fitness')
    return {k:float(metrics[k]) for k in OBJECTIVES}
def dominates(a,b):
    return all(a[k]>=b[k] for k in OBJECTIVES) and any(a[k]>b[k] for k in OBJECTIVES)
def epsilon_cell(m):
    return tuple(math.floor(m[k]/EPS[k]) for k in OBJECTIVES)
def update_archive(archive,records):
    """Keep one best representative per objective-space epsilon cell.
    Improvement requires a new non-dominated cell, not a new genome identity.
    """
    merged=list(archive)+[{'genome':g.identity(),'genome_payload':asdict(g),'metrics':validate(m)} for g,m in records]
    cells={}
    for entry in merged:
        cell=epsilon_cell(entry['metrics'])
        prior=cells.get(cell)
        if prior is None or (tuple(entry['metrics'][k] for k in OBJECTIVES),entry['genome']) > (tuple(prior['metrics'][k] for k in OBJECTIVES),prior['genome']):
            cells[cell]=entry
    candidates=list(cells.values())
    front=[e for e in candidates if not any(dominates(other['metrics'],e['metrics']) for other in candidates if other is not e)]
    front.sort(key=lambda e:(epsilon_cell(e['metrics']),e['genome']))
    old_cells={epsilon_cell(e['metrics']) for e in archive}
    new_cells={epsilon_cell(e['metrics']) for e in front}
    return front,bool(new_cells-old_cells)
