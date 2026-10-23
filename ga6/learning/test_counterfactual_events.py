"""Tests for immutable, chronology-safe execution event schema."""
from dataclasses import replace
import pytest
from ga6.learning.counterfactual_events import TradeEvent

def example():
    return TradeEvent(run_id="run1", chromosome_id="1660", symbol="ABC",
        decision_date="2024-01-02", event_type="ENTER",
        position_id="p1", decision_id="d1", evidence_cutoff="2024-01-02",
        execution_date="2024-01-03", side="BUY", quantity=10, price=100,
        fee=1, cash_before=10000, cash_after=8999,
        inventory_before=0, inventory_after=10)

def test_valid_fill():
    assert example().record()["inventory_after"] == 10

@pytest.mark.parametrize("change", [
    {"evidence_cutoff":"2024-01-04"},
    {"execution_date":"2024-01-02"},
    {"inventory_after":9},
    {"cash_after":9000},
    {"quantity":0},
    {"event_type":"MAGIC"},
])
def test_invalid_fill(change):
    with pytest.raises(ValueError):
        replace(example(), **change)

def test_valid_scale_out():
    fill = replace(example(), event_type="SCALE_OUT", side="SELL",
        inventory_before=20, inventory_after=10, cash_after=10999)
    assert fill.record()["side"] == "SELL"
