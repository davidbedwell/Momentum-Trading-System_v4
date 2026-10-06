import numpy as np,pandas as pd
from Core.conforming_ga.g2features import G2Tape
from Core.conforming_ga.g2schema import *
from Core.conforming_ga.g2model import evaluate_g2_fields

def tape():
    T=40;N=2;dates=pd.date_range("2020-01-01",periods=T,freq="B")
    sig=np.tile(np.array([[1.0,-1.0]]),(T,1))
    stock={"signal":sig,"rv20":np.full((T,N),.02),"dist_low20":np.full((T,N),.1)}
    market={"regime":np.r_[np.full(20,-2.0),np.full(20,2.0)]}
    ex={k:np.ones((T,N))*100 for k in ("adj_close","open","high","low","close")}
    ex["volume"]=np.ones((T,N))*1e6;ex["dividends"]=np.zeros((T,N))
    return G2Tape(dates,("A","B"),stock,{},market,ex)

def conditioned_genome():
    gate_expr=op("gate","softthresh",feature("market","regime"),theta=0.0,scale=.2)
    ctx=CtxUnit(10,"market",feature("market","regime"),"sigmoid",5.0,0.0)
    app=ctxref("gate",10)
    m=StrategyModule(20,"momentum",app,feature("stock","signal"),"both",1.0,
                     feature("stock","rv20"),op("stock","abs",feature("stock","dist_low20")))
    return GenomeG2("MTS-GA-G2",(10,20),(ctx,),(),(),(m,),AggGene(),
        OppMapGene("affine",const("market",1.0),const("market",0.0)),
        LifecycleGene(const("market",1.0),0.0,const("market",0.0)),
        AllocGene("strength",const("market",1.0),1.0,1.0),
        ShortGene(False,const("gate",0.0),0.0))

def test_g2_market_context_actually_gates_stock_signal():
    g=conditioned_genome();assert validate_genome(g)==[]
    f=evaluate_g2_fields(g,tape())
    assert abs(f["E"][5,0])<.01
    assert f["E"][30,0]>.99
    assert f["E"][30,1]<-.99

def test_pf26_reduced_linear_is_nested_in_g2():
    g=reduced_linear_g2({"signal":2.0});assert validate_genome(g)==[]
    f=evaluate_g2_fields(g,tape())
    assert np.allclose(f["E"][:,0],2.0)
    assert np.allclose(f["E"][:,1],-2.0)

def test_g2_invalid_module_without_stock_leaf_rejected():
    m=StrategyModule(1,"momentum",const("gate",1),feature("market","regime"))
    g=GenomeG2("MTS-GA-G2",(1,),(),(),(),(m,),AggGene(),OppMapGene(),
      LifecycleGene(const("market",1),0,const("market",0)),AllocGene("equal",const("market",1),1,1),
      ShortGene(False,const("gate",0),0))
    assert any("no_stock_leaf" in x for x in validate_genome(g))
