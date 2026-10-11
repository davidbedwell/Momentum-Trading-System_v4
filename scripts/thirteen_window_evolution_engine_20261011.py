"""Shared GA4 restored selection for 13 independent holding windows.

Evaluator-neutral: consumes completed per-horizon results; never reads protected banks.
No crash masking. Does not constitute evaluator certification or a launch runner.
"""
from scripts.run_evolution_v2_20261010 import qualify,pool_for
from scripts.evolution_active_dedup_fast_20261010 import curate
from scripts.evolution_safety_20261010 import overlap
from scripts.ga4_rolling_progress_20261011 import checkpoint

WINDOWS=((2,5),(6,10),(11,15),(16,20),(21,25),(26,30),(31,35),(36,40),(41,45),(46,50),(51,55),(56,60),(61,65))
HORIZONS=tuple(range(2,66))

def select_parents(genomes,results,domains,side='LONG',limit=20):
    """Rank by LCB95 then net EV; curate by signal diversity at 85% overlap.

    Every horizon is assigned to exactly one window; never mix window scores.
    """
    active=curate(genomes,results,domains,HORIZONS,threshold=.85)['active']
    allowed={(x['side'],x['horizon'],x['genome_hash']) for x in active}
    out={}
    for lo,hi in WINDOWS:
        niches=[]
        for h in range(lo,hi+1):
            pool=[x for x in pool_for(side,h,genomes,results,domains,limit=limit)
                  if (side,h,x[1]['genome_hash']) in allowed]
            if len(pool)>=2:niches.append((h,pool))
        out[(lo,hi)]=niches
    return out

def distinct_improvements(pending,results,prior_genomes,prior_results,domains):
    """Cross-generation signal novelty and LCB improvement for target horizon."""
    incumbents={h:pool_for('LONG',h,prior_genomes,prior_results,domains) for h in HORIZONS}
    accepted={h:[] for h in HORIZONS}
    for c in pending:
        h=c.get('target_horizon');r=results.get(c['genome_hash'])
        if h not in incumbents or not r:continue
        q=qualify(r,h)
        if not q or not r.get('signal') or r['signal']['count']<30:continue
        if any(overlap(r['signal'],old[2]['signal'])>=.85 and old[0][0]>=q[0] for old in incumbents[h]):continue
        if any(overlap(r['signal'],old['signal'])>=.85 and old['lcb95']>=q[0] for old in accepted[h]):continue
        accepted[h].append({'genome_hash':c['genome_hash'],'signal':r['signal'],'lcb95':q[0],'ev_net':q[1]})
    return accepted

def window_checkpoint(history,frontier,generation):
    return checkpoint(history,frontier,generation,step=25,window=100,patience=3)
