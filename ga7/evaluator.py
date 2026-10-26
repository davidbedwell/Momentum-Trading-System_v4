"""GA7 portfolio accounting. Research only; not a PIT certification."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Policy:
    starting_cash: float = 100000.
    fee: float = .001
    cash_yield: float = .03
    max_positions: int = 10
    max_hold_sessions: int = 40

    def validate(self):
        if not (self.starting_cash > 0 and 0 <= self.fee < .01 and 0 <= self.cash_yield < 1):
            raise ValueError("Invalid accounting policy")
        if not (1 <= self.max_positions <= 10 and 1 <= self.max_hold_sessions <= 40):
            raise ValueError("Invalid position limits")
        return self

class Portfolio:
    def __init__(self, policy=None):
        self.policy = (policy or Policy()).validate()
        self.cash = self.policy.starting_cash
        self.positions = {}
        self.fills = []
        self.closed = []
        self.nav_history = []
        self.session = 0

    def equity(self, prices):
        missing = set(self.positions) - set(prices)
        if missing:
            raise ValueError("Held securities missing prices: " + str(sorted(missing)))
        return self.cash + sum(p["shares"] * prices[t] for t, p in self.positions.items())

    def accrue_cash(self):
        self.cash *= 1 + self.policy.cash_yield / 252

    def buy(self, ticker, price, weight, prices):
        if ticker in self.positions or len(self.positions) >= self.policy.max_positions:
            return False
        if not (isfinite(price) and price > 0 and 0 < weight <= 1):
            raise ValueError("Invalid buy")
        budget = min(self.cash, self.equity(prices) * weight)
        shares = int(budget / (price * (1 + self.policy.fee)))
        if shares < 1:
            return False
        gross = shares * price
        fee = gross * self.policy.fee
        self.cash -= gross + fee
        if self.cash < -1e-7:
            raise AssertionError("Negative cash")
        self.positions[ticker] = {"shares": shares, "entry": price, "cost": gross + fee, "session": self.session, "min_low": price}
        self.fills.append((self.session, ticker, "BUY", shares, price, fee))
        return True

    def update_low(self, ticker, low):
        if ticker in self.positions:
            if not (isfinite(low) and low > 0):
                raise ValueError("Invalid low")
            self.positions[ticker]["min_low"] = min(low, self.positions[ticker]["min_low"])

    def sell(self, ticker, price):
        if not (isfinite(price) and price > 0):
            raise ValueError("Invalid sell")
        p = self.positions.pop(ticker)
        gross = p["shares"] * price
        fee = gross * self.policy.fee
        proceeds = gross - fee
        self.cash += proceeds
        self.closed.append({"ticker": ticker, "pnl": proceeds - p["cost"], "net_return": proceeds / p["cost"] - 1, "mae": p["min_low"] / p["entry"] - 1, "sessions": self.session - p["session"]})
        self.fills.append((self.session, ticker, "SELL", p["shares"], price, fee))

    def mark(self, date, prices):
        nav = self.equity(prices)
        if not isfinite(nav) or nav <= 0:
            raise ValueError("Invalid NAV")
        self.nav_history.append((date, nav))
        return nav

    def finish(self, date, prices):
        for ticker in sorted(tuple(self.positions)):
            self.sell(ticker, prices[ticker])
        self.mark(date, prices)
        return self.metrics()

    def metrics(self):
        if self.positions:
            raise ValueError("Cannot finalize with open positions")
        peak, mdd = self.policy.starting_cash, 0.
        for _, nav in self.nav_history:
            peak = max(peak, nav)
            mdd = max(mdd, 1 - nav / peak)
        years = max(1, len(self.nav_history)) / 252
        cagr = (self.cash / self.policy.starting_cash) ** (1 / years) - 1
        n = len(self.closed)
        return {"final_nav": self.cash, "cagr": cagr, "mdd": mdd, "calmar": cagr / mdd if mdd else None, "ev": sum(p["net_return"] for p in self.closed) / n if n else 0., "mae": sum(p["mae"] for p in self.closed) / n if n else 0., "trades": n, "avg_hold": sum(p["sessions"] for p in self.closed) / n if n else 0.}
