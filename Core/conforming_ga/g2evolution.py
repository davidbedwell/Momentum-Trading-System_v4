"""Family-seeded, structurally mutable evolution operators for MTS-GA-G2."""
from __future__ import annotations
from dataclasses import replace
import hashlib
import numpy as np
from .g2schema import *

STOCK_FEATURES=("ret1","ret5","ret20","ret60","ret120","ret252","residual_mom60","dist_high20","dist_high252",
 "donchian20","donchian60","ma_gap20","ma_gap50","ma_gap200","ma_slope20","ma_slope50","ma_slope200",
 "rv5","rv20","rv60","vol_compression5_60","atr_compression5_20","beta60","idio_vol60",
 "positive_day_fraction20","failed_rebound_count30","max_single_day_return20","skew60","dollar_volume20",
 "amihud20","overnight1","intraday1","volume_rel20","rsi14","pullback_high20","range_expansion5_20",
 "rel_market20","rel_market60","earnings_surprise_pct__v1","days_since_earnings__v1","earnings_event_session__v1")
MARKET_FEATURES=("spy_ret5","spy_ret20","spy_dd","spy_vol20","market_positive20","breadth_positive20","breadth_above200",
 "breadth_positive20_delta5","breadth_positive20_delta10","breadth_above200_delta5","breadth_above200_delta10",
 "sector_participation5","sector_participation20","leadership_change20","cross_sectional_dispersion20","avg_pair_corr60",
 "failed_rebound_count30","gap20","gap50","slope20","slope50","bounce_from_running_trough","sessions_since_running_trough",
 "vix","vvix","ofr_fsi","funding","credit","funding_delta5","funding_delta20","credit_delta5","credit_delta20",
 "tbill3m","tbill3m_delta20","yield_curve_10y_3m")
SECTOR_FEATURES=("peer_ret1","peer_ret20","peer_ret60","peer_rv20","peer_positive_day_fraction20",
 "peer_rel_market20","peer_breadth_positive20","peer_rel_strength20","peer_rel_strength60")

def innov(seed,label):
    return int.from_bytes(hashlib.sha256(f"{seed}|{label}".encode()).digest()[:8],"big") & ((1<<63)-1)
def _soft_market(name,theta=0.,scale=.25):return op("gate","softthresh",feature("market",name,"zscore_ts"),theta=theta,scale=scale)
def _weighted_stock(name,w=1.):
    return op("stock","mul",feature("stock",name),const("stock",w))
def _add(*xs):
    z=xs[0]
    for x in xs[1:]:z=op(z.scope,"add",z,x)
    return z

def family_signal(family:str,rng)->Expr:
    if family=="momentum":return _add(_weighted_stock("ret20"),_weighted_stock("residual_mom60"))
    if family=="breakout":return _add(_weighted_stock("dist_high252",-1),_weighted_stock("donchian60"))
    if family=="trend":return _add(_weighted_stock("ma_gap50"),_weighted_stock("ma_slope50",5))
    if family=="mean_reversion":return _add(_weighted_stock("ma_gap20",-1),_weighted_stock("ret5",-1))
    if family=="volatility":return _add(_weighted_stock("vol_compression5_60",-1),_weighted_stock("rv20",-0.5))
    if family=="volume_liquidity":return _add(_weighted_stock("volume_rel20"),_weighted_stock("amihud20",-1e7))
    if family=="relative_strength":return _add(_weighted_stock("rel_market20"),_weighted_stock("residual_mom60"))
    if family=="earnings":return _add(_weighted_stock("earnings_surprise_pct__v1",.01),_weighted_stock("ret20",.25))
    if family=="regime_structure":return op("stock","mul",feature("stock","beta60"),_soft_market("breadth_positive20"))
    if family=="reversal":return _add(_weighted_stock("ret1",-1),_weighted_stock("ret5",-0.5))
    if family=="pullback":
        return op("stock","ifsoft",_soft_market("spy_ret20"),_weighted_stock("pullback_high20",-1),const("stock",0))
    if family=="volatility_breakout":return op("stock","mul",feature("stock","range_expansion5_20"),feature("stock","ret5"))
    if family=="composite_breadth":return op("stock","mul",feature("stock","beta60"),_soft_market("breadth_positive20"))
    if family=="sector_relative":return _add(_weighted_stock("rel_market20"),_weighted_stock("ret20",.5))
    return _add(_weighted_stock(str(rng.choice(STOCK_FEATURES))),_weighted_stock(str(rng.choice(STOCK_FEATURES)),float(rng.normal())))

def family_applicability(family:str,rng)->Expr:
    choices={
      "momentum":"breadth_positive20","breakout":"breadth_positive20_delta5","trend":"gap50",
      "mean_reversion":"spy_dd","volatility":"vix","volume_liquidity":"cross_sectional_dispersion20",
      "relative_strength":"sector_participation20","earnings":"market_positive20","regime_structure":"breadth_above200",
      "reversal":"spy_vol20","pullback":"gap50","volatility_breakout":"vol_compression5_60",
      "composite_breadth":"breadth_positive20","sector_relative":"leadership_change20","discovered":"spy_ret20"}
    name=choices.get(family,"spy_ret20")
    if name=="vol_compression5_60":return op("gate","softthresh",feature("stock",name,"zscore_ts"),theta=0,scale=.5)
    return _soft_market(name)

def seed_g2(seed:int,primary_family:str|None=None)->GenomeG2:
    rng=np.random.Generator(np.random.PCG64(seed))
    fam=primary_family or str(rng.choice(FAMILIES))
    mid=innov(seed,"module1");mcid=innov(seed,"mctx");scid=innov(seed,"sctx")
    mctx=CtxUnit(mcid,"market",feature("market",str(rng.choice(("breadth_positive20","vix","gap50","funding_delta20"))),"zscore_ts"),
                 "sigmoid",float(rng.uniform(.5,2)),float(rng.normal(0,.25)))
    sctx=CtxUnit(scid,"sector",feature("sector",str(rng.choice(SECTOR_FEATURES)),"zscore_ts"),
                 "tanh01",float(rng.uniform(.5,2)),float(rng.normal(0,.25)))
    base=family_applicability(fam,rng)
    app=op("gate","and",base,ctxref("gate",mcid))
    mod=StrategyModule(mid,fam,app,family_signal(fam,rng),str(rng.choice(SIDE_MODES)),float(rng.uniform(.25,1.5)),
         op("stock","abs",feature("stock","rv20")),op("stock","abs",feature("stock","dist_low20")))
    agg=AggGene(str(rng.choice(AGG_MODES)),float(rng.uniform(.5,2)))
    om=OppMapGene("affine",const("market",float(rng.uniform(.05,1.0))),const("market",float(rng.normal(0,.002))))
    life=LifecycleGene(const("market",float(rng.uniform(.25,3))),float(rng.uniform(0,.05)),const("market",float(rng.normal(0,.01))))
    # tau is a Market-Scalar policy expression, not a Gate. Start from a positive
    # market constant; later type-safe mutation may grow it into a market expression.
    alloc=AllocGene(str(rng.choice(ALLOC_MODES)),const("market",float(rng.uniform(.05,1.0))),
                    float(rng.uniform(.5,4)),float(rng.uniform(.05,1)))
    short=ShortGene(bool(rng.integers(0,2)),_soft_market(str(rng.choice(("spy_dd","vix","gap50")))),float(rng.uniform(0,.02)))
    ids=(mcid,scid,mid)
    g=GenomeG2("MTS-GA-G2",ids,(mctx,),(sctx,),(),(mod,),agg,om,life,alloc,short)
    if validate_genome(g):raise RuntimeError(validate_genome(g))
    return g

def initial_population_g2(master_seed:str,fold:int,island:int,population_size:int):
    out=[];nf=len(FAMILIES)
    for j in range(population_size):
        seed=innov(f"{master_seed}|{fold}|{island}",j)
        out.append(seed_g2(seed,FAMILIES[j%nf]))
    min_required=int(np.floor(population_size/(2*nf)))
    counts={f:sum(any(m.family_tag==f for m in g.modules) for g in out) for f in FAMILIES}
    if any(v<min_required for v in counts.values()):raise AssertionError(("family representation",counts,min_required))
    return out

def _random_feature_expr(scope,rng):
    bank=MARKET_FEATURES if scope=="market" else SECTOR_FEATURES if scope=="sector" else STOCK_FEATURES
    return feature(scope,str(rng.choice(bank)),str(rng.choice(TRANSFORMS)))

def _expr_paths(e:Expr,prefix=()):
    out=[(prefix,e)]
    for i,a in enumerate(e.args):out.extend(_expr_paths(a,prefix+(i,)))
    return out

def _replace_at_path(e:Expr,path:tuple[int,...],new:Expr)->Expr:
    if not path:return new
    i=path[0];aa=list(e.args);aa[i]=_replace_at_path(aa[i],path[1:],new);return replace(e,args=tuple(aa))

def _random_typed_subtree(scope,rng)->Expr:
    # Type-safe replacement rooted in the same scope. It may be a leaf or a
    # newly generated one-level expression, so replacement is not synonymous
    # with leaf swap.
    leaf=_random_feature_expr(scope,rng)
    if scope in ("market","sector","stock") and rng.random()<.5:
        return op(scope,str(rng.choice(("delta","ema","lag"))),leaf,lookback=int(rng.choice(LOOKBACKS)))
    return leaf

def replace_subtree(e:Expr,rng)->Expr:
    eligible=[(p,n) for p,n in _expr_paths(e) if n.scope in ("market","sector","stock")]
    if not eligible:return e
    path,node=eligible[int(rng.integers(0,len(eligible)))]
    return _replace_at_path(e,path,_random_typed_subtree(node.scope,rng))

WRAP_FAMILIES=("ifsoft","softthresh","temporal")

def wrap_subtree(e:Expr,rng,force_family:str|None=None)->Expr:
    eligible=[(p,n) for p,n in _expr_paths(e) if n.scope in ("market","sector","stock")]
    if not eligible:return e
    path,node=eligible[int(rng.integers(0,len(eligible)))]
    family=force_family or str(rng.choice(WRAP_FAMILIES))
    if family=="temporal":
        wrapped=op(node.scope,str(rng.choice(("delta","accel","rollmax","rollmin","ema","lag"))),node,lookback=int(rng.choice(LOOKBACKS)))
    elif family=="softthresh":
        # SoftThresh is a gate-valued wrapper. It is type-safe only where a
        # gate expression can replace the selected node; therefore preserve
        # the selected node scope in this representation while retaining the
        # softthresh operation semantics used by eval_expr.
        wrapped=op(node.scope,"softthresh",node,theta=float(rng.normal()),scale=float(rng.uniform(.1,1)))
    elif family=="ifsoft":
        gate=op(node.scope,"softthresh",_random_feature_expr(node.scope,rng),theta=float(rng.normal()),scale=float(rng.uniform(.1,1)))
        alt=_random_typed_subtree(node.scope,rng)
        wrapped=op(node.scope,"ifsoft",gate,node,alt)
    else:raise ValueError(f"unknown wrap family {family}")
    return _replace_at_path(e,path,wrapped)

def unwrap_subtree(e:Expr,rng)->Expr:
    # A wrapper is removable only when one child has the same typed scope as
    # the wrapper. This covers Claude's temporal/SoftThresh wrapping without
    # changing the expression's output type.
    eligible=[]
    for path,node in _expr_paths(e):
        same=[a for a in node.args if a.scope==node.scope]
        if same:eligible.append((path,node,same))
    if not eligible:return e
    path,node,same=eligible[int(rng.integers(0,len(eligible)))]
    child=same[int(rng.integers(0,len(same)))]
    return _replace_at_path(e,path,child)

def mutate_expr(e:Expr,rng,kind:str)->Expr:
    if kind=="constant":
        if e.op=="const":return replace(e,value=float(e.value+rng.normal(0,.1)))
        if e.op=="softthresh":return replace(e,theta=float(e.theta+rng.normal(0,.1)),scale=max(.01,float(e.scale*np.exp(rng.normal(0,.1)))))
    if kind=="leaf_swap" and e.op=="feature":return _random_feature_expr(e.scope,rng)
    if kind=="operator_swap":
        if e.op in ("add","sub","mul","safediv","min","max"):return replace(e,op=str(rng.choice(("add","sub","mul","safediv","min","max"))))
        if e.op in ("delta","accel","rollmax","rollmin","ema","lag"):return replace(e,op=str(rng.choice(("delta","accel","rollmax","rollmin","ema","lag"))),lookback=int(rng.choice(LOOKBACKS)))
    if kind=="insert":
        if e.scope in ("market","sector","stock"):
            return op(e.scope,str(rng.choice(("add","sub","mul"))),e,_random_feature_expr(e.scope,rng))
    if kind=="wrap":return wrap_subtree(e,rng)
    if kind=="delete" and e.args:
        cand=[a for a in e.args if a.scope==e.scope]
        if cand:return cand[int(rng.integers(0,len(cand)))]
    if e.args:
        i=int(rng.integers(0,len(e.args)));aa=list(e.args);aa[i]=mutate_expr(aa[i],rng,kind);return replace(e,args=tuple(aa))
    return e

# Claude C.5 mutation classes are sampled as classes, not flattened low-level
# operators. This prevents multi-operation classes from receiving accidental
# extra probability mass. Frozen plateau structural classes are 4,5,6,11.
G2_MUTATION_CLASSES={
 1:("constant",), 2:("leaf_swap",), 3:("operator_swap",),
 4:("insert","delete","replace"), 5:("wrap","unwrap"),
 6:("module_add","module_delete","module_duplicate"),
 7:("applicability",), 8:("context",), 9:("policy",),
 10:("short",), 11:("simplify",),
}
STRUCTURAL_MUTATION_CLASSES=frozenset((4,5,6,11))
G2_MUTATION_OPS=tuple(x for c in sorted(G2_MUTATION_CLASSES) for x in G2_MUTATION_CLASSES[c])

# Historical pre-class sampler gave every EXISTING low-level operator equal
# probability. Thus established within-class ratios are preserved below.
# Frozen interpretation: conditional sampling is uniform among Claude-specified
# alternatives unless Claude explicitly specifies otherwise. This layer is
# applied only AFTER class selection and therefore cannot alter class weights.
WITHIN_CLASS_OPERATION_WEIGHTS={
 1:{"constant":1.0},2:{"leaf_swap":1.0},3:{"operator_swap":1.0},
 4:{"insert":1.0,"delete":1.0,"replace":1.0},
 5:{"wrap":1.0,"unwrap":1.0},
 6:{"module_add":1.0,"module_delete":1.0,"module_duplicate":1.0},
 7:{"applicability":1.0},8:{"context":1.0},9:{"policy":1.0},
 10:{"short":1.0},11:{"simplify":1.0},
}

def mutation_class_weights(structural_multiplier:float=1.0,stage:str="A"):
    w=np.ones(11,dtype=float)
    if stage=="B":
        w[6]*=2.0;w[7]*=2.0
    for c in STRUCTURAL_MUTATION_CLASSES:w[c-1]*=float(structural_multiplier)
    return w

def mutation_class_probabilities(structural_multiplier:float=1.0,stage:str="A"):
    w=mutation_class_weights(structural_multiplier,stage);return w/w.sum()

def choose_mutation_class(rng,structural_multiplier:float=1.0,stage:str="A"):
    probs=mutation_class_probabilities(structural_multiplier,stage)
    return int(rng.choice(np.arange(1,12),p=probs))

def choose_operation_within_class(rng,cls:int):
    spec=WITHIN_CLASS_OPERATION_WEIGHTS[int(cls)]
    unresolved=[k for k,v in spec.items() if v is None]
    if unresolved:
        raise RuntimeError(f"UNRESOLVED_WITHIN_CLASS_OPERATION_RATIO: class {cls}: {','.join(unresolved)}")
    ops=tuple(spec);w=np.asarray([spec[x] for x in ops],float);w=w/w.sum()
    return str(ops[int(rng.choice(np.arange(len(ops)),p=w))])

def choose_mutation_op(rng,structural_multiplier:float=1.0,stage:str="A"):
    cls=choose_mutation_class(rng,structural_multiplier,stage)
    return choose_operation_within_class(rng,cls)

def choose_context_scope(rng,stage:str="A"):
    # Conditional after class selection: Stage B sector:market = 2:1; otherwise 1:1.
    p=(1/3,2/3) if stage=="B" else (.5,.5)
    return str(rng.choice(("market","sector"),p=p))

def _new_module(seed,rng):
    fam=str(rng.choice(FAMILIES));mid=int(rng.integers(1,2**63-1))
    return StrategyModule(mid,fam,family_applicability(fam,rng),family_signal(fam,rng),
        str(rng.choice(SIDE_MODES)),float(rng.uniform(.1,1.5)),
        op("stock","abs",feature("stock","rv20")),op("stock","abs",feature("stock","dist_low20")))

def mutate_g2(g:GenomeG2,rng:np.random.Generator,stage:str="A",force:str|None=None,structural_multiplier:float=1.0)->GenomeG2:
    opn=force or choose_mutation_op(rng,structural_multiplier,stage)
    mods=list(g.modules);mctx=list(g.market_contexts);sctx=list(g.sector_contexts);states=list(g.stock_states)
    out=g
    if opn in ("constant","leaf_swap","operator_swap","insert","delete","replace","wrap","unwrap"):
        i=int(rng.integers(0,len(mods)));m=mods[i]
        slot=str(rng.choice(("signal","applicability","uncertainty","downside")))
        e=getattr(m,slot)
        if e is not None:
            if opn=="replace": ne=replace_subtree(e,rng)
            elif opn=="unwrap": ne=unwrap_subtree(e,rng)
            else: ne=mutate_expr(e,rng,opn)
            mods[i]=replace(m,**{slot:ne})
        out=replace(g,modules=tuple(mods))
    elif opn=="module_add" and len(mods)<N_MAX:
        m=_new_module(int(rng.integers(0,2**63-1)),rng);mods.append(m)
        out=replace(g,modules=tuple(mods),innovation_ids=tuple(sorted(set(g.innovation_ids+(m.innov_id,)))))
    elif opn=="module_delete" and len(mods)>1:
        mods.pop(int(rng.integers(0,len(mods))));out=replace(g,modules=tuple(mods))
    elif opn=="module_duplicate" and len(mods)<N_MAX:
        base=mods[int(rng.integers(0,len(mods)))];nid=int(rng.integers(1,2**63-1))
        dup=replace(base,innov_id=nid,signal=mutate_expr(base.signal,rng,"constant"));mods.append(dup)
        out=replace(g,modules=tuple(mods),innovation_ids=tuple(sorted(set(g.innovation_ids+(nid,)))))
    elif opn=="applicability":
        i=int(rng.integers(0,len(mods)));m=mods[i]
        refs=[("market",x.innov_id) for x in mctx]+[("sector",x.innov_id) for x in sctx]
        existing={n.ref_id for _,n in _expr_paths(m.applicability) if n.op=="ctxref" and n.ref_id is not None}
        removable=[x for x in refs if x[1] in existing]
        addable=[x for x in refs if x[1] not in existing]
        do_remove=bool(removable) and (not addable or rng.random()<.5)
        pool=removable if do_remove else addable
        if pool:
            scope=choose_context_scope(rng,stage)
            scoped=[x for x in pool if x[0]==scope]
            if not scoped:scoped=pool
            _,rid=scoped[int(rng.integers(0,len(scoped)))]
            if do_remove:
                def drop_ref(e):
                    if e.op=="and" and any(a.op=="ctxref" and a.ref_id==rid for a in e.args):
                        keep=[a for a in e.args if not (a.op=="ctxref" and a.ref_id==rid)]
                        return keep[0] if len(keep)==1 else replace(e,args=tuple(keep))
                    return replace(e,args=tuple(drop_ref(a) for a in e.args)) if e.args else e
                app=drop_ref(m.applicability)
            else:
                app=op("gate","and",m.applicability,ctxref("gate",rid))
        else:app=mutate_expr(m.applicability,rng,"wrap")
        mods[i]=replace(m,applicability=app);out=replace(g,modules=tuple(mods))
    elif opn=="context":
        scope=choose_context_scope(rng,stage)
        if scope=="market" and len(mctx)<M_MAX and (not mctx or rng.random()<.5):
            nid=int(rng.integers(1,2**63-1));u=CtxUnit(nid,"market",_random_feature_expr("market",rng),str(rng.choice(SQUASHES)),1.,0.)
            mctx.append(u);out=replace(g,market_contexts=tuple(mctx),innovation_ids=tuple(sorted(set(g.innovation_ids+(nid,)))))
        elif scope=="sector" and len(sctx)<S_MAX and (not sctx or rng.random()<.5):
            nid=int(rng.integers(1,2**63-1));u=CtxUnit(nid,"sector",_random_feature_expr("sector",rng),str(rng.choice(SQUASHES)),1.,0.)
            sctx.append(u);out=replace(g,sector_contexts=tuple(sctx),innovation_ids=tuple(sorted(set(g.innovation_ids+(nid,)))))
        elif scope=="market" and mctx:
            i=int(rng.integers(0,len(mctx)));mctx[i]=replace(mctx[i],expr=mutate_expr(mctx[i].expr,rng,"leaf_swap"));out=replace(g,market_contexts=tuple(mctx))
        elif sctx:
            i=int(rng.integers(0,len(sctx)));sctx[i]=replace(sctx[i],expr=mutate_expr(sctx[i].expr,rng,"leaf_swap"));out=replace(g,sector_contexts=tuple(sctx))
    elif opn=="policy":
        pick=str(rng.choice(("allocation","aggregator","lifecycle","oppmap")))
        if pick=="allocation":
            a=replace(g.allocation,mode=str(rng.choice(ALLOC_MODES)),gamma=float(np.clip(g.allocation.gamma+rng.normal(0,.2),.5,4)),
                      eta=float(np.clip(g.allocation.eta+rng.normal(0,.05),.01,1)),tau=mutate_expr(g.allocation.tau,rng,"wrap"))
            out=replace(g,allocation=a)
        elif pick=="aggregator":out=replace(g,aggregator=replace(g.aggregator,mode=str(rng.choice(AGG_MODES)),temp=max(.05,float(g.aggregator.temp*np.exp(rng.normal(0,.1))))))
        elif pick=="lifecycle":
            out=replace(g,lifecycle=replace(g.lifecycle,kappa=mutate_expr(g.lifecycle.kappa,rng,"constant"),
                q=mutate_expr(g.lifecycle.q,rng,"constant"),lambda_u=max(0.,float(g.lifecycle.lambda_u+rng.normal(0,.01)))))
        else:
            mode="causal_calibrated" if g.opportunity_map.mode=="affine" else "affine"
            out=replace(g,opportunity_map=replace(g.opportunity_map,mode=mode))
    elif opn=="short":
        out=replace(g,short_policy=replace(g.short_policy,enabled=not g.short_policy.enabled,
            applicability=mutate_expr(g.short_policy.applicability,rng,"wrap"),
            extra_hurdle=max(0.,float(g.short_policy.extra_hurdle+rng.normal(0,.002)))))
    elif opn=="simplify":
        if len(mods)>1 and rng.random()<.5:
            mods.pop(int(rng.integers(0,len(mods))));out=replace(g,modules=tuple(mods))
        else:
            i=int(rng.integers(0,len(mods)));mods[i]=replace(mods[i],signal=mutate_expr(mods[i].signal,rng,"delete"));out=replace(g,modules=tuple(mods))
    errs=validate_genome(out)
    return g if errs else out

def crossover_g2(a:GenomeG2,b:GenomeG2,rng:np.random.Generator)->GenomeG2:
    def merge_by_id(x,y):
        dx={z.innov_id:z for z in x};dy={z.innov_id:z for z in y};out=[]
        for i in sorted(set(dx)|set(dy)):
            if i in dx and i in dy:out.append(dx[i] if rng.random()<.5 else dy[i])
            elif rng.random()<.5:out.append((dx if i in dx else dy)[i])
        return tuple(out)
    mc=merge_by_id(a.market_contexts,b.market_contexts)[:M_MAX]
    sc=merge_by_id(a.sector_contexts,b.sector_contexts)[:S_MAX]
    st=merge_by_id(a.stock_states,b.stock_states)[:K_MAX]
    mods=merge_by_id(a.modules,b.modules)[:N_MAX]
    if not mods:mods=(a.modules[0],)
    ids=tuple(sorted({z.innov_id for z in (*mc,*sc,*st,*mods)}))
    pick=lambda x,y:x if rng.random()<.5 else y
    g=GenomeG2("MTS-GA-G2",ids,mc,sc,st,mods,pick(a.aggregator,b.aggregator),pick(a.opportunity_map,b.opportunity_map),
               pick(a.lifecycle,b.lifecycle),pick(a.allocation,b.allocation),pick(a.short_policy,b.short_policy))
    return g if not validate_genome(g) else a

def compatibility_distance(a:GenomeG2,b:GenomeG2)->float:
    ia=set(a.innovation_ids);ib=set(b.innovation_ids);union=max(len(ia|ib),1)
    innov_d=len(ia^ib)/union
    ma={m.innov_id:m for m in a.modules};mb={m.innov_id:m for m in b.modules};common=set(ma)&set(mb)
    fam_d=0. if not common else sum(ma[i].family_tag!=mb[i].family_tag for i in common)/len(common)
    return float(.75*innov_d+.25*fam_d)

def assign_species(pop,threshold=.35):
    reps=[];groups=[]
    for g in pop:
        for i,r in enumerate(reps):
            if compatibility_distance(g,r)<=threshold:groups[i].append(g);break
        else:reps.append(g);groups.append([g])
    return groups
