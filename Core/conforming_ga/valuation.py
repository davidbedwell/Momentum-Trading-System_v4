"""Literal Claude E.2 valuation in SAFE excess-return units."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Values:
    long:float; short:float; safe:float=0.0

def asset_values(E:float,u:float,lambda_u:float,daily_safe:float,daily_borrow:float,extra_short_hurdle:float)->Values:
    long=E-lambda_u*u
    short=-E-2.0*daily_safe-daily_borrow-lambda_u*u-extra_short_hurdle
    return Values(long,short,0.0)
