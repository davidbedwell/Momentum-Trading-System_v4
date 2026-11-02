"""Source-independent defense interface; accepts causal detector flags only.

The upstream feature/detector adapter must implement frozen market criteria.
Dates are sequence identifiers, never conditions for entering defense.
"""
from ga6.abc_b1_r1_state_controller import qualify_statefully

FLAGS=('A','B','B1','C','R1_evidence')

def evaluate(rows):
    observations=list(rows)
    for row in observations:
        if not isinstance(row,dict): raise TypeError('expected observation mapping')
        for name in FLAGS:
            if name not in row or type(row[name]) is not bool:
                raise ValueError('missing or unqualified detector flag: '+name)
    return qualify_statefully(observations)
