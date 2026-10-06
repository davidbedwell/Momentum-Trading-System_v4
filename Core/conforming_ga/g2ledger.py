"""Side-explicit G2 capital ledger: LONG and SHORT are distinct risky assets."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SideState:
    value:float
    uncertainty:float=0.0
    exit_cost:float=0.0
    entry_cost:float=0.0

@dataclass(frozen=True)
class G2Move:
    source:str
    destination:str
    amount:float
    net_gain:float
    label:str

SAFE="SAFE"
def side_id(ticker,side):return f"{ticker}:{side}"
def parse_side(x):
    if x==SAFE:return (SAFE,SAFE)
    return tuple(x.rsplit(":",1))

def signed_to_alloc(weights):
    out={}
    for t,w in weights.items():
        if w>0:out[side_id(t,"LONG")]=float(w)
        elif w<0:out[side_id(t,"SHORT")]=float(-w)
    return out
def alloc_to_signed(alloc):
    out={}
    for a,w in alloc.items():
        t,s=parse_side(a)
        if t==SAFE:continue
        out[t]=out.get(t,0.0)+(float(w) if s=="LONG" else -float(w))
    return out

def move_ledger_assets(prev,target,states,*,kappa:float,lambda_u:float):
    names=sorted(set(prev)|set(target))
    st={**states,SAFE:SideState(0,0,0,0)}
    cur={k:float(prev.get(k,0.0)) for k in names}
    want={k:float(target.get(k,0.0)) for k in names}
    moves=[]
    def excess(k):return max(0.0,cur[k]-want[k])
    def deficit(k):return max(0.0,want[k]-cur[k])
    while True:
        gross=sum(cur.values());safe_now=max(0.0,1.0-gross)
        safe_want=max(0.0,1.0-sum(want.values()))
        sources=[(k,excess(k)) for k in names if excess(k)>1e-15]
        if safe_now>safe_want+1e-15:sources.append((SAFE,safe_now-safe_want))
        dests=[(k,deficit(k)) for k in names if deficit(k)>1e-15]
        if safe_now<safe_want-1e-15:dests.append((SAFE,safe_want-safe_now))
        cand=[]
        for a,ea in sources:
            for b,db in dests:
                if a==b:continue
                sa,sb=st[a],st[b]
                gain=sb.value-sa.value-kappa*(sa.exit_cost+sb.entry_cost)-lambda_u*(sa.uncertainty+sb.uncertainty)
                if gain>0:cand.append((gain,a,b,min(ea,db)))
        if not cand:break
        gain,a,b,amt=max(cand,key=lambda z:(z[0],z[1],z[2]))
        if a!=SAFE:cur[a]-=amt
        if b!=SAFE:cur[b]+=amt
        if a==SAFE:
            t,side=parse_side(b)
            label="SHORT" if side=="SHORT" and prev.get(b,0)<=1e-15 else "ENTER" if prev.get(b,0)<=1e-15 else "CONTINUE"
        elif b==SAFE:
            label="EXIT_TO_SAFE" if cur[a]<=1e-15 else "CONTINUE"
        else:label="REPLACE"
        moves.append(G2Move(a,b,amt,gain,label))
        if sum(cur.values())>1+1e-12:raise AssertionError("gross")
    return {k:v for k,v in cur.items() if v>1e-15},moves
