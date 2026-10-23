"""Immutable, validated trade-level event records for GA6-v3 instrumentation.

This is an event schema and reconciliation boundary, not an execution engine.
"""
from dataclasses import dataclass, asdict
from math import isfinite
from typing import Optional

ACTIONS = frozenset(("ENTER", "HOLD", "SCALE_IN", "SCALE_OUT",
                     "EXIT", "REPLACE_CANDIDATE", "RISK_EXIT", "REJECT"))
SIDES = frozenset(("BUY", "SELL"))

@dataclass(frozen=True)
class TradeEvent:
    run_id: str
    chromosome_id: str
    symbol: str
    decision_date: str
    event_type: str
    position_id: str
    decision_id: str
    evidence_cutoff: str
    execution_date: Optional[str] = None
    side: Optional[str] = None
    quantity: int = 0
    price: Optional[float] = None
    fee: float = 0.0
    cash_before: Optional[float] = None
    cash_after: Optional[float] = None
    inventory_before: Optional[int] = None
    inventory_after: Optional[int] = None
    rejection_reason: Optional[str] = None

    def __post_init__(self):
        if not all((self.run_id, self.chromosome_id, self.symbol,
                    self.decision_date, self.position_id, self.decision_id)):
            raise ValueError("missing event identity")
        if self.event_type not in ACTIONS:
            raise ValueError("unknown event action")
        if self.evidence_cutoff > self.decision_date:
            raise ValueError("future decision evidence")
        if self.quantity < 0 or self.fee < 0 or not isfinite(self.fee):
            raise ValueError("invalid quantity or fee")
        if self.side is not None:
            if self.side not in SIDES or not self.execution_date:
                raise ValueError("invalid fill side/date")
            if self.execution_date <= self.decision_date:
                raise ValueError("fill must occur after decision date")
            if self.quantity <= 0 or self.price is None or not isfinite(self.price) or self.price <= 0:
                raise ValueError("invalid fill")
            if self.inventory_before is None or self.inventory_after is None:
                raise ValueError("missing inventory reconciliation")
            delta = self.quantity if self.side == "BUY" else -self.quantity
            if self.inventory_after - self.inventory_before != delta:
                raise ValueError("inventory does not reconcile")
            if self.cash_before is None or self.cash_after is None:
                raise ValueError("missing cash reconciliation")
            expected = self.cash_before + (self.quantity * self.price * (1 if self.side == "SELL" else -1)) - self.fee
            if abs(self.cash_after - expected) > max(1e-6, abs(expected)*1e-9):
                raise ValueError("cash does not reconcile")
        elif self.quantity or self.price is not None:
            raise ValueError("non-fill event carries execution quantities")

    def record(self):
        return asdict(self)
