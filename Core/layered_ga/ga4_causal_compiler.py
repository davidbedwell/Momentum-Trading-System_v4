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
        key = (feature, float(q))
        if not 0 <= q <= 1:
            raise ValueError('Invalid quantile')
        if key not in self._q:
            values = self.arr(feature)
            result = np.full(len(values), np.nan, dtype=float)
            finite = np.isfinite(values)
            unique = np.unique(values[finite])
            size = len(unique)
            tree = [0] * (size + 1)
            count = 0

            def insert(rank):
                while rank <= size:
                    tree[rank] += 1
                    rank += rank & -rank

            def kth(k):
                index = 0
                step = 1 << (size.bit_length() - 1) if size else 0
                while step:
                    nxt = index + step
                    if nxt <= size and tree[nxt] <= k:
                        index = nxt
                        k -= tree[nxt]
                    step >>= 1
                return float(unique[index])

            groups = self.frame.groupby(self._dates, sort=True).indices
            for day in sorted(groups):
                indices = groups[day]
                if count:
                    pos = (count - 1) * float(q)
                    lo = math.floor(pos)
                    hi = math.ceil(pos)
                    lower = kth(lo)
                    threshold = lower if lo == hi else lower * (1 - (pos - lo)) + kth(hi) * (pos - lo)
                    result[indices] = threshold
                batch = values[indices]
                batch = batch[np.isfinite(batch)]
                if len(batch):
                    ranks = np.searchsorted(unique, batch) + 1
                    for rank in ranks:
                        insert(int(rank))
                    count += len(batch)
            self._q[key] = result
        return self._q[key]
