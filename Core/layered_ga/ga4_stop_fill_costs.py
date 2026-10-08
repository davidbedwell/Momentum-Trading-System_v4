[Reading 37 lines from start (total: 37 lines, 0 remaining)]

"""Causal roundtrip cost estimate for an actual OHLC emergency-stop fill.

Entry spread/impact use only information known at decision T; exit spread
and impact use only the last completed bar before the exit execution.
This is an engineering estimate, not independent certification.
"""
import math
import numpy as np
from .stage2_path_v3 import REFERENCE_NOTIONAL, SPREAD_FLOOR_BPS, SPREAD_CAP_BPS, IMPACT_COEFFICIENT_BPS, _frozen_costs

def estimate_fill_cost(bars, decision_index, entry_index, exit_index, entry_price, exit_price, exit_fraction=1., notional=REFERENCE_NOTIONAL):
    if not (0 <= decision_index < entry_index <= exit_index < len(bars)):
        raise ValueError('invalid temporal indices')
    if not (0 < exit_fraction <= 1) or notional <= 0 or entry_price <= 0 or exit_price <= 0:
        raise ValueError('invalid fill parameters')
    def leg(known_index, executed_index, px, fraction):
        if known_index < 19:
            return float('nan')
        known=bars.iloc[known_index]
        trailing=bars.iloc[known_index-19:known_index+1]
        adv=np.mean(trailing['close'].to_numpy(float)*trailing['volume'].to_numpy(float))
        high,low,close=(float(known[k]) for k in ('high','low','close'))
        if not all(math.isfinite(x) for x in (adv,high,low,close)) or adv<=0 or close<=0 or high<low:
            return float('nan')
        spread=np.clip(10000*(high-low)/close/2,SPREAD_FLOOR_BPS,SPREAD_CAP_BPS)
        impact=IMPACT_COEFFICIENT_BPS*math.sqrt(notional*fraction/adv)
        return float((spread+impact)/10000*fraction)
    entry=leg(decision_index,entry_index,entry_price,1.)
    exit=leg(exit_index-1,exit_index,exit_price,exit_fraction)
    from datetime import datetime
    when=bars.iloc[exit_index]['date']
    when=when.date() if hasattr(when,'date') else datetime.fromisoformat(str(when)).date()
    if when < _frozen_costs._d(_frozen_costs.SEC31[0][0]):
        return float('nan')
    shares=notional*exit_fraction/exit_price
    reg=_frozen_costs.regulatory_sell_fee(when,notional*exit_fraction,shares,exit_price)/notional
    return float(entry+exit+reg)

[executed on device: instance-e298gycb-main (a21f8a9b-b225-483b-b45f-ba34708f98ee)]