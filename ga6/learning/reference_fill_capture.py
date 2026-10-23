"""Reference-evaluator execution capture for research verification.

Uses a scoped, serialized ledger substitution because the frozen evaluator
constructs SettledLedger internally. NEVER run concurrent evaluator calls in
the same interpreter; use separate worker processes for parallelism.
"""
from contextlib import contextmanager
from threading import RLock

_LOCK = RLock()

def _capture_ledger(base, sink):
    class CapturingLedger(base):
        def execute_open(self, order, execution_date, open_price):
            before_cash = self.cash
            before_qty = self.holdings.get(order.security, 0)
            result = super().execute_open(order, execution_date, open_price)
            after_qty = self.holdings.get(order.security, 0)
            fill = dict(self.fills[-1])
            sink.append({
                "decision_date": str(order.date),
                "execution_date": str(execution_date),
                "security": order.security,
                "side": order.side,
                "quantity": fill["shares"],
                "price": fill["price"],
                "fee": fill["fee"],
                "cash_before": before_cash,
                "cash_after": self.cash,
                "inventory_before": before_qty,
                "inventory_after": after_qty,
                "settled_cash_after": self.available_cash(),
            })
            return result
    return CapturingLedger

def run_reference_with_fills(evaluator_module, frame, genome, **kwargs):
    """Return exact frozen evaluator metrics plus its actual executed fills.

    This captures executed orders, NOT yet decision-level HOLD/REJECT events.
    No changes to frozen source or fill semantics are made.
    """
    with _LOCK:
        original = evaluator_module.SettledLedger
        fills = []
        evaluator_module.SettledLedger = _capture_ledger(original, fills)
        try:
            metrics = evaluator_module.evaluate(frame, genome, **kwargs)
        finally:
            evaluator_module.SettledLedger = original
        if len(fills) != metrics["fills"]:
            raise RuntimeError("captured fill count differs from evaluator")
        for event in fills:
            delta = event["quantity"] if event["side"] == "BUY" else -event["quantity"]
            if event["inventory_after"] - event["inventory_before"] != delta:
                raise RuntimeError("captured inventory mismatch")
            expected = event["cash_before"] + (1 if event["side"] == "SELL" else -1) * event["quantity"] * event["price"] - event["fee"]
            if abs(expected - event["cash_after"]) > max(1e-6, abs(expected) * 1e-9):
                raise RuntimeError("captured cash mismatch")
        return {"metrics": metrics, "fills": fills,
                "status": "REFERENCE_EXECUTED_FILLS_CAPTURED_NOT_DECISION_CERTIFIED"}
