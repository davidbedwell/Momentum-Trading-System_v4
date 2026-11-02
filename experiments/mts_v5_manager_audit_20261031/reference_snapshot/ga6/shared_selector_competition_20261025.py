"""Capital competition without a fixed number of positions; research prototype."""

def allocate(proposals, existing, equity, settled_cash, defensive=False):
    if equity <= 0 or settled_cash < 0: raise ValueError('Invalid capital')
    if defensive: return []
    budget = min(settled_cash, equity * max(0, 1-sum(existing.values())))
    result=[]; seen=set(existing)
    for ticker, chromosome, requested_weight, quality in sorted(proposals,key=lambda p:(-p[3],p[0],p[1])):
        if ticker in seen or quality<=0 or requested_weight<=0:continue
        weight=min(requested_weight,budget/equity)
        if weight<=0:break
        result.append((ticker,chromosome,weight))
        seen.add(ticker);budget-=weight*equity
    return result

def self_test():
    proposals=[(str(i),'c'+str(i),.03,100-i) for i in range(40)]
    r=allocate(proposals,{},100000,100000)
    assert len(r)==34 and abs(sum(x[2] for x in r)-1)<1e-8
    big=allocate([('A','top',.8,100),('B','other',.5,90)],{},100000,100000)
    assert big[0][2]==.8 and abs(big[1][2]-.2)<1e-8
    assert not allocate(proposals,{},100000,100000,True)
    return 'COMPETITIVE_ALLOCATION_TEST_OK'
if __name__=='__main__':print(self_test())
