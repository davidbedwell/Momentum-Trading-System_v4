"""Family-wise multiplicity guard for genome x horizon screening.
Uses Bonferroni over all tested hypotheses; no claims of calibrated coverage.
"""
from statistics import NormalDist
import math

def adjusted_lcb(ev,se,number_of_tests,alpha=.05):
    if not all(math.isfinite(float(v)) for v in (ev,se,alpha)) or se<0 or not (0<alpha<1) or not isinstance(number_of_tests,int) or number_of_tests<1:raise ValueError('invalid inputs')
    # one-sided family-wise 95% confidence bound
    z=NormalDist().inv_cdf(1-alpha/number_of_tests)
    return float(ev-z*se)

def family_screen(points,number_of_genomes,alpha=.05):
    if not isinstance(number_of_genomes,int) or number_of_genomes<1:raise ValueError('invalid genome count')
    tests=number_of_genomes*64
    out=[]
    for p in points:
        h=int(p['horizon'])
        if not 2<=h<=65:raise ValueError('invalid horizon')
        lo=adjusted_lcb(p['ev_net'],p['se_cluster'],tests,alpha)
        out.append({**p,'lcb_fwer95':lo,'multiplicity_tests':tests,'qualified_fwer':bool(lo>0 and p.get('effective_n',0)>=30)})
    return out
