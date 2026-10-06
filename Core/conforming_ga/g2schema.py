"""MTS-GA-G2 typed, growable genome schema from the frozen Claude redesign."""
from __future__ import annotations
from dataclasses import dataclass,field,asdict
from typing import Literal
import hashlib,json,math

Scope=Literal["market","sector","stock","gate"]
TRANSFORMS=("raw","ts_pct","xs_pct","zscore_ts","vol_scaled")
LOOKBACKS=(1,2,3,5,10,20,40,60,120,252)
FAMILIES=("momentum","breakout","trend","mean_reversion","volatility","volume_liquidity",
          "relative_strength","earnings","regime_structure","reversal","pullback",
          "volatility_breakout","composite_breadth","sector_relative","discovered")
AGG_MODES=("appl_weighted_sum","appl_weighted_mean","softmax","max_confidence")
ALLOC_MODES=("equal","strength","uncertainty","downside")
SIDE_MODES=("long_only","short_only","both")
SQUASHES=("sigmoid","tanh01","causal_ts_pct")
OPPMAP_MODES=("affine","causal_calibrated")
M_MAX=12;S_MAX=8;K_MAX=12;N_MAX=16

@dataclass(frozen=True)
class Expr:
    scope:Scope
    op:str
    args:tuple["Expr",...]=()
    feature:str|None=None
    transform:str="raw"
    lookback:int|None=None
    value:float|None=None
    theta:float=0.0
    scale:float=1.0
    ref_id:int|None=None

@dataclass(frozen=True)
class CtxUnit:
    innov_id:int
    scope:Literal["market","sector"]
    expr:Expr
    squash:str="sigmoid"
    a:float=1.0
    b:float=0.0

@dataclass(frozen=True)
class StateUnit:
    innov_id:int
    expr:Expr

@dataclass(frozen=True)
class StrategyModule:
    innov_id:int
    family_tag:str
    applicability:Expr
    signal:Expr
    side_mode:str="both"
    weight:float=1.0
    uncertainty:Expr|None=None
    downside:Expr|None=None

@dataclass(frozen=True)
class AggGene:
    mode:str="appl_weighted_sum"
    temp:float=1.0

@dataclass(frozen=True)
class OppMapGene:
    mode:str="affine"
    alpha:Expr|None=None
    beta:Expr|None=None
    calibration_method:str="linear"
    halflife:int=60

@dataclass(frozen=True)
class LifecycleGene:
    kappa:Expr
    lambda_u:float
    q:Expr

@dataclass(frozen=True)
class AllocGene:
    mode:str
    tau:Expr
    gamma:float
    eta:float

@dataclass(frozen=True)
class ShortGene:
    enabled:bool
    applicability:Expr
    extra_hurdle:float

@dataclass(frozen=True)
class GenomeG2:
    schema_version:str
    innovation_ids:tuple[int,...]
    market_contexts:tuple[CtxUnit,...]
    sector_contexts:tuple[CtxUnit,...]
    stock_states:tuple[StateUnit,...]
    modules:tuple[StrategyModule,...]
    aggregator:AggGene
    opportunity_map:OppMapGene
    lifecycle:LifecycleGene
    allocation:AllocGene
    short_policy:ShortGene

def const(scope:Scope,v:float)->Expr:return Expr(scope,"const",value=float(v))
def feature(scope:Scope,name:str,transform:str="raw")->Expr:return Expr(scope,"feature",feature=name,transform=transform)
def ctxref(scope:Scope,innov_id:int)->Expr:return Expr(scope,"ctxref",ref_id=int(innov_id))
def stateref(innov_id:int)->Expr:return Expr("stock","stateref",ref_id=int(innov_id))
def op(scope:Scope,name:str,*args:Expr,lookback=None,theta=0.0,scale=1.0)->Expr:
    return Expr(scope,name,tuple(args),lookback=lookback,theta=float(theta),scale=float(scale))

def _walk(e:Expr):
    yield e
    for a in e.args: yield from _walk(a)

def _contains_stock_leaf(e:Expr)->bool:
    return any(x.op=="feature" and x.scope=="stock" for x in _walk(e))

def validate_expr(e:Expr)->list[str]:
    errs=[]
    if e.transform not in TRANSFORMS:errs.append(f"bad transform {e.transform}")
    if e.lookback is not None and e.lookback not in LOOKBACKS:errs.append(f"bad lookback {e.lookback}")
    if e.op=="feature" and not e.feature:errs.append("feature missing")
    if e.op in ("ctxref","stateref") and e.ref_id is None:errs.append(f"{e.op} missing")
    if e.op=="const" and e.value is None:errs.append("const missing")
    temporal={"delta","accel","persist","rollmax","rollmin","ema","lag"}
    if e.op in temporal and (len(e.args)!=1 or e.lookback not in LOOKBACKS):errs.append(f"bad temporal {e.op}")
    unary={"neg","abs","not"}
    if e.op in unary and len(e.args)!=1:errs.append(f"bad unary {e.op}")
    binary={"add","sub","mul","safediv","min","max","and","or"}
    if e.op in binary and len(e.args)!=2:errs.append(f"bad binary {e.op}")
    if e.op=="ifsoft" and len(e.args)!=3:errs.append("bad ifsoft")
    if e.op=="softthresh" and len(e.args)!=1:errs.append("bad softthresh")
    for a in e.args:errs.extend(validate_expr(a))
    return errs

def validate_genome(g:GenomeG2)->list[str]:
    errs=[]
    if g.schema_version!="MTS-GA-G2":errs.append("schema_version")
    if len(g.market_contexts)>M_MAX:errs.append("market_context_bound")
    if len(g.sector_contexts)>S_MAX:errs.append("sector_context_bound")
    if len(g.stock_states)>K_MAX:errs.append("stock_state_bound")
    if not (1<=len(g.modules)<=N_MAX):errs.append("module_bound")
    if g.aggregator.mode not in AGG_MODES:errs.append("aggregator")
    if g.allocation.mode not in ALLOC_MODES:errs.append("allocation")
    if g.opportunity_map.mode not in OPPMAP_MODES:errs.append("oppmap")
    if g.short_policy.applicability.scope not in ("market","sector","stock","gate"):errs.append("short_app_scope")
    ids=[]
    for c in (*g.market_contexts,*g.sector_contexts):ids.append(c.innov_id);errs.extend(validate_expr(c.expr))
    for s in g.stock_states:ids.append(s.innov_id);errs.extend(validate_expr(s.expr))
    for m in g.modules:
        ids.append(m.innov_id)
        if m.family_tag not in FAMILIES:errs.append("family")
        if m.side_mode not in SIDE_MODES:errs.append("side_mode")
        if m.weight<0:errs.append("negative_module_weight")
        if not _contains_stock_leaf(m.signal):errs.append(f"module_{m.innov_id}_no_stock_leaf")
        errs.extend(validate_expr(m.applicability));errs.extend(validate_expr(m.signal))
        if m.uncertainty:errs.extend(validate_expr(m.uncertainty))
        if m.downside:errs.extend(validate_expr(m.downside))
    if len(ids)!=len(set(ids)):errs.append("duplicate_innovation_id")
    if set(ids)-set(g.innovation_ids):errs.append("innovation_registry_missing")
    # Referential integrity is part of structural validity. Crossover may only
    # produce genomes whose expression references resolve inside that genome.
    ctx_ids={c.innov_id for c in (*g.market_contexts,*g.sector_contexts)}
    state_ids={s.innov_id for s in g.stock_states}
    exprs=[]
    for c in (*g.market_contexts,*g.sector_contexts):exprs.append(c.expr)
    for s in g.stock_states:exprs.append(s.expr)
    for m in g.modules:
        exprs.extend((m.applicability,m.signal))
        if m.uncertainty is not None:exprs.append(m.uncertainty)
        if m.downside is not None:exprs.append(m.downside)
    exprs.extend((g.lifecycle.kappa,g.lifecycle.q,g.allocation.tau,g.short_policy.applicability))
    if g.opportunity_map.alpha is not None:exprs.append(g.opportunity_map.alpha)
    if g.opportunity_map.beta is not None:exprs.append(g.opportunity_map.beta)
    for e in exprs:
        for x in _walk(e):
            if x.op=="ctxref" and x.ref_id not in ctx_ids:errs.append(f"dangling_ctxref_{x.ref_id}")
            if x.op=="stateref" and x.ref_id not in state_ids:errs.append(f"dangling_stateref_{x.ref_id}")
    errs.extend(validate_expr(g.lifecycle.kappa));errs.extend(validate_expr(g.lifecycle.q))
    errs.extend(validate_expr(g.allocation.tau));errs.extend(validate_expr(g.short_policy.applicability))
    if g.lifecycle.q.scope!="market":errs.append("q_must_be_market")
    if g.allocation.tau.scope!="market":errs.append("tau_must_be_market")
    if g.lifecycle.kappa.scope not in ("market","stock"):errs.append("kappa_scope")
    if g.opportunity_map.alpha is not None and g.opportunity_map.alpha.scope!="market":errs.append("alpha_must_be_market")
    if g.opportunity_map.beta is not None and g.opportunity_map.beta.scope!="market":errs.append("beta_must_be_market")
    if g.opportunity_map.alpha:errs.extend(validate_expr(g.opportunity_map.alpha))
    if g.opportunity_map.beta:errs.extend(validate_expr(g.opportunity_map.beta))
    if not (0.5<=g.allocation.gamma<=4.0):errs.append("gamma")
    if not (0<g.allocation.eta<=1):errs.append("eta")
    if g.lifecycle.lambda_u<0 or g.short_policy.extra_hurdle<0:errs.append("negative_policy")
    return errs

def canonical(g:GenomeG2)->str:
    return json.dumps(asdict(g),sort_keys=True,separators=(",",":"),allow_nan=False)

def genome_hash(g:GenomeG2)->str:
    return hashlib.sha256(canonical(g).encode()).hexdigest()

def genome_from_canonical_g2(raw:str)->GenomeG2:
    d=json.loads(raw)
    def ex(x):
        return Expr(x["scope"],x["op"],tuple(ex(a) for a in x.get("args",())),
                    x.get("feature"),x.get("transform","raw"),x.get("lookback"),x.get("value"),
                    x.get("theta",0.0),x.get("scale",1.0),x.get("ref_id"))
    def cx(x):return CtxUnit(x["innov_id"],x["scope"],ex(x["expr"]),x.get("squash","sigmoid"),x.get("a",1.0),x.get("b",0.0))
    def st(x):return StateUnit(x["innov_id"],ex(x["expr"]))
    def mo(x):return StrategyModule(x["innov_id"],x["family_tag"],ex(x["applicability"]),ex(x["signal"]),
        x.get("side_mode","both"),x.get("weight",1.0),ex(x["uncertainty"]) if x.get("uncertainty") else None,
        ex(x["downside"]) if x.get("downside") else None)
    om=d["opportunity_map"];lc=d["lifecycle"];al=d["allocation"];sh=d["short_policy"]
    g=GenomeG2(d["schema_version"],tuple(d["innovation_ids"]),tuple(cx(x) for x in d["market_contexts"]),
      tuple(cx(x) for x in d["sector_contexts"]),tuple(st(x) for x in d["stock_states"]),tuple(mo(x) for x in d["modules"]),
      AggGene(**d["aggregator"]),OppMapGene(om["mode"],ex(om["alpha"]) if om.get("alpha") else None,ex(om["beta"]) if om.get("beta") else None,om.get("calibration_method","linear"),om.get("halflife",60)),
      LifecycleGene(ex(lc["kappa"]),lc["lambda_u"],ex(lc["q"])),AllocGene(al["mode"],ex(al["tau"]),al["gamma"],al["eta"]),
      ShortGene(sh["enabled"],ex(sh["applicability"]),sh["extra_hurdle"]))
    errs=validate_genome(g)
    if errs:raise ValueError("INVALID_CANONICAL_G2:"+",".join(errs))
    return g

def active_concept_count(g:GenomeG2)->int:
    leaves=set()
    for c in (*g.market_contexts,*g.sector_contexts):
        leaves.update((x.scope,x.feature,x.transform) for x in _walk(c.expr) if x.op=="feature")
    for s in g.stock_states:
        leaves.update((x.scope,x.feature,x.transform) for x in _walk(s.expr) if x.op=="feature")
    for m in g.modules:
        for e in (m.applicability,m.signal,m.uncertainty,m.downside):
            if e: leaves.update((x.scope,x.feature,x.transform) for x in _walk(e) if x.op=="feature")
    return len(leaves)+len(g.market_contexts)+len(g.sector_contexts)+len(g.stock_states)+len(g.modules)

def reduced_linear_g2(weights:dict[str,float])->GenomeG2:
    terms=[]
    for name,w in sorted(weights.items()):
        terms.append(op("stock","mul",feature("stock",name),const("stock",float(w))))
    sig=terms[0] if terms else const("stock",0.0)
    for t in terms[1:]:sig=op("stock","add",sig,t)
    m=StrategyModule(1,"discovered",const("gate",1.0),sig,"both",1.0,
                     feature("stock","rv20"),op("stock","abs",feature("stock","dist_low20")))
    return GenomeG2("MTS-GA-G2",(1,),(),(),(),(m,),AggGene("appl_weighted_sum",1.0),
                    OppMapGene("affine",const("market",1.0),const("market",0.0)),
                    LifecycleGene(const("market",1.0),0.0,const("market",0.0)),
                    AllocGene("strength",const("market",1.0),1.0,1.0),
                    ShortGene(False,const("gate",0.0),0.0))
