"""Evaluate genuine shared-capital NAV observations, never independent shadow returns.

The caller must provide the executed portfolio's actual end-of-session NAV series.
This module does not synthesize shared-capital fills or claim selector certification.
"""
from datetime import date
from math import isfinite

def assess_shared_portfolio(nav_series, *, starting_cash, baseline=None):
    """Return growth, CAGR, MDD, Calmar from dated portfolio NAV.

    nav_series: sequence of (ISO date, end-of-session NAV), including first
    observed session. All open holdings must be marked to market, and all
    settled/unsettled cash, fees and corporate actions reconciled upstream.
    """
    if not isfinite(starting_cash) or starting_cash <= 0:
        raise ValueError("invalid starting capital")
    if len(nav_series) < 2:
        raise ValueError("at least two sessions required")
    dates, values = [], []
    for ds, value in nav_series:
        day = date.fromisoformat(str(ds)[:10])
        v = float(value)
        if not isfinite(v) or v <= 0:
            raise ValueError("nonpositive or nonfinite NAV")
        if dates and day <= dates[-1]:
            raise ValueError("NAV dates must be strictly increasing")
        dates.append(day)
        values.append(v)
    elapsed = (dates[-1]-dates[0]).days
    if elapsed <= 0:
        raise ValueError("zero time horizon")
    peak = float(starting_cash)
    mdd = 0.0
    for v in values:
        peak = max(peak, v)
        mdd = max(mdd, (peak-v)/peak)
    growth = values[-1]/starting_cash - 1
    cagr = (values[-1]/starting_cash)**(365.25/elapsed)-1
    result = dict(starting_cash=starting_cash, ending_nav=values[-1],
        net_growth=growth, cagr=cagr, max_drawdown=mdd,
        calmar=cagr/mdd if mdd else None, sessions=len(values),
        elapsed_calendar_days=elapsed,
        status="PORTFOLIO_NAV_METRICS_ONLY_REQUIRES_EXECUTION_PARITY")
    if baseline is not None:
        b = assess_shared_portfolio(baseline, starting_cash=starting_cash)
        if str(baseline[0][0])[:10] != str(nav_series[0][0])[:10] or str(baseline[-1][0])[:10] != str(nav_series[-1][0])[:10]:
            raise ValueError("baseline must cover same dates")
        result["baseline"] = b
        result["cagr_delta"] = cagr-b["cagr"]
        result["mdd_delta"] = mdd-b["max_drawdown"]
    return result
