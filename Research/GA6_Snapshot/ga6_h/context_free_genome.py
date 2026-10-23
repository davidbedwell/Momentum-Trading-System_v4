"""GA6-H context-free chromosome grammar and reproducible recombination.
No niche label participates in genotype identity. No production GA6 imports.
"""
from dataclasses import dataclass
from hashlib import sha256
import json, math, random

FEATURES=frozenset({'momentum','reversal','acceleration','trend','volatility','volume','liquidity','relative_strength','sector_strength','breadth'})
OPS=frozenset({'AND','OR'})
TRANSFORMS=frozenset({'raw','zscore','rank'})

def validate_tree(tree):
    if not isinstance(tree,dict):raise ValueError('tree must be dict')
    if 'feature' in tree:
        if set(tree)!={'feature','window','threshold','direction','transform'}:raise ValueError('leaf schema')
        if tree['feature'] not in FEATURES or tree['transform'] not in TRANSFORMS or tree['direction'] not in ('>=','<='):raise ValueError('invalid leaf')
        if type(tree['window']) is not int or not 1<=tree['window']<=252:raise ValueError('window')
        if not math.isfinite(float(tree['threshold'])):raise ValueError('threshold')
        return [(tree['feature'],tree['window'],tree['transform'],tree['direction'],float(tree['threshold']))]
    if set(tree)!={'op','children'} or tree['op'] not in OPS or not isinstance(tree['children'],list) or len(tree['children'])<2:raise ValueError('invalid branch')
    leaves=[x for child in tree['children'] for x in validate_tree(child)]
    if len(leaves)>8:raise ValueError('too many leaves')
    if len(set(leaves))!=len(leaves):raise ValueError('duplicate identical leaves')
    return leaves

@dataclass(frozen=True)
class Genome:
    tree:dict
    rank_method:str='weighted'
    entry_threshold:float=0.0
    hold_sessions:int=20
    replace_threshold:float=0.0
    stop_loss:float=0.10
    trailing_stop:float=0.10
    target_weight:float=0.03
    def validate(self):
        leaves=validate_tree(self.tree)
        if not 1<=len(leaves)<=8 or self.rank_method not in ('weighted','count','margin'):raise ValueError('rank method')
        if not 1<=self.hold_sessions<=40:raise ValueError('hold')
        for v in (self.entry_threshold,self.replace_threshold,self.stop_loss,self.trailing_stop,self.target_weight):
            if not math.isfinite(v):raise ValueError('nonfinite gene')
        if not (-10<=self.entry_threshold<=10 and 0<=self.replace_threshold<=10):raise ValueError('threshold')
        if not (0<self.stop_loss<=1 and 0<self.trailing_stop<=1 and 0<self.target_weight<=0.10):raise ValueError('risk gene')
        return True
    def identity(self):
        self.validate()
        from dataclasses import asdict
        return sha256(json.dumps(asdict(self),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def leaf(rng,feature=None):
    return {'feature':feature or rng.choice(sorted(FEATURES)),'window':rng.choice((5,10,20,40,60,120,252)),'threshold':round(rng.uniform(-2,2),4),'direction':rng.choice(('>=','<=')),'transform':rng.choice(sorted(TRANSFORMS))}

def random_genome(rng):
    n=rng.randint(2,8)
    t={'op':rng.choice(sorted(OPS)),'children':[leaf(rng) for _ in range(n)]}
    g=Genome(t,rank_method=rng.choice(('weighted','count','margin')),hold_sessions=rng.randint(1,40),target_weight=round(rng.uniform(.01,.10),4))
    g.validate();return g

def crossover(a,b,rng):
    from dataclasses import replace
    a.validate();b.validate()
    # Crosses context-free genes; retains legal grammar and independent identity.
    al=validate_tree(a.tree);bl=validate_tree(b.tree)
    aa=a.tree['children'] if 'children' in a.tree else [a.tree]
    bb=b.tree['children'] if 'children' in b.tree else [b.tree]
    pool=aa[:max(1,len(aa)//2)]+bb[max(0,len(bb)//2):]
    if len(pool)<2:pool=aa[:1]+bb[:1]
    unique=[];seen=set()
    for x in pool:
        for l in validate_tree(x):
            if l in seen:break
        else:
            unique.append(x);seen.update(validate_tree(x))
    if len(unique)<2:unique=[leaf(rng),leaf(rng)]
    t={'op':rng.choice(sorted(OPS)),'children':unique[:8]}
    g=replace(a,tree=t,rank_method=rng.choice((a.rank_method,b.rank_method)),hold_sessions=rng.choice((a.hold_sessions,b.hold_sessions)),target_weight=rng.choice((a.target_weight,b.target_weight)))
    g.validate();return g

def mutate(g,rng):
    from dataclasses import replace
    g.validate();t=json.loads(json.dumps(g.tree))
    choices=['threshold','window','direction','transform','operator','add','remove','hold','weight','rank']
    action=rng.choice(choices)
    leaves=t.get('children',[])
    if action in ('threshold','window','direction','transform') and leaves:
        l=rng.choice(leaves)
        if 'feature' not in l:return g
        if action=='threshold':l['threshold']=round(rng.uniform(-2,2),4)
        elif action=='window':l['window']=rng.choice((5,10,20,40,60,120,252))
        elif action=='direction':l['direction']='>=' if l['direction']=='<=' else '<='
        else:l['transform']=rng.choice(sorted(TRANSFORMS))
    elif action=='operator':t['op']='AND' if t['op']=='OR' else 'OR'
    elif action=='add' and len(leaves)<8:leaves.append(leaf(rng))
    elif action=='remove' and len(leaves)>2:leaves.pop(rng.randrange(len(leaves)))
    elif action=='hold':return replace(g,hold_sessions=rng.randint(1,40))
    elif action=='weight':return replace(g,target_weight=round(rng.uniform(.01,.10),4))
    elif action=='rank':return replace(g,rank_method=rng.choice(('weighted','count','margin')))
    try:
        result=replace(g,tree=t);result.validate();return result
    except ValueError:return g
