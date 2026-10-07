from scripts.layered_stage_common_20261007 import pmap
def square(x): return x*x
def test_parallel_map_preserves_order_and_values():
 x=list(range(24))
 assert pmap(square,x,workers=1)==pmap(square,x,workers=6)
