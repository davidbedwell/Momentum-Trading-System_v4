from pathlib import Path

def test_v4_missing_endpoint_is_not_numeric_penalty():
 s=Path('scripts/run_g3_v4_preregistered_gate_20261007.py').read_text();assert 'None),len(vals)' in s;assert '-1e9' not in s[s.index('def run_local_ticker'):s.index('def seed')]
def test_v4_is_stock_local_and_validation_frozen():
 s=Path('scripts/run_g3_v4_preregistered_gate_20261007.py').read_text();assert 'exact_structural_screen_local(*train,48)' in s;assert 'for ti,t in enumerate(TICKERS)' in s;assert 'len(vals)>=6' in s
def test_v4_requires_20_paired_replicates_and_same_gate():
 s=Path('scripts/run_g3_v4_preregistered_gate_20261007.py').read_text();assert 'len(pairs)>=20' in s;assert 'PER_NULL_ALPHA' in s;assert 'PASS_2_OF_3' in s and 'STRONG_PASS_3_OF_3' in s
