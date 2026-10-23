"""Validity-preserving structural genetic operators; no evaluation lookahead."""
from copy import deepcopy
from ga6.structural_evolution_v3_20261022.thresholds import calibrated
from ga5_feature_families import FAMILIES
from ga6.structural_evolution_v3_20261022.family_logic import validate


def leaves(tree):
    if 'family' in tree:
        return [tree]
    return [leaf for child in tree['children'] for leaf in leaves(child)]


def mutate_tree(tree,rng):
    tree=deepcopy(tree)
    nodes=leaves(tree)
    choice=rng.choice(('threshold','comparison','family','logic','branch'))
    leaf=rng.choice(nodes)
    if choice=='threshold':
        leaf['threshold']=calibrated(leaf['family'],rng.random())
    elif choice=='comparison':
        leaf['comparison']='>=' if leaf['comparison']=='<=' else '<='
    elif choice=='family':
        available=list(set(FAMILIES)-{n['family'] for n in nodes})
        if available:leaf['family']=rng.choice(sorted(available))
        else:leaf['threshold']=calibrated(leaf['family'],rng.random())
    elif choice=='logic':
        groups=[]
        def walk(n):
            if 'op' in n:
                groups.append(n)
                for child in n['children']:walk(child)
        walk(tree)
        group=rng.choice(groups);group['op']='OR' if group['op']=='AND' else 'AND'
    else:
        leaf['threshold']=calibrated(leaf['family'],rng.random())
        leaf['comparison']=rng.choice(('>=','<='))
    validate(tree)
    return tree


def crossover_tree(first,second,rng):
    """Recombine compatible predicates from another parent, retaining unique families."""
    child=deepcopy(first)
    other=leaves(second)
    nodes=leaves(child)
    index=rng.randrange(len(nodes))
    occupied={n['family'] for i,n in enumerate(nodes) if i!=index}
    compatible=[n for n in other if n['family'] not in occupied]
    if compatible:
        donor=rng.choice(compatible)
        nodes[index].update(deepcopy(donor))
    else:
        donor=rng.choice(other)
        if donor['family']==nodes[index]['family']:
            nodes[index].update(deepcopy(donor))
        else:
            nodes[index]['threshold']=donor['threshold']
            nodes[index]['comparison']=donor['comparison']
    validate(child)
    return child
