"""Deterministic research replay kernel; NOT broker/production parity certified."""
from dataclasses import dataclass, field
from math import isfinite
from discovery.competitive_ga.progressive_scaling import allowed_target

@dataclass(frozen=True)
class Bar:
    open: float
    close: float
    dividend: float = 0.0
    split: float = 1.0

@dataclass(frozen=True)
class Signal:
    ticker: str
    family: str
    chromosome: str
    target_weight: float
    score: float = 0.0
    scaling_evidence: object = None
    stop_distance: float = None
    gap_risk: float = None
    other_equity_risk: float = 0.0

@dataclass
class Replay:
    cash: float = 100000.0
    shares: dict = field(default_factory=dict)
    pending: list = field(default_factory=list)
    ledger: list = field(default_factory=list)
    nav: list = field(default_factory=list)
    fees: float = 0.001
    cap: float = 0.10
    max_equity_risk: float = .02
    settlement_sessions: int = 0
    unsettled: list = field(default_factory=list)
    session: int = -1
    risk_snapshot: object = None
    risk_audit: list = field(default_factory=list)
    spread: float = 0.0  # full proportional bid/ask spread
    slippage: float = 0.0  # one-way adverse execution allowance
    impact: float = 0.0  # one-way scenario allowance, not a fitted liquidity model
    mdd_limit: float = .20
    high_water: float = None
    max_drawdown: float = 0.0
    admission_halted: bool = False
    drawdowns: list = field(default_factory=list)

    @property
    def friction(self):
        return self.spread / 2 + self.slippage + self.impact

    @property
    def round_trip_cost(self):
        return (1 + self.friction) * (1 + self.fees) - (1 - self.friction) * (1 - self.fees)

    def monitor(self, equity):
        if not isfinite(equity) or equity <= 0:
            raise ValueError('nonpositive or nonfinite NAV')
        if self.high_water is None:
            self.high_water = equity
        drawdown = max(0., 1 - equity / self.high_water)
        self.max_drawdown = max(self.max_drawdown, drawdown)
        self.high_water = max(self.high_water, equity)
        if drawdown >= self.mdd_limit:
            self.admission_halted = True
        return drawdown

    def day(self, date, bars, signals=(), defense=False, cash_yield_daily=0.0):
        """Execute yesterday's close signals at today's open, then mark close.
        Scaling requires explicit historical evidence and risk estimates; absent
        evidence, only initial 10% exposure is allowed, never an unearned add.
        """
        if self.high_water is None:
            self.high_water = self.cash
        if any(not isfinite(v) or not 0 <= v < 1 for v in (self.spread, self.slippage, self.impact)) or self.friction >= 1:
            raise ValueError('invalid execution costs')
        if not isfinite(self.mdd_limit) or not 0 < self.mdd_limit <= .20:
            raise ValueError('MDD policy cannot exceed 20%')
        if not isfinite(self.max_equity_risk) or not 0 < self.max_equity_risk <= .02:
            raise ValueError('risk budget cannot exceed 2%')
        if not isfinite(self.fees) or not 0<=self.fees<1:raise ValueError('invalid fee')
        if type(self.settlement_sessions) is not int or not 0 <= self.settlement_sessions <= 2:
            raise ValueError('bounded settlement lag required')
        if len({s.ticker for s in self.pending}) != len(self.pending):
            raise ValueError('duplicate pending ticker')
        if any(not isfinite(s.target_weight) or not 0 <= s.target_weight <= 1
               or not isfinite(s.score) for s in self.pending):
            raise ValueError('invalid pending order')
        self.session += 1
        self.cash += sum(v for due,v in self.unsettled if due <= self.session)
        self.unsettled = [(due,v) for due,v in self.unsettled if due > self.session]
        if not 0 <= cash_yield_daily < 1: raise ValueError('invalid yield')
        for ticker,bar in bars.items():
            if not all(isfinite(v) for v in (bar.open,bar.close,bar.split,bar.dividend)) or bar.open<=0 or bar.close<=0 or bar.split<=0:raise ValueError('invalid bar')
            if ticker in self.shares:
                self.shares[ticker]*=bar.split
                self.cash+=self.shares[ticker]*bar.dividend
        self.cash*=(1+cash_yield_daily)
        receivable=sum(v for _,v in self.unsettled)
        open_equity=self.cash+receivable+sum(q*bars[t].open for t,q in self.shares.items())
        self.monitor(open_equity)
        ordered=sorted(self.pending,key=lambda x:(-x.score,x.ticker,x.chromosome))
        targets={}
        # Reserve portfolio risk across all evidence-based additions in score order.
        # The caller-supplied other_equity_risk remains a separate floor.
        reserved_risk=0.0
        if defense:
            targets={t:0. for t in self.shares}
        else:
            for s in ordered:
                t=s.ticker
                if t not in bars or t in targets:continue
                existing=self.shares.get(t,0.)*bars[t].open/open_equity
                requested=max(0.,s.target_weight)
                if requested<=existing:
                    targets[t]=requested
                elif s.scaling_evidence is not None:
                    if s.stop_distance is None or s.gap_risk is None:
                        raise ValueError('scaling risk inputs required')
                    targets[t]=max(existing,allowed_target(existing,requested,s.scaling_evidence,
                        stop_distance=s.stop_distance,gap_risk=s.gap_risk,
                        other_equity_risk=max(s.other_equity_risk,reserved_risk),max_equity_risk=self.max_equity_risk))
                    reserved_risk+=max(0.,targets[t]-existing)*max(s.stop_distance,s.gap_risk)
                else:
                    # No evidence means no increases beyond ordinary 10% entry.
                    targets[t]=min(requested,self.cap) if existing<=self.cap else existing
            # Every increase, ordinary or scaled, gets the same prefill loss gate.
            # Missing gap information means a conservative total-loss scenario.
            for s in ordered:
                t = s.ticker
                if t not in targets:
                    continue
                existing = self.shares.get(t, 0.) * bars[t].open / open_equity
                if targets[t] <= existing:
                    continue
                stop = s.stop_distance
                gap = 1.0 if s.gap_risk is None else s.gap_risk
                if stop is None:
                    stop = 1.0
                if any(not isfinite(v) or not 0 <= v <= 1 for v in (stop, gap)):
                    raise ValueError('invalid mandatory loss inputs')
                loss = max(stop, gap) + self.round_trip_cost
                limit = self.max_equity_risk / loss if loss > 0 else 0.
                allowed = existing if self.admission_halted else max(existing, min(targets[t], limit))
                self.risk_audit.append(dict(date=date, ticker=t, requested=targets[t],
                    allowed=allowed, modeled_equity_loss=allowed * loss,
                    gap_stress_equity_loss=allowed * (1 + self.friction) * (1 + self.fees),
                    gap_loss_guaranteed=False, admission_halted=self.admission_halted))
                targets[t] = allowed
            for t,q in self.shares.items():
                if t not in targets:targets[t]=q*bars[t].open/open_equity
        if self.risk_snapshot is not None:
            if self.risk_snapshot.as_of >= date:
                raise ValueError('risk snapshot must precede execution')
            existing={t:q*bars[t].open/open_equity for t,q in self.shares.items()}
            rejected=self.risk_snapshot.constrain(existing,targets,ordered,bars)
            self.risk_audit.append((date,rejected,dict(targets)))
        proceeds=0.
        for t in sorted(set(self.shares)&set(targets)):
            desired=targets[t]*open_equity/bars[t].open
            sell=max(0.,self.shares[t]-desired)
            if sell>1e-10:
                sell_price = bars[t].open * (1 - self.friction)
                gross=sell*sell_price
                proceeds+=gross*(1-self.fees)
                self.shares[t]-=sell
                self.ledger.append((date,t,'SELL',sell,sell_price,gross*self.fees))
        spendable=self.cash
        for s in ordered:
            t=s.ticker
            if defense or t not in targets:continue
            mark_price=bars[t].open
            price=mark_price*(1+self.friction)
            desired=targets[t]*open_equity/mark_price
            buy=max(0.,desired-self.shares.get(t,0.))
            cost=buy*price*(1+self.fees)
            if cost>spendable:
                buy=spendable/(price*(1+self.fees))
                cost=buy*price*(1+self.fees)
            if buy>1e-10:
                self.shares[t]=self.shares.get(t,0.)+buy
                spendable-=cost
                self.ledger.append((date,t,'BUY',buy,price,buy*price*self.fees))
        self.cash=spendable
        if self.settlement_sessions and proceeds:
            self.unsettled.append((self.session+self.settlement_sessions,proceeds))
        else:
            self.cash+=proceeds
        self.shares={t:q for t,q in self.shares.items() if q>1e-10}
        equity=self.cash+sum(v for _,v in self.unsettled)+sum(q*bars[t].close for t,q in self.shares.items())
        drawdown = self.monitor(equity)
        self.drawdowns.append((date, drawdown, self.max_drawdown, self.admission_halted))
        self.nav.append((date,equity,self.cash,dict(self.shares),defense))
        self.pending=[] if defense else list(signals)
        return equity
