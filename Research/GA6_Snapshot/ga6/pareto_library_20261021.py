"""NSGA-II non-dominated selection for GA6 research library.
No production service changes. All objectives maximize.
"""
from math import isfinite

OBJECTIVES=('log_ev','ev_per_session','tail_5pct','repeatable_opportunities')

def objectives(item):
    m=item['metrics']
    # Independent months measures repeated evidence; do not reward trade count alone.
    return (float(m['log_ev']),float(m.get('ev_per_session') or 0),
            float(m['tail_5pct']),float(m['months']))

def dominates(a,b):
    return all(x>=y for x,y in zip(a,b)) and any(x>y for x,y in zip(a,b))

def non_dominated_sort(items):
    n=len(items)
    vectors=[objectives(x) for x in items]
    if any(not all(isfinite(v) for v in vec) for vec in vectors):
        raise ValueError('Nonfinite Pareto objective')
    wins=[[] for _ in items]; losses=[0]*n
    for i in range(n):
        for j in range(i+1,n):
            if dominates(vectors[i],vectors[j]):
                wins[i].append(j);losses[j]+=1
            elif dominates(vectors[j],vectors[i]):
                wins[j].append(i);losses[i]+=1
    fronts=[]; front=[i for i in range(n) if losses[i]==0]
    while front:
        fronts.append(front)
        next_front=[]
        for i in front:
            for j in wins[i]:
                losses[j]-=1
                if losses[j]==0:next_front.append(j)
        front=sorted(next_front)
    if sum(map(len,fronts))!=n:raise AssertionError('Missing candidates')
    return fronts

def crowding(front,items):
    if not front:return {}
    distance={i:0. for i in front}
    if len(front)<=2:return {i:float('inf') for i in front}
    dimensions=len(objectives(items[front[0]]))
    for k in range(dimensions):
        ordered=sorted(front,key=lambda i:(objectives(items[i])[k],items[i]['id']))
        lo=objectives(items[ordered[0]])[k];hi=objectives(items[ordered[-1]])[k]
        if hi==lo:continue
        distance[ordered[0]]=distance[ordered[-1]]=float('inf')
        for j in range(1,len(ordered)-1):
            if distance[ordered[j]]!=float('inf'):
                distance[ordered[j]]+=(objectives(items[ordered[j+1]])[k]-objectives(items[ordered[j-1]])[k])/(hi-lo)
    return distance

def rank(items):
    fronts=non_dominated_sort(items)
    result=[]
    for level,front in enumerate(fronts,1):
        distances=crowding(front,items)
        for i in sorted(front,key=lambda j:(-distances[j],items[j]['id'])):
            x=dict(items[i])
            x['pareto_front']=level
            x['crowding_distance']=distances[i] if isfinite(distances[i]) else None
            result.append(x)
    return result

def compare(items,limit=20):
    pareto=rank(items)
    weighted=sorted(items,key=lambda x:(-x['metrics']['score'],x['id']))
    p={x['id'] for x in pareto[:limit]}
    w={x['id'] for x in weighted[:limit]}
    return {'candidates':len(items),'pareto_front_one':sum(x['pareto_front']==1 for x in pareto),
            'selection_size':min(limit,len(items)),'overlap':len(p&w),
            'pareto_top':[x['id'] for x in pareto[:limit]],
            'weighted_top':[x['id'] for x in weighted[:limit]]}
