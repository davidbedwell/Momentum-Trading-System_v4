"""Independent GA7 chromosome request replay (research, not MTS allocation).

At session t close, emit proposals using only t data. Fill requests at t+1
open; keep the proposal ledger even when a request cannot be funded.
Probabilities are explicitly uncalibrated until separately validated.
"""
from dataclasses import dataclass
from ga7.proposals import Proposal
from ga7.shadow_ledger import ShadowLedger

@dataclass
class Position:
    shares: int
    entry: float
    cost: float
    entered: int
    low: float
    origin_session: int

def score_signal(genome, bar):
    return sum(bar["features"][x] for x in (genome.feature_a, genome.feature_b))/2

def replay_requests(genome, sessions, passes, *, starting_cash=100000.,
                    fee=.001, cash_yield=.0297, record_pass=False):
    if len(sessions) < 2:
        raise ValueError("Need two sessions")
    ledger = ShadowLedger()
    positions = {}
    cash = float(starting_cash)
    nav = []
    completed = []
    identity = genome.identity()
    for i, (day, bars, defensive) in enumerate(sessions):
        if i:
            cash *= 1 + cash_yield / 252.
            previous = sessions[i-1][1]
            previous_defense = sessions[i-1][2]
            # Execute decisions recorded at prior close, with no lookahead.
            for proposal in pending:
                ticker = proposal.ticker
                if ticker not in bars:
                    if ticker in positions:
                        raise ValueError("Held ticker disappeared: " + ticker)
                    continue
                price = bars[ticker]["open"]
                if proposal.action == "EXIT" and ticker in positions:
                    pos = positions.pop(ticker)
                    proceeds = pos.shares * price * (1-fee)
                    cash += proceeds
                    ret = proceeds / pos.cost - 1
                    completed.append((ticker, ret, i-pos.entered))
                    ledger.settle(identity, ticker, pos.origin_session, ret,
                                  ret > 0, min(40, max(1, i-pos.entered)))
                elif proposal.action == "REDUCE" and ticker in positions:
                    pos = positions[ticker]
                    qty = max(1, pos.shares // 2)
                    cash += qty * price * (1-fee)
                    original_shares = pos.shares
                    pos.shares -= qty
                    pos.cost *= pos.shares / original_shares
                    if pos.shares == 0:
                        positions.pop(ticker)
                elif proposal.action in ("ENTER", "INCREASE") and not defensive and not previous_defense and bars[ticker]["eligible"]:
                    if proposal.action == "INCREASE" and ticker in positions:
                        pos = positions[ticker]
                        equity = cash + sum(p.shares * bars[t]["open"] for t,p in positions.items())
                        budget = min(cash, max(0., equity * .30 - pos.shares * price), equity * proposal.requested_weight)
                        qty = int(budget / (price * (1+fee)))
                        if qty:
                            cost = qty * price * (1+fee)
                            cash -= cost
                            pos.shares += qty
                            pos.cost += cost
                    elif ticker not in positions and len(positions) < genome.capacity:
                        equity = cash + sum(p.shares * bars[t]["open"] for t,p in positions.items())
                        budget = min(cash, equity * proposal.requested_weight)
                        qty = int(budget / (price * (1+fee)))
                        if qty > 0:
                            cost = qty * price * (1+fee)
                            cash -= cost
                            positions[ticker] = Position(qty, price, cost, i, price, proposal.session)
            for ticker, pos in list(positions.items()):
                if ticker not in bars:
                    raise ValueError("Held ticker disappeared: " + ticker)
                pos.low = min(pos.low, bars[ticker]["low"])
        nav.append(cash + sum(p.shares * bars[t]["close"] for t,p in positions.items()))
        pending = []
        if i == len(sessions)-1:
            continue
        for ticker, bar in bars.items():
            held = ticker in positions
            signal = passes(genome, bar)
            age = i - positions[ticker].entered if held else 0
            pnl = bar["close"]/positions[ticker].entry-1 if held else 0.
            if held:
                exit_now = defensive or age >= min(genome.hold_sessions,40) or pnl <= -genome.stop_pct
                exit_now |= genome.exit_rule == "signal_decay" and not signal
                exit_now |= genome.exit_rule == "reversal" and pnl < -.005
                exit_now |= genome.exit_rule == "volatility" and abs(pnl) > .04
                action = "EXIT" if exit_now else "HOLD"
                if action == "HOLD" and pnl > .03 and score_signal(genome, bar) > .75:
                    action = "INCREASE"
                elif action == "HOLD" and pnl < -.01:
                    action = "REDUCE"
            elif signal and not defensive and bar["eligible"]:
                action = "ENTER"
            else:
                action = "PASS"
            if action == "PASS" and not record_pass:
                continue
            # Feature score is NOT a calibrated probability.
            score = score_signal(genome, bar)
            score = max(0., min(1., score)) if score == score else 0.
            request = Proposal(i, ticker, identity, action, score,
                (score-.5)*.1, .02, genome.entry_pct if action=="ENTER" else (.03 if action=="INCREASE" else 0.),
                min(40, genome.hold_sessions), score, False).validate()
            ledger.record(request)
            pending.append(request)
    # Research liquidation at final close, not a next-open signal fill.
    for ticker, pos in list(positions.items()):
        proceeds = pos.shares * sessions[-1][1][ticker]["close"] * (1-fee)
        cash += proceeds
        completed.append((ticker, proceeds/pos.cost-1, len(sessions)-1-pos.entered))
        del positions[ticker]
    peak = starting_cash
    mdd = 0.
    for value in nav:
        peak = max(peak,value)
        mdd = max(mdd, 1-value/peak)
    years = len(sessions)/252
    cagr = (cash/starting_cash)**(1/years)-1
    return {"final_nav":cash,"cagr":cagr,"mdd":mdd,
            "calmar":cagr/mdd if mdd else None,
            "ev":sum(x[1] for x in completed)/len(completed) if completed else 0.,
            "mae":0., "trades":len(completed),
            "avg_hold":sum(x[2] for x in completed)/len(completed) if completed else 0.,
            "requests":len(ledger.requests),"outcomes":len(ledger.outcomes)}, ledger
