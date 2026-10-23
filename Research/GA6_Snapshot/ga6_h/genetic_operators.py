"""GA6-H deterministic genome operations with nested AND/OR and policy genes."""
from dataclasses import replace
import copy
from context_free_genome import Genome,leaf,validate_tree

def nodes(tree):
    out=[]
    def walk(n,path):
        out.append((path,n))
        if 'children' in n:
            for i,c in enumerate(n['children']):walk(c,path+(i,))
    walk(tree,())
    return out

def at(tree,path):
    n=tree
    for i in path:n=n['children'][i]
    return n

def tree_crossover(a,b,rng):
    """Swap subtrees between any two chromosomes, independent of context."""
    a.validate();b.validate()
    for _ in range(80):
        tree=copy.deepcopy(a.tree)
        target=rng.choice(nodes(tree))[0]
        donor_candidates=[n for p,n in nodes(b.tree) if target != () or 'children' in n]
        if not donor_candidates:continue
        donor=copy.deepcopy(rng.choice(donor_candidates))
        if not target:tree=donor
        else:
            parent=at(tree,target[:-1]);parent['children'][target[-1]]=donor
        try:
            validate_tree(tree)
            g=replace(a,tree=tree,hold_sessions=rng.choice((a.hold_sessions,b.hold_sessions)),
                      stop_loss=rng.choice((a.stop_loss,b.stop_loss)),
                      trailing_stop=rng.choice((a.trailing_stop,b.trailing_stop)),
                      replace_threshold=rng.choice((a.replace_threshold,b.replace_threshold)))
            g.validate()
            if g.identity() not in (a.identity(),b.identity()):return g
        except ValueError:continue
    return a

def structural_mutation(g,rng):
    """Single bounded mutation; no silent violation of 40-session cap."""
    g.validate()
    options=['add_leaf','replace_leaf','group','ungroup','toggle','threshold','window','feature',
             'hold','stop','trail','replacement','entry','weight','rank']
    for _ in range(200):
        action=rng.choice(options);tree=copy.deepcopy(g.tree)
        kw={}
        branches=[(p,n) for p,n in nodes(tree) if 'children' in n]
        leaves=[(p,n) for p,n in nodes(tree) if 'feature' in n]
        if action=='add_leaf':
            p,n=rng.choice(branches);n['children'].append(leaf(rng))
        elif action=='replace_leaf':
            p,n=rng.choice(leaves);new=leaf(rng)
            if not p:tree=new
            else:at(tree,p[:-1])['children'][p[-1]]=new
        elif action=='group':
            candidates=[(p,n) for p,n in branches if len(n['children'])>=3]
            if not candidates:continue
            p,n=rng.choice(candidates);i=rng.randrange(len(n['children'])-1)
            group={'op':rng.choice(('AND','OR')),'children':n['children'][i:i+2]}
            n['children'][i:i+2]=[group]
        elif action=='ungroup':
            candidates=[(p,n) for p,n in branches if p and 'children' in n and len(at(tree,p[:-1])['children'])-1+len(n['children'])>=2]
            if not candidates:continue
            p,n=rng.choice(candidates)
            parent=at(tree,p[:-1]);parent['children'][p[-1]:p[-1]+1]=n['children']
        elif action=='toggle':
            p,n=rng.choice(branches);n['op']='OR' if n['op']=='AND' else 'AND'
        elif action in ('threshold','window','feature'):
            p,n=rng.choice(leaves)
            if action=='threshold':n['threshold']=round(rng.uniform(-2,2),4)
            elif action=='window':n['window']=rng.choice((5,10,20,40,60,120,252))
            else:n['feature']=leaf(rng)['feature']
        elif action=='hold':kw['hold_sessions']=rng.randint(1,40)
        elif action=='stop':kw['stop_loss']=round(rng.uniform(.01,.5),4)
        elif action=='trail':kw['trailing_stop']=round(rng.uniform(.01,.5),4)
        elif action=='replacement':kw['replace_threshold']=round(rng.uniform(0,3),4)
        elif action=='entry':kw['entry_threshold']=round(rng.uniform(-3,3),4)
        elif action=='weight':kw['target_weight']=round(rng.uniform(.01,.10),4)
        else:kw['rank_method']=rng.choice(('weighted','count','margin'))
        try:
            new=replace(g,tree=tree,**kw);new.validate()
            if new.identity()!=g.identity():return new
        except ValueError:continue
    return g
