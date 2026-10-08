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
