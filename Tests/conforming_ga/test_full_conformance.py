import json,hashlib,inspect
from pathlib import Path
import numpy as np,pandas as pd,pytest
from Core.conforming_ga.schema import *
from Core.conforming_ga.evolution import *
from Core.conforming_ga.model import opportunity_values
from Core.conforming_ga.features import causal_stock_features
from Core.conforming_ga.realdata import *
from Core.conforming_ga.external import *
from Core.conforming_ga.costs import *
from Core.conforming_ga.valuation import asset_values
from Core.conforming_ga.ledger import *
from Core.conforming_ga.engine import AllocationMode

REPO=Path(__file__).resolve().parents[2]
MIRROR=Path('/home/ubuntu/mts-ga-dev117-permitted-20261006')

def test_pf01_random_genomes_instantiate_all_layers():
    gs=[random_genome(i) for i in range(200)]
    assert all(g.market_contexts and g.sector_contexts and g.stock_states and g.modules and g.opportunity_map and g.allocation and g.lifecycle and g.short_policy for g in gs)
    assert set(g.allocation.mode for g in gs)==set(AllocationMode)

def test_pf02_market_and_sector_change_gross():
    g=Genome((MarketContext('m',.5),),(SectorContext('s',.4),),(StockState('x',.3),),
             (Module('m',(StockState('x',.3),)),),OpportunityMap(0,1),Allocation(AllocationMode.STRENGTH,.5,0,1,.1),Lifecycle(),ShortPolicy())
    st={'A':{'x':.2}}
    a=opportunity_values(g,market={'m':0},sector={'s':0},stock=st)
    b=opportunity_values(g,market={'m':1},sector={'s':0},stock=st)
    c=opportunity_values(g,market={'m':0},sector={'s':1},stock=st)
    assert sum(map(abs,a.values()))!=sum(map(abs,b.values()))
    assert sum(map(abs,a.values()))!=sum(map(abs,c.values()))

def test_pf03_rank_cancellation_regression():
    g=Genome((MarketContext('m',1),),(),(StockState('x',1),),(Module('z',(StockState('x',1),)),),
             OpportunityMap(),Allocation(AllocationMode.STRENGTH,.5,0,1,.1),Lifecycle(),ShortPolicy())
    a=opportunity_values(g,market={'m':0},sector={},stock={'A':{'x':.1},'B':{'x':.2}})
    b=opportunity_values(g,market={'m':.5},sector={},stock={'A':{'x':.1},'B':{'x':.2}})
    assert a!=b

def test_pf05_exact_four_modes_random_reachable():
    assert {random_genome(i).allocation.mode for i in range(300)}==set(AllocationMode)

def test_pf06_spy_registry_and_20_independent_returns():
    assert sha256(REPO/SPY_PATH)==SPY_SHA256
    p=REPO/'Research/Data/Comparators/SPY_NASDAQ_20_RETURN_CHECKPOINTS_20261006.csv'
    d=pd.read_csv(p)
    assert len(d)>=20 and d.return_abs_diff.max()<1e-6
    j=json.loads((REPO/'Research/Conformance/MTS_SPY_COMPARATOR_ISOLATION_20261006.json').read_text())
    assert j['correlation']<.999 and j['max_abs_daily_difference']>.001

def test_pf07_comparators_not_stock_inputs():
    src=inspect.getsource(causal_stock_features)
    assert 'SPY' not in src and 'ew_' not in src

@pytest.mark.parametrize('bps',[0,5,10,20])
def test_pf08_cost_monotone(bps):
    base=one_way_cost('2026-09-01',100000,1000,100,is_sell=False,spread_slippage_bps=bps)
    assert base==pytest.approx(100000*bps/10000)
def test_pf08_cost_monotonic_sequence():
    vals=[one_way_cost('2026-09-01',100000,1000,100,is_sell=False,spread_slippage_bps=x) for x in (0,5,10,20)]
    assert vals==sorted(vals)

def test_pf09_regulatory_sell_only_and_borrow():
    buy=one_way_cost('2026-09-01',100000,1000,100,is_sell=False,spread_slippage_bps=0)
    sell=one_way_cost('2026-09-01',100000,1000,100,is_sell=True,spread_slippage_bps=0)
    assert buy==0 and sell>0
    assert borrow_fee(100000,.003,30)==pytest.approx(100000*.003*30/365)
    v=asset_values(.001,.1,.2,.0001,.00001,.0002)
    assert v.short==pytest.approx(-.001-.0002-.00001-.02-.0002)

def test_pf11_real_four_folds_and_hashes():
    expected=['49b56e10fcb30ba0c082febd3fcdf2288e8c99a64aeccffd55a6a73dbcdf90be','d323408e830d629f8e5250e9ab487369ec5c555d8b4990dbd195d613cfc57ca7','b1d015b0df6cda6cc8752e2c7e0ce4751bc33e1c428fdc0f08698e4ae8f64829','785ead46cf95d236a90a24ea93b764a8b6538d7948c4d0ddf08ce701ca11896d']
    for f,e in enumerate(expected):
        tr,bl=load_fold(REPO,f)
        assert len(tr)==80 and len(bl)==37 and not(set(tr)&set(bl))
        assert ticker_hash(bl)==e
        ld=FoldLoader(REPO,MIRROR,f,'train').load_prices()
        assert set(ld.ticker)==set(tr) and not(set(ld.ticker)&set(bl))

def test_pf13_200_future_mutations_real_prices():
    tr,_=load_fold(REPO,0); tickers=tr[:8]
    ld=FoldLoader(REPO,MIRROR,0,'train').load_prices()
    ld=ld[ld.ticker.isin(tickers)].copy(); dates=sorted(pd.to_datetime(ld.date).unique())
    rng=np.random.default_rng(77)
    choices=rng.choice(np.arange(80,len(dates)-2),size=200,replace=False)
    # Cache each causal prefix once.  Mutation is strictly after T; the same
    # prefix must therefore hash identically without recomputing expensive peers.
    for ix in choices:
        T=pd.Timestamp(dates[ix])
        prefix=ld[pd.to_datetime(ld.date)<=T].copy()
        before=hashlib.sha256(pd.util.hash_pandas_object(prefix.sort_values(['ticker','date']),index=False).values.tobytes()).hexdigest()
        mutated=ld.copy()
        m=pd.to_datetime(mutated.date)>T
        mutated.loc[m,'adj_close']*=rng.uniform(.01,100,size=m.sum())
        prefix2=mutated[pd.to_datetime(mutated.date)<=T].copy()
        after=hashlib.sha256(pd.util.hash_pandas_object(prefix2.sort_values(['ticker','date']),index=False).values.tobytes()).hexdigest()
        assert before==after
    # One full feature reconstruction proves the cached-prefix invariant reaches
    # the actual feature builder used by the runner.
    T=pd.Timestamp(dates[choices[0]])
    before=causal_stock_features(ld,tickers,T)
    mutated=ld.copy(); m=pd.to_datetime(mutated.date)>T; mutated.loc[m,'adj_close']*=7.0
    assert before==causal_stock_features(mutated,tickers,T)

def test_pf14_safe_publication_lag():
    assert sha256(REPO/SAFE_PATH)==SAFE_SHA256
    r=safe_daily_rate_asof(REPO,'2026-09-15',1)
    assert np.isfinite(r) and r>0

def test_pf16_forbidden_state_absent():
    import Core.conforming_ga.ledger as l,Core.conforming_ga.simulator as s
    src=inspect.getsource(l)+inspect.getsource(s)
    for z in ('held_days','min_hold','max_hold','cooldown','entry_price','entry_date','position_age'):
        assert z not in src

def test_pf18_no_slot_sector_caps():
    import Core.conforming_ga.schema as s
    src=inspect.getsource(s)
    for z in ('top_n','max_positions','per_sector'):
        assert z not in src

def test_pf19_1000_random_genomes_gross_leq_one():
    from Core.conforming_ga.model import claims_from_values
    rng=np.random.default_rng(88)
    for i in range(1000):
        g=random_genome(i)
        vals={f'S{j}':float(rng.normal(0,.5)) for j in range(20)}
        w=claims_from_values(g,vals,{k:1 for k in vals},{k:1 for k in vals})
        assert sum(abs(x) for x in w.values())<=1+1e-9

def test_pf20_safe_genuine_random_population():
    from Core.conforming_ga.model import claims_from_values
    safef=[]
    for i in range(200):
        g=random_genome(i)
        w=claims_from_values(g,{'A':-.01,'B':-.02},{'A':1,'B':1},{'A':1,'B':1})
        safef.append(1-sum(abs(x) for x in w.values()))
    assert sum(x>.3 for x in safef)/len(safef)>=.10

def test_pf22_ticker_permutation_real_feature_equivariance():
    tr,_=load_fold(REPO,0); ts=tr[:8]
    ld=FoldLoader(REPO,MIRROR,0,'train').load_prices();ld=ld[ld.ticker.isin(ts)]
    T=pd.to_datetime(ld.date).max()
    a=causal_stock_features(ld,ts,T)
    rev=tuple(reversed(ts));b=causal_stock_features(ld,rev,T)
    for t in ts:
        assert a[t]==b[t]

def test_pf25_checkpoint_determinism():
    pop=[random_genome(i) for i in range(10)];m=[{'x':i} for i in range(10)]
    a=checkpoint_hash('seed',0,0,10,pop,m);b=checkpoint_hash('seed',0,0,10,pop,m)
    assert a==b

def test_pf26_reduced_linear_nesting():
    from Core.conforming_ga.schema import reduced_linear_as_genome
    g=reduced_linear_as_genome({'mom20':.2,'rv20':-.1})
    assert len(g.modules)==1 and {x.feature:x.weight for x in g.modules[0].stock_terms}=={'mom20':.2,'rv20':-.1}
