"""Versioned, incremental Stage2 boolean search grammar; does not alter GA4."""
import hashlib,json,random

def canonical(node,arm):
    if not isinstance(node,(tuple,list)) or len(node)!=2:raise ValueError('Invalid node')
    op,children=node
    if op=='LEAF':
        if not isinstance(children,(tuple,list)) or len(children)!=2:raise ValueError('Invalid leaf')
        family,genes=children
        if not isinstance(family,str) or not isinstance(genes,(dict,tuple)):raise ValueError('Invalid leaf')
        return ('LEAF',(family,tuple(sorted(genes.items() if isinstance(genes,dict) else genes))))
    if op not in ('AND','OR') or not isinstance(children,(tuple,list)) or len(children)<2:raise ValueError('Invalid operator')
    cs=[canonical(c,arm) for c in children]
    flat=[]
    for c in cs:
        if c[0]==op:flat.extend(c[1])
        else:flat.append(c)
    if len(flat)<2:raise ValueError('Degenerate operator')
    return (op,tuple(sorted(flat,key=repr)))

def validate(node,arm):
    if arm not in ('AND_5_8','OR_2_8','GROUP_3_8'):raise ValueError('Unknown arm')
    c=canonical(node,arm);leaves=[];ops=[]
    def visit(n):
        if n[0]=='LEAF':leaves.append(n[1]);return
        ops.append(n[0]);[visit(x) for x in n[1]]
    visit(c)
    if len(set(leaves))!=len(leaves):raise ValueError('Repeated leaf')
    n=len(leaves)
    if arm=='AND_5_8' and not (5<=n<=8 and set(ops)=={'AND'}):raise ValueError('Not 5-8 AND')
    if arm=='OR_2_8' and not (2<=n<=8 and set(ops)=={'OR'}):raise ValueError('Not 2-8 OR')
    if arm=='GROUP_3_8' and not (3<=n<=8 and set(ops)=={'AND','OR'}):raise ValueError('Not mixed group')
    return c

def identity(node,arm):
    return hashlib.sha256(json.dumps([arm,validate(node,arm)],sort_keys=True,separators=(',',':')).encode()).hexdigest()

def compile_mask(node,arm,compiler):
    c=validate(node,arm)
    import numpy as np
    def visit(n):
        if n[0]=='LEAF':return np.asarray(compiler.compile(n[1][0],dict(n[1][1])),dtype=bool)
        masks=[visit(x) for x in n[1]]
        if any(m.shape!=masks[0].shape for m in masks):raise ValueError('Misaligned signals')
        return np.logical_and.reduce(masks) if n[0]=='AND' else np.logical_or.reduce(masks)
    return visit(c)

def propose(spaces,arm,rng):
    count=rng.randint(5,8) if arm=='AND_5_8' else rng.randint(2 if arm=='OR_2_8' else 3,8)
    leaves=[];seen=set()
    for _ in range(2000):
        if len(leaves)==count:break
        family=rng.choice(sorted(spaces));genes={g.gene_id:rng.choice(g.values) for g in spaces[family].genes}
        leaf=('LEAF',(family,genes));key=repr(canonical(leaf,arm))
        if key not in seen:leaves.append(leaf);seen.add(key)
    if len(leaves)!=count:raise RuntimeError('Novelty exhausted')
    if arm=='AND_5_8':node=('AND',leaves)
    elif arm=='OR_2_8':node=('OR',leaves)
    else:
        rng.shuffle(leaves);split=rng.randint(2,count-1)
        node=('AND',[('OR',leaves[:split]),*leaves[split:]]) if rng.randrange(2) else ('OR',[('AND',leaves[:split]),*leaves[split:]])
    return validate(node,arm)

def leaves_of(node):
    if node[0]=='LEAF':return [node]
    return [leaf for child in node[1] for leaf in leaves_of(child)]

def _assemble(leaves,arm,rng):
    if arm=='AND_5_8':return ('AND',leaves)
    if arm=='OR_2_8':return ('OR',leaves)
    if len(leaves)<3:raise ValueError('Grouped expression requires three leaves')
    rng.shuffle(leaves);split=rng.randint(2,len(leaves)-1)
    return ('AND',[('OR',leaves[:split]),*leaves[split:]]) if rng.randrange(2) else ('OR',[('AND',leaves[:split]),*leaves[split:]])

def mutate(node,spaces,arm,rng):
    current=validate(node,arm)
    for _ in range(128):
        leaves=[('LEAF',(x[1][0],dict(x[1][1]))) for x in leaves_of(current)]
        action=rng.choice(('add','drop','parameter','regroup'))
        if action=='add' and len(leaves)<8:
            new=leaves_of(propose(spaces,arm,rng))[0]
            leaves.append(('LEAF',(new[1][0],dict(new[1][1]))))
        elif action=='drop' and len(leaves)>(5 if arm=='AND_5_8' else 2 if arm=='OR_2_8' else 3):
            leaves.pop(rng.randrange(len(leaves)))
        elif action=='parameter':
            i=rng.randrange(len(leaves));family,genes=leaves[i][1]
            candidates=[g for g in spaces[family].genes if len(g.values)>1]
            if not candidates:continue
            gene=rng.choice(candidates);alternatives=[v for v in gene.values if v!=genes[gene.gene_id]]
            genes[gene.gene_id]=rng.choice(alternatives)
        elif action=='regroup' and arm=='GROUP_3_8':pass
        else:continue
        try:
            result=validate(_assemble(leaves,arm,rng),arm)
            if identity(result,arm)!=identity(current,arm):return result
        except ValueError:pass
    return propose(spaces,arm,rng)

def combine(left,right,spaces,arm,rng):
    left=validate(left,arm);right=validate(right,arm)
    pool={repr(x):x for x in leaves_of(left)+leaves_of(right)}
    choices=list(pool.values());rng.shuffle(choices)
    low=5 if arm=='AND_5_8' else 2 if arm=='OR_2_8' else 3
    if len(choices)<low:return propose(spaces,arm,rng)
    size=rng.randint(low,min(8,len(choices)))
    leaves=[('LEAF',(x[1][0],dict(x[1][1]))) for x in choices[:size]]
    return validate(_assemble(leaves,arm,rng),arm)
