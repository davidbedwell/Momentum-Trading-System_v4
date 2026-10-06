import numpy as np
from dataclasses import replace
from collections import Counter
from Core.conforming_ga.g2evolution import *
from Core.conforming_ga.g2schema import feature,op,_walk,validate_expr

def sig(e):
 return (e.scope,e.op,e.feature,e.lookback,tuple(sig(a) for a in e.args))

def test_every_claude_alternative_is_directly_reachable():
 # Direct conditional sampler reachability, not just forced mutate_g2.
 for cls,expected in G2_MUTATION_CLASSES.items():
  seen=set()
  for seed in range(2000):
   seen.add(choose_operation_within_class(np.random.default_rng(seed),cls))
   if seen==set(expected):break
  assert seen==set(expected),(cls,seen,expected)

def test_class_sampling_is_independent_of_low_level_count_exact_contract():
 assert np.allclose(mutation_class_probabilities(1),[1/11]*11)
 p=mutation_class_probabilities(2)
 assert np.allclose(p,[(2/15 if c in {4,5,6,11} else 1/15) for c in range(1,12)])

def test_plateau_does_not_touch_conditional_operation_distributions():
 for cls in (4,5,6):
  spec=WITHIN_CLASS_OPERATION_WEIGHTS[cls]
  q=np.array(list(spec.values()),float);q/=q.sum()
  assert np.allclose(q,np.full(len(q),1/len(q)))
 # API separation is mechanical: structural multiplier is accepted by class
 # selector only; within-class selector has no multiplier argument.
 import inspect
 assert 'structural_multiplier' in inspect.signature(choose_mutation_class).parameters
 assert 'structural_multiplier' not in inspect.signature(choose_operation_within_class).parameters

def test_replace_replaces_a_typed_subtree_not_necessarily_whole_slot():
 # Root and nested nodes are stock-typed. Across deterministic seeds prove a
 # nested replacement occurs while root remains unchanged.
 base=op('stock','add',
         op('stock','ema',feature('stock','ret20'),lookback=20),
         op('stock','lag',feature('stock','rv20'),lookback=5))
 found=False
 for seed in range(500):
  out=replace_subtree(base,np.random.default_rng(seed))
  assert validate_expr(out)==[]
  assert out.scope==base.scope
  if out.op==base.op and sig(out)!=sig(base):
   # Root survived, therefore mutation occurred below root.
   found=True;break
 assert found

def test_replace_preserves_scope_at_replacement_point():
 base=op('stock','add',feature('stock','ret20'),feature('stock','rv20'))
 for seed in range(100):
  out=replace_subtree(base,np.random.default_rng(seed))
  assert validate_expr(out)==[]
  assert all(n.scope=='stock' for n in _walk(out))

def test_unwrap_removes_wrapper_and_promotes_same_scope_child():
 leaf=feature('stock','ret20')
 wrapped=op('stock','ema',leaf,lookback=20)
 out=unwrap_subtree(wrapped,np.random.default_rng(1))
 assert sig(out)==sig(leaf)
 assert out.scope==wrapped.scope
 assert len(list(_walk(out))) < len(list(_walk(wrapped)))

def test_unwrap_can_remove_nested_wrapper_without_collapsing_root():
 leaf=feature('stock','ret20')
 inner=op('stock','ema',leaf,lookback=20)
 base=op('stock','add',inner,feature('stock','rv20'))
 found=False
 for seed in range(500):
  out=unwrap_subtree(base,np.random.default_rng(seed))
  assert validate_expr(out)==[]
  if out.op=='add' and sig(out)!=sig(base):
   found=True
   assert len(list(_walk(out)))<len(list(_walk(base)))
   break
 assert found

def test_wrap_all_claude_wrapper_families_are_reachable_and_valid():
 base=op('stock','add',feature('stock','ret20'),feature('stock','rv20'))
 for family in WRAP_FAMILIES:
  out=wrap_subtree(base,np.random.default_rng(123),force_family=family)
  assert validate_expr(out)==[]
  ops={n.op for n in _walk(out)}
  if family=='temporal': assert ops & {'delta','accel','rollmax','rollmin','ema','lag'}
  elif family=='softthresh': assert 'softthresh' in ops
  else: assert 'ifsoft' in ops

def test_wrap_can_target_nested_subtree_without_replacing_root():
 base=op('stock','add',
         op('stock','ema',feature('stock','ret20'),lookback=20),
         op('stock','lag',feature('stock','rv20'),lookback=5))
 for family in WRAP_FAMILIES:
  found=False
  for seed in range(500):
   out=wrap_subtree(base,np.random.default_rng(seed),force_family=family)
   assert validate_expr(out)==[]
   if out.op==base.op and sig(out)!=sig(base):
    found=True
    assert len(list(_walk(out)))>len(list(_walk(base)))
    break
  assert found,family

def test_wrap_preserves_selected_expression_scope_and_unwrap_roundtrip_possible():
 leaf=feature('stock','ret20')
 for family in WRAP_FAMILIES:
  wrapped=wrap_subtree(leaf,np.random.default_rng(9),force_family=family)
  assert wrapped.scope==leaf.scope
  assert validate_expr(wrapped)==[]
  # Every wrapper has the original same-scope subtree as an eligible child,
  # so unwrap can legally recover/promote a same-scope child.
  same=[a for a in wrapped.args if a.scope==wrapped.scope]
  assert same
