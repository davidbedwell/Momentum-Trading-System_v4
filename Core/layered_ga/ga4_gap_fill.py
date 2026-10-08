"""Causal OHLC emergency-stop simulator; gap fills at first available open.

Long exits on open <= stop at open, otherwise intraday low <= stop at stop.
Short exits on open >= stop at open, otherwise intraday high >= stop at stop.
No threshold is optimized from observed outcomes.
"""
from math import isfinite

def emergency_exit(side, entry, stop, bars):
    if side not in ("LONG","SHORT"):
        raise ValueError("side")
    if not all(isfinite(float(x)) and float(x)>0 for x in (entry,stop)):
        raise ValueError("entry/stop")
    if side=="LONG" and stop>=entry or side=="SHORT" and stop<=entry:
        raise ValueError("stop must be adverse to entry")
    for index, bar in enumerate(bars):
        o,h,l=(float(bar[k]) for k in ("open","high","low"))
        if not all(isfinite(v) and v>0 for v in (o,h,l)) or not l<=o<=h:
            raise ValueError("invalid OHLC")
        if side=="LONG":
            if o<=stop:
                return {"bar":index,"fill":o,"type":"GAP_THROUGH","return":o/entry-1}
            if l<=stop:
                return {"bar":index,"fill":stop,"type":"INTRADAY_STOP","return":stop/entry-1}
        else:
            if o>=stop:
                return {"bar":index,"fill":o,"type":"GAP_THROUGH","return":1-o/entry}
            if h>=stop:
                return {"bar":index,"fill":stop,"type":"INTRADAY_STOP","return":1-stop/entry}
    return None
