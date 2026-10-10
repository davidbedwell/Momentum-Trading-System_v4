#!/usr/bin/env python3
"""Deterministic generation evidence and economic plateau audit for future horizon runs."""
import json,math,pathlib
FIELDS=("ev_net","lcb95","cvar5","mae_tail5","effective_n")
def finite(v):return isinstance(v,(int,float)) and math.isfinite(v)
def record_generation(generation,candidates,evaluations,previous_best,minimum_effect=1e-5):
    assert isinstance(generation,int) and generation>=1
    byhash={e["genome_hash"]:e for e in evaluations}
    assert len(byhash)==len(evaluations)
    best=dict(previous_best);improved={};count=0
    for c in candidates:
        assert c["generation"]==generation and c.get("parent_hashes") is not None
        r=byhash[c["genome_hash"]];count+=1
        for p in r.get("points",[]):
            if not all(finite(p.get(k)) for k in FIELDS):continue
            if p["effective_n"]<30 or p["ev_net"]<=0 or p["lcb95"]<=0:continue
            niche=f'{c["side"]}:{p["horizon"]}'
            # Conservative improvement: confidence lower bound; downside retained for audit.
            old=best.get(niche)
            if old is None or p["lcb95"]>old["lcb95"]+minimum_effect:
                value={k:p[k] for k in FIELDS};value["genome_hash"]=c["genome_hash"]
                best[niche]=value;improved[niche]=p["lcb95"]-(old["lcb95"] if old else 0)
    return {"generation":generation,"evaluated":count,"niche_improvements":improved,"total_lcb_gain":sum(improved.values()),"best":best}
def plateau(history,patience=40,min_generations=60):
    assert patience>=1 and min_generations>=patience
    if len(history)<min_generations:return False
    tail=history[-patience:]
    return all(not h["niche_improvements"] for h in tail)
