from discovery.competitive_ga.streaming_defense import StreamingDefense
from ga6.abc_b1_r1_state_controller import qualify_statefully
import pytest

def test_streaming_matches_frozen_state_machine():
    rows=[]
    for i in range(16):
        rows.append({'date':f'2026-01-{i+1:02d}','A':2<=i<=7,'B':False,'B1':False,'C':False,'R1_evidence':i>=8})
    expected=qualify_statefully(rows)
    stream=StreamingDefense()
    observed=[stream.observe(row['date'],row) for row in rows]
    assert [v['defensive_next_open'] for v in observed]==[s.defensive for s in expected]
    assert [v['entered'] for v in observed]==[s.entered_defensive for s in expected]
    assert [v['exited'] for v in observed]==[s.exited_defensive for s in expected]
    assert observed[6]['entered']
    assert observed[10]['exited']

def test_missing_criteria_rejected():
    with pytest.raises(ValueError):StreamingDefense().observe('2026-01-01',{'A':False})
