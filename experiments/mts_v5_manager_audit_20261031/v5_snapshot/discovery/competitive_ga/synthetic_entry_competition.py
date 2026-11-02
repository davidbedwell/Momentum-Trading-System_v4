"""Research-only GA6 entry competition; no invented expected-return scores.
Rotate equal-eligibility ownership by session and ticker to remove first-catalogue bias.
This is a deterministic fairness baseline, NOT an evolved or calibrated selector.
"""
def choose(eligible, ticker, session):
    candidates=sorted((str(cid),float(weight)) for cid,weight in eligible if float(weight)>0)
    if not candidates:return None
    if len({cid for cid,_ in candidates})!=len(candidates):raise ValueError('duplicate chromosome')
    # Stable ticker offset independent of Python's randomized hash seed.
    offset=sum((i+1)*ord(ch) for i,ch in enumerate(str(ticker)))
    return candidates[(session+offset)%len(candidates)]
