import json
def chromosome_key(pair):
    return (pair[0], json.dumps(pair[1], sort_keys=True))
def validate(items):
    if not 1 <= len(items) <= 4: raise ValueError('Expected 1-4 chromosomes')
    if len(set(map(chromosome_key,items))) != len(items): raise ValueError('Duplicate chromosome')
    return tuple(items)
def combine(left,right,rng):
    pool=list({chromosome_key(x):x for x in (*validate(left),*validate(right))}.values())
    rng.shuffle(pool)
    return validate(pool[:rng.randint(1,min(4,len(pool)))])

def propose(spaces, rng):
    def random_genome(space, rng):
        return {gene.gene_id:rng.choice(gene.values) for gene in space.genes}
    if not spaces: raise ValueError('No families')
    count=rng.randint(1,4)
    items=[]
    for attempt in range(1000):
        if len(items)==count: break
        family=rng.choice(sorted(spaces))
        pair=(family,random_genome(spaces[family],rng))
        if chromosome_key(pair) not in set(map(chromosome_key,items)): items.append(pair)
    if len(items)!=count: raise ValueError('Not enough distinct candidates')
    return validate(items)
