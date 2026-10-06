import numpy as np
from dataclasses import replace
from Core.conforming_ga.g2evolution import *
from Core.conforming_ga.g2schema import CtxUnit,feature,ctxref,op

def test_stage_b_exact_class_weights_and_plateau_multiplicative():
 a=mutation_class_weights(1,"A");b=mutation_class_weights(1,"B");bp=mutation_class_weights(2,"B")
 assert np.array_equal(a,np.ones(11))
 assert np.array_equal(b,np.array([1,1,1,1,1,1,2,2,1,1,1],float))
 assert np.array_equal(bp,np.array([1,1,1,2,2,2,2,2,1,1,2],float))
 assert np.array_equal(mutation_class_weights(1,"C"),a)
 assert np.array_equal(mutation_class_weights(1,"D"),a)
 assert np.all(mutation_class_probabilities(1,"B")>0)

def test_sector_conditional_ratio_stage_b_and_baseline():
 class R:
  def __init__(self):self.ps=[]
  def choice(self,a,p=None):self.ps.append(tuple(p));return a[0]
 r=R();choose_context_scope(r,"B");choose_context_scope(r,"A");choose_context_scope(r,"C");choose_context_scope(r,"D")
 assert r.ps[0]==(1/3,2/3)
 assert all(x==(.5,.5) for x in r.ps[1:])

def _g_with_contexts():
 g=initial_population_g2("ctx",0,0,1)[0]
 mc=CtxUnit(9001,"market",feature("market","spy_ret20"))
 sc=CtxUnit(9002,"sector",feature("sector","sector_ret20"))
 return replace(g,market_contexts=g.market_contexts+(mc,),sector_contexts=g.sector_contexts+(sc,),
                innovation_ids=tuple(sorted(set(g.innovation_ids+(9001,9002)))))

def _refs(e):
 out=set()
 def walk(n):
  if n.op=="ctxref" and n.ref_id is not None:out.add(n.ref_id)
  for a in n.args:walk(a)
 walk(e);return out

def test_class7_can_add_and_remove_market_and_sector_refs():
 g=_g_with_contexts();adds=set();removes=set()
 for seed in range(800):
  z=mutate_g2(g,np.random.Generator(np.random.PCG64(seed)),stage="A",force="applicability")
  for before,after in zip(g.modules,z.modules):
   adds|=(_refs(after.applicability)-_refs(before.applicability))
 base=g.modules[0];app=op("gate","and",op("gate","and",base.applicability,ctxref("gate",9001)),ctxref("gate",9002))
 gr=replace(g,modules=(replace(base,applicability=app),))
 for seed in range(800):
  z=mutate_g2(gr,np.random.Generator(np.random.PCG64(seed)),stage="A",force="applicability")
  removes|=({9001,9002}-_refs(z.modules[0].applicability))
 assert {9001,9002}<=adds
 assert {9001,9002}<=removes

def test_all_classes_reachable_every_stage_and_stage_d_baseline():
 for stage in ("A","B","C","D"):
  p=mutation_class_probabilities(1,stage);assert len(p)==11 and np.all(p>0)
 assert np.array_equal(mutation_class_weights(1,"A"),mutation_class_weights(1,"C"))
 assert np.array_equal(mutation_class_weights(1,"A"),mutation_class_weights(1,"D"))
