import pytest
from ga6.learning.position_lifecycle import reconstruct_positions

SESSIONS={f"2024-01-{d:02d}":d for d in range(2,15)}
def fill(date,decision,side,qty,price,before,after,fee=1):
    return dict(security="AAA",execution_date=date,decision_date=decision,
                side=side,quantity=qty,price=price,fee=fee,
                inventory_before=before,inventory_after=after)

def test_entry_scale_partial_exit_and_close():
    rows=[
        fill("2024-01-03","2024-01-02","BUY",10,100,0,10),
        fill("2024-01-05","2024-01-04","BUY",5,110,10,15),
        fill("2024-01-09","2024-01-08","SELL",5,120,15,10),
        fill("2024-01-11","2024-01-10","SELL",10,130,10,0),
    ]
    result=reconstruct_positions(rows,session_index=SESSIONS)
    assert [e["action"] for e in result["events"]]==["ENTER","SCALE_IN","SCALE_OUT","EXIT"]
    assert len(result["completed"])==1
    trade=result["completed"][0]
    assert trade["scale_in_count"]==1 and trade["scale_out_count"]==1
    assert trade["fill_count"]==4
    assert trade["holding_sessions"]==8
    assert trade["realized_pnl"]==350-4
    assert result["open_positions"]=={}

def test_missing_split_adjustment_fails_closed():
    rows=[fill("2024-01-03","2024-01-02","BUY",10,100,0,10),
          fill("2024-01-05","2024-01-04","SELL",5,110,20,15)]
    with pytest.raises(ValueError,match="unexplained inventory"):
        reconstruct_positions(rows,session_index=SESSIONS)

def test_missing_sessions_fails_closed():
    with pytest.raises(ValueError,match="explicit chronological"):
        reconstruct_positions([],session_index=None)
