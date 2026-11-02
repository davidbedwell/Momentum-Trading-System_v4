"""Incremental source-independent defense qualification at session close.

The result of observe(close) is an order instruction for the NEXT open.
Inputs are raw causal criteria booleans, not historical date labels.
"""

class StreamingDefense:
    def __init__(self):
        self.runs={k:0 for k in ('A','B','B1','C')}
        self.recovery=0
        self.defensive=False
        self.last=None

    def observe(self, session, criteria):
        if self.last is not None and session<=self.last:
            raise ValueError('defense observations must be chronological')
        required=(*self.runs,'R1_evidence')
        for name in required:
            if name not in criteria or type(criteria[name]) is not bool:
                raise ValueError('missing or invalid criterion '+name)
        self.last=session
        for name in self.runs:
            self.runs[name]=self.runs[name]+1 if criteria[name] else 0
        triggered=tuple(name for name, minimum in (('A',5),('B',3),('B1',1),('C',3))
                        if self.runs[name]>=minimum)
        entered=exited=False
        if triggered:
            entered=not self.defensive
            self.defensive=True
            self.recovery=0
        elif self.defensive:
            self.recovery=self.recovery+1 if criteria['R1_evidence'] else 0
            if self.recovery>=3:
                self.defensive=False
                exited=True
                self.recovery=0
        else:
            self.recovery=0
        return {'session':session,'defensive_next_open':self.defensive,
                'entered':entered,'exited':exited,'triggers':triggered}
