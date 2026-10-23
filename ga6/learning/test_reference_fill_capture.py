from types import SimpleNamespace
import pytest
from ga6.learning.reference_fill_capture import run_reference_with_fills

class FakeLedger:
    def __init__(self, *args, **kwargs):
        self.cash=10000.
        self.holdings={}
        self.fills=[]
    def available_cash(self):
        return self.cash
    def execute_open(self, order, execution_date, open_price):
        qty=order.shares
        fee=qty*open_price*.001
        self.cash += (qty*open_price if order.side=="SELL" else -qty*open_price)-fee
        self.holdings[order.security]=self.holdings.get(order.security,0)+(qty if order.side=="BUY" else -qty)
        self.fills.append(dict(shares=qty,price=open_price,fee=fee,side=order.side))
        return self.fills[-1]

def evaluator(frame, genome, **kwargs):
    ledger=module.SettledLedger()
    ledger.execute_open(SimpleNamespace(date="2024-01-02",security="AAA",side="BUY",shares=10),"2024-01-03",100)
    ledger.execute_open(SimpleNamespace(date="2024-01-04",security="AAA",side="SELL",shares=10),"2024-01-05",110)
    return dict(fills=len(ledger.fills), final_nav=ledger.cash)

module=SimpleNamespace(SettledLedger=FakeLedger,evaluate=evaluator)

def test_capture_and_restore():
    result=run_reference_with_fills(module,None,None)
    assert len(result["fills"])==2
    assert result["fills"][0]["inventory_after"]==10
    assert result["fills"][1]["inventory_after"]==0
    assert result["metrics"]["final_nav"]==10097.9
    assert module.SettledLedger is FakeLedger

def test_restoration_after_error():
    def bad(*args,**kwargs):
        raise ValueError("expected")
    failing=SimpleNamespace(SettledLedger=FakeLedger,evaluate=bad)
    with pytest.raises(ValueError):
        run_reference_with_fills(failing,None,None)
    assert failing.SettledLedger is FakeLedger
