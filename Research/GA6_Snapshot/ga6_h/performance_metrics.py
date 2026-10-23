"""Measured equity-curve statistics, never chromosome fitness or forward-label proxies."""
import math
import pandas as pd

def equity_metrics(equity, initial_cash=100000.0, sessions_per_year=252):
    """Return CAGR and MDD from chronological, executable marked-to-market equity.
    Net trade EV requires a matched realized-trade ledger; it is not inferred from CAGR.
    """
    e=pd.Series(equity,dtype=float)
    if len(e)<2 or initial_cash<=0 or not e.map(math.isfinite).all() or (e<=0).any():
        raise ValueError('invalid equity series')
    if not math.isclose(e.iloc[0],initial_cash,rel_tol=1e-8):
        raise ValueError('initial equity mismatch')
    years=(len(e)-1)/sessions_per_year
    peak=e.cummax()
    return {'cagr':float((e.iloc[-1]/e.iloc[0])**(1/years)-1),
            'max_drawdown':float((e/peak-1).min()),
            'final_equity':float(e.iloc[-1]),
            'sessions':len(e)-1}

def trade_net_ev(realized_pnl):
    """Arithmetic net dollars per completed trade, costs included by caller."""
    values=list(realized_pnl)
    if not values or any(not math.isfinite(float(x)) for x in values):
        raise ValueError('requires finite realized completed-trade PnL')
    return sum(values)/len(values)
