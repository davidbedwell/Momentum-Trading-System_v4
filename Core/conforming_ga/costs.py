"""Registered equity cost mechanics for MTS conformance.

SEC Section 31 rate is dollars per dollar of covered sale. FINRA TAF is per
share with a per-trade cap. Rates are date-effective and apply on sales only.
"""
from __future__ import annotations
from datetime import date
import math

SEC31=[
("2005-12-22",30.70),("2007-03-17",15.30),("2008-01-25",11.00),("2008-04-01",5.60),
("2009-04-10",25.70),("2010-01-15",12.70),("2010-04-01",16.90),("2011-01-21",19.20),
("2012-02-21",18.00),("2012-04-01",22.40),("2013-05-25",17.40),("2014-03-18",22.10),
("2015-02-14",18.40),("2016-02-16",21.80),("2017-07-04",23.10),("2018-05-22",13.00),
("2019-04-16",20.70),("2020-02-18",22.10),("2021-02-25",5.10),("2022-05-14",22.90),
("2023-02-27",8.00),("2024-05-22",27.80),("2025-05-14",0.00),("2026-04-04",20.60),
]
TAF=[
("2004-01-01",0.000075,3.75),("2011-07-01",0.000090,4.50),
("2012-03-01",0.000095,4.75),("2012-07-01",0.000119,5.95),
("2022-01-01",0.000130,6.49),("2023-01-01",0.000145,7.27),
("2024-01-01",0.000166,8.30),("2026-01-01",0.000195,9.79),
]
def _d(x): return date.fromisoformat(x) if isinstance(x,str) else x
def _effective(table,when):
    when=_d(when); row=None
    for r in table:
        if _d(r[0])<=when: row=r
        else: break
    if row is None: raise ValueError("date before registered schedule")
    return row

def sec31_rate(when)->float:
    return _effective(SEC31,when)[1]/1_000_000.0

def taf_fee(when,shares:float,price:float)->float:
    _,rate,cap=_effective(TAF,when)
    if price < rate:return 0.0
    return min(abs(shares)*rate,cap)

def regulatory_sell_fee(when,notional:float,shares:float,price:float)->float:
    return abs(notional)*sec31_rate(when)+taf_fee(when,shares,price)

def spread_bps_from_hlc(high:float,low:float,close:float,*,floor_bps:float=2.0,cap_bps:float)->float:
    if not (high>0 and low>0 and close>0 and high>=low): raise ValueError("bad HLC")
    # registered causal HLC range proxy; cap is explicit configuration, never hidden.
    proxy=10000.0*(high-low)/close/2.0
    return min(cap_bps,max(floor_bps,proxy))

def impact_bps(order_notional:float,adv_dollars:float,coefficient:float=10.0)->float:
    if order_notional<=0:return 0.0
    if adv_dollars<=0:return math.inf
    return coefficient*math.sqrt(order_notional/adv_dollars)

def one_way_cost(when,notional:float,shares:float,price:float,*,is_sell:bool,
                 spread_slippage_bps:float,impact_bps_value:float=0.0)->float:
    c=abs(notional)*(spread_slippage_bps+impact_bps_value)/10000.0
    if is_sell:c+=regulatory_sell_fee(when,notional,shares,price)
    return c

def borrow_fee(short_notional:float,annual_rate:float,calendar_days:int)->float:
    return abs(short_notional)*annual_rate*calendar_days/365.0
