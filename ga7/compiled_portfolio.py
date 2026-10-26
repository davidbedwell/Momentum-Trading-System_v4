"""Numba chronological cash-funded portfolio replay.

Research kernel: requires separate GA6 parity certification before production.
Split-adjusted OHLC convention matches GA6 SettledLedger(price_basis="split_adjusted").
Inputs are daily contiguous arrays, signal[t] derived from information at t-1.
"""
import numpy as np
from numba import njit

@njit(cache=True)
def replay(opens, closes, lows, dividends, splits, present, eligible,
           sector, defense, signals, hold_limit, entry_fraction,
           max_positions, fee=0.001, cash_yield=0.0297,
           hard_stop=0.02, start_cash=100000.):
    n_days, n_stocks = opens.shape
    if n_days < 2 or n_stocks < 1 or hold_limit < 1 or hold_limit > 40:
        raise ValueError("Invalid dimensions or swing hold")
    if not 0. < entry_fraction <= .30 or not 1 <= max_positions <= n_stocks:
        raise ValueError("Invalid allocation or capacity")
    if not 0. <= fee < 1. or not 0. <= cash_yield < 1. or not 0. < hard_stop <= .02:
        raise ValueError("Invalid execution costs or risk policy")
    if start_cash <= 0. or not np.isfinite(start_cash):
        raise ValueError("Invalid starting capital")
    shares = np.zeros(n_stocks, np.int64)
    entry = np.zeros(n_stocks, np.float64)
    costs = np.zeros(n_stocks, np.float64)
    entry_day = np.zeros(n_stocks, np.int64)
    min_low = np.full(n_stocks, np.inf)
    nav = np.empty(n_days, np.float64)
    cash = start_cash
    trades = 0
    pnl_sum = 0.
    mae_sum = 0.
    hold_sum = 0.
    peak = start_cash
    mdd = 0.
    for day in range(n_days):
        # Fixed SGOV proxy, user-approved: 2.97% annual on uninvested cash.
        # Session accrual is an approximation, not GA6 T+1 cash settlement.
        if day > 0:
            cash *= 1. + cash_yield / 252.
        if day > 0:
            for stock in range(n_stocks):
                if shares[stock] == 0:
                    continue
                if not present[day, stock]:
                    raise ValueError("Held ticker missing")
                split = splits[day, stock]
                if not np.isfinite(split) or split < 0.:
                    raise ValueError("Invalid split ratio")
                # GA6 split-adjusted basis: do not multiply held shares.
                cash += shares[stock] * dividends[day, stock]
                price = opens[day, stock]
                if not np.isfinite(price) or price <= 0.:
                    raise ValueError("Invalid held open")
                pnl = price / entry[stock] - 1.
                if defense[day-1] or pnl <= -hard_stop or day - entry_day[stock] >= hold_limit or day == n_days-1:
                    proceeds = shares[stock] * price * (1.-fee)
                    cash += proceeds
                    trades += 1
                    pnl_sum += proceeds / costs[stock] - 1.
                    mae_sum += min_low[stock] / entry[stock] - 1.
                    hold_sum += day - entry_day[stock]
                    shares[stock] = 0
                    costs[stock] = 0.
            if not defense[day-1] and day != n_days-1:
                for stock in range(n_stocks):
                    if not signals[day, stock] or not eligible[day, stock] or shares[stock] != 0:
                        continue
                    active = 0
                    sector_count = 0
                    for other in range(n_stocks):
                        if shares[other] > 0:
                            active += 1
                            if sector[day, other] == sector[day, stock]:
                                sector_count += 1
                    if active >= max_positions or sector_count >= 3:
                        continue
                    equity = cash
                    for other in range(n_stocks):
                        if shares[other] > 0:
                            if not present[day, other]:
                                raise ValueError("Held ticker missing at valuation")
                            equity += shares[other] * opens[day, other]
                    price = opens[day, stock]
                    budget = min(cash, equity * entry_fraction)
                    qty = int(budget / (price * (1. + fee)))
                    if qty > 0:
                        gross = qty * price
                        total = gross * (1. + fee)
                        cash -= total
                        shares[stock] = qty
                        entry[stock] = price
                        costs[stock] = total
                        entry_day[stock] = day
                        min_low[stock] = price
        for stock in range(n_stocks):
            if shares[stock] > 0:
                if not present[day, stock]:
                    raise ValueError("Held ticker missing close")
                if not np.isfinite(lows[day, stock]) or lows[day, stock] <= 0.:
                    raise ValueError("Invalid held low")
                min_low[stock] = min(min_low[stock], lows[day, stock])
        value = cash
        for stock in range(n_stocks):
            if shares[stock] > 0:
                value += shares[stock] * closes[day, stock]
        if not np.isfinite(value) or value <= 0.:
            raise ValueError("Invalid NAV")
        nav[day] = value
        peak = max(peak, value)
        mdd = max(mdd, 1. - value / peak)
    if np.any(shares != 0):
        raise ValueError("Open positions after final session")
    years = max(1, n_days) / 252.
    cagr = (cash / start_cash) ** (1. / years) - 1.
    return (cash, cagr, mdd, cagr / mdd if mdd > 0. else np.nan,
            pnl_sum / trades if trades else 0.,
            mae_sum / trades if trades else 0.,
            trades, hold_sum / trades if trades else 0., nav)
