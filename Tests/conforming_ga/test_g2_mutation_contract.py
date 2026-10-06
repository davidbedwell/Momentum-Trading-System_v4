import numpy as np
import pytest
from Core.conforming_ga.g2evolution import *
from Core.conforming_ga.g2schema import canonical,validate_genome

def test_frozen_structural_class_mapping():
 assert STRUCTURAL_MUTATION_CLASSES==frozenset({4,5,6,11})
 assert G2_MUTATION_CLASSES[4]==("insert","delete","replace")
 assert G2_MUTATION_CLASSES[5]==("wrap","unwrap")
 assert G2_MUTATION_CLASSES[6]==("module_add","module_delete","module_duplicate")
 assert G2_MUTATION_CLASSES[11]==("simplify",)
 assert 7 not in STRUCTURAL_MUTATION_CLASSES and 8 not in STRUCTURAL_MUTATION_CLASSES

def test_plateau_multiplier_changes_only_aggregate_class_weights():
 b=mutation_class_weights(1.0);p=mutation_class_weights(2.0)
 for c in range(1,12):
  assert p[c-1]==b[c-1]*(2.0 if c in {4,5,6,11} else 1.0)

def test_class_probability_independent_of_low_level_operation_count():
 b=mutation_class_probabilities(1.0)
 # At baseline every Claude class is one first-class probability unit despite
 # classes 4/6 having three operations and class 5 having two.
 assert np.allclose(b,np.full(11,1/11))
 p=mutation_class_probabilities(2.0)
 # Four structural class units doubled, seven untouched => denominator 15.
 for c in range(1,12):
  assert np.isclose(p[c-1],2/15 if c in {4,5,6,11} else 1/15)

def test_frozen_uniform_within_class_conditional_ratios():
 assert WITHIN_CLASS_OPERATION_WEIGHTS[4]=={"insert":1.0,"delete":1.0,"replace":1.0}
 assert WITHIN_CLASS_OPERATION_WEIGHTS[5]=={"wrap":1.0,"unwrap":1.0}
 assert WITHIN_CLASS_OPERATION_WEIGHTS[6]=={"module_add":1.0,"module_delete":1.0,"module_duplicate":1.0}

def test_plateau_multiplier_does_not_change_within_class_ratios():
 # Within-class sampler has no structural-multiplier input by design.
 # Verify the frozen conditional distributions themselves remain uniform.
 for cls,n in ((4,3),(5,2),(6,3)):
  w=np.array(list(WITHIN_CLASS_OPERATION_WEIGHTS[cls].values()),float)
  assert np.allclose(w/w.sum(),np.full(n,1/n))

def test_missing_replace_is_explicit_reachable_valid_operation():
 g=seed_g2(41,"momentum");seen=False
 for k in range(100):
  h=mutate_g2(g,np.random.default_rng(5000+k),force="replace")
  assert validate_genome(h)==[]
  if canonical(h)!=canonical(g):seen=True;break
 assert seen

def test_missing_unwrap_is_explicit_reachable_valid_operation():
 # First create an actual wrapper, then force unwrap until the wrapper is removed.
 g=seed_g2(42,"trend")
 for k in range(100):
  w=mutate_g2(g,np.random.default_rng(6000+k),force="wrap")
  if canonical(w)!=canonical(g):break
 assert canonical(w)!=canonical(g)
 seen=False
 for k in range(100):
  h=mutate_g2(w,np.random.default_rng(7000+k),force="unwrap")
  assert validate_genome(h)==[]
  if canonical(h)!=canonical(w):seen=True;break
 assert seen
