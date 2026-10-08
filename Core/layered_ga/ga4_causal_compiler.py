"""GA4 point-in-time quantiles: only observations strictly before decision date."""
from bisect import insort
import math
import numpy as np
import pandas as pd
from .stage2_compiler_v3 import VectorSignalCompiler

class CausalSignalCompiler(VectorSignalCompiler):
    def __init__(self, frame):
        super().__init__(frame)
        if 'effective_date' not in self.frame:
            raise ValueError('Missing decision dates')
        self._dates = pd.to_datetime(self.frame.effective_date, errors='raise')
        if self._dates.isna().any():
            raise ValueError('Missing decision date')

    def qthreshold(self, feature, q):
        key=(feature,float(q))
        if not 0 <= q <= 1:
            raise ValueError('Invalid quantile')
        if key not in self._q:
            values=self.arr(feature)
            result=np.full(len(values), np.nan, dtype=float)
            history=[]
            groups=self.frame.groupby(self._dates, sort=True).indices
            for day in sorted(groups):
                indices=groups[day]
                if history:
                    pos=(len(history)-1)*float(q)
                    lo=math.floor(pos);hi=math.ceil(pos)
                    threshold=history[lo] if lo==hi else history[lo]*(1-(pos-lo))+history[hi]*(pos-lo)
                    result[indices]=threshold
                for x in values[indices]:
                    if np.isfinite(x):
                        insort(history,float(x))
            self._q[key]=result
        return self._q[key]
