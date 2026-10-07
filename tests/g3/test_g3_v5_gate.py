import importlib.util
from pathlib import Path
P=Path('scripts/run_g3_v5_preregistered_gate_20261007.py')
def load():
 spec=importlib.util.spec_from_file_location('v5',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def test_v5_has_no_arm_missing_or_numeric_sentinel():
 s=P.read_text();section=s[s.index('def run_arm'):s.index('def seed')];assert "'viable_stock_count':len(vals)" in section;assert '-1e9' not in section;assert 'len(vals)>=6' not in section
def test_lexicographic_viability_precedes_return():
 m=load();assert m._cmp_endpoint({'viable_stock_count':7,'median_viable_return':-.5},{'viable_stock_count':6,'median_viable_return':.5})==(1,'viability')
def test_return_breaks_equal_viability():
 m=load();assert m._cmp_endpoint({'viable_stock_count':6,'median_viable_return':.02},{'viable_stock_count':6,'median_viable_return':.01})==(1,'return')
def test_zero_viability_pair_is_tie():
 m=load();assert m._cmp_endpoint({'viable_stock_count':0,'median_viable_return':None},{'viable_stock_count':0,'median_viable_return':None})==(0,'tie')
def test_exact_sign_test_and_bonferroni_gate():
 m=load();assert abs(m._exact_sign_p(19,25)-0.007316648960113525)<1e-15;assert m._exact_sign_p(18,25)>m.PER_NULL_ALPHA
def test_v5_preserves_frozen_search_controls():
 s=P.read_text();assert 'cut=int(n*.70);vstart=cut+10' in s;assert 'exact_structural_screen_local(*train,48)' in s;assert 'for gen in range(6)' in s;assert 'a.replicates==25' in s
