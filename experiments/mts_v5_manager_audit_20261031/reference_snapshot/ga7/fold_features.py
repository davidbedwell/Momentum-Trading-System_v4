"""Recompute cross-sectional ranks after investable-stock filtering.
Never reuse full-universe ranks in smaller stock-fold evaluations.
"""
import math
import numpy as np

def rank_filtered_sessions(sessions, allowed, columns):
    allowed=set(allowed)
    output=[]
    for day,bars,defense in sessions:
        selected={t:{**b,"features":b["features"].copy()} for t,b in bars.items() if t in allowed}
        if not selected:continue
        for col in columns:
            valid=[(b["features"][col],t) for t,b in selected.items()
                   if b.get("eligible",True) and math.isfinite(b["features"][col])]
            if not valid:continue
            values=np.fromiter((v for v,_ in valid),dtype=np.float64,count=len(valid))
            order=np.argsort(values,kind="stable")
            ordered=values[order]
            boundaries=np.r_[0,np.flatnonzero(ordered[1:]!=ordered[:-1])+1,len(ordered)]
            ranks=np.empty(len(valid),dtype=np.float64)
            for left,right in zip(boundaries[:-1],boundaries[1:]):
                ranks[order[left:right]]=((left+1+right)/2)/len(valid)
            for idx,(_,ticker) in enumerate(valid):
                selected[ticker]["features"][col]=float(ranks[idx])
        output.append((day,selected,defense))
    return output
