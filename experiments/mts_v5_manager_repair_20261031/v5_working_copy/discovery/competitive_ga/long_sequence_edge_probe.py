"""Longer deterministic synthetic sequence for edge viability, no GA optimization."""
import json,math,random
from datetime import date,timedelta
from engines.portfolio_replay.kernel import Bar
from . import native_competitive_evolution_trial as trial
from .native_competitive_evolution_trial import new

def make(seed=7,variant='train',sessions=128):
    rng=random.Random(seed);start=date(2026,1,2)
    regimes=([.006,-.009,.002,.008] if variant=='train' else [-.008,.004,.009,-.004])
    prices={t:100. for t in trial.TICKERS};days=[]
    for i in range(sessions):
        bars={}
        for j,t in enumerate(trial.TICKERS):
            drift=regimes[(i//32+j)%4]*(1 if j!=2 else .8)
            shock=rng.gauss(0,.011)+(rng.choice([-.08,.08]) if i in (37,73,109) and j==i%3 else 0)
            previous=prices[t];prices[t]=max(2,previous*(1+drift+shock))
            bars[t]=Bar(previous,prices[t])
        days.append(((start+timedelta(days=i)).isoformat(),bars))
    return days

def main():
    rng=random.Random(41);pop=[new(rng) for _ in range(24)]
    original_fixture=trial.fixture
    results={}
    try:
        for variant,seed in [('train',7),('unseen',91),('reordered',19)]:
            trial.fixture=lambda regime='mixed',variant=variant,seed=seed:make(seed,variant,128)
            try:results[variant]=trial.portfolio(pop)
            except Exception as e:results[variant]={'error':str(e),'type':type(e).__name__}
    finally:trial.fixture=original_fixture
    print(json.dumps({'scope':'128_SESSION_SYNTHETIC_UNOPTIMIZED_BASELINE','results':results},indent=2))
if __name__=='__main__':main()
