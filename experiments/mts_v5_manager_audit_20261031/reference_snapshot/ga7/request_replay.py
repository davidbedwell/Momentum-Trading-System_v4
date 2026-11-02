"""Independent GA7 chromosome request replay (research, not MTS allocation).

At session t close, emit proposals using only t data. Fill requests at t+1
open; keep the proposal ledger even when a request cannot be funded.
Probabilities are explicitly uncalibrated until separately validated.
"""
from dataclasses import dataclass
from math import sqrt
from ga7.proposals import Proposal
from ga7.portfolio_priority import prioritize_pending
from ga7.shadow_ledger import ShadowLedger
from ga7.trade_accounting import TradeAccount

@dataclass
class Position:
    shares: int
    entry: float
    cost: float
    entered: int
    low: float
    origin_session: int
    realized_pnl: float = 0.
    realized_cost: float = 0.
    initial_stop: float = .02
    chromosome_id: str = ""
    high: float = 0.
    sector: str = "UNKNOWN"
    account: TradeAccount = None

def score_signal(genome, bar):
    return sum(bar["features"][x] for x in (genome.feature_a, genome.feature_b))/2

def replay_requests(genome, sessions, passes, *, starting_cash=100000.,
                    fee=.001, cash_yield=.0297, record_pass=False):
    if len(sessions) < 2:
        raise ValueError("Need two sessions")
    ledger = ShadowLedger()
    positions = {}
    cash = float(starting_cash)
    cash_flow = []  # independent cashflow journal for replay reconciliation
    unsettled = []  # (release_session, proceeds); T+1 equity cash settlement
    nav = []
    completed = []
    trade_r = []
    mae_r = []
    niche_entry_counts = {}
    niche_signal_counts = {}
    entry_signature = []
    pending_genomes = {}
    niche_bank = genome if isinstance(genome, dict) else None
    if niche_bank:
        if not all(hasattr(g, "identity") for g in niche_bank.values()):
            raise ValueError("Invalid niche chromosome bank")
        identity = "NICHE_BANK"
    else:
        identity = genome.identity()
    def active_genome(bar):
        if niche_bank is None:
            return genome
        return niche_bank.get(bar.get("controlling_niche")) or niche_bank.get("NON_NICHE")
    session_count=len(sessions)
    for i, (day, bars, defensive) in enumerate(sessions):
        if i:
            interest = cash * cash_yield / 252.
            cash += interest
            cash_flow.append(("YIELD", interest))
            # Prior-session sales settle at this session's open.
            settled = 0.
            outstanding = []
            for release, amount in unsettled:
                if release <= i: settled += amount
                else: outstanding.append((release, amount))
            cash += settled
            cash_flow.append(("SETTLEMENT", settled))
            unsettled = outstanding
            previous = sessions[i-1][1]
            previous_defense = sessions[i-1][2]
            # Apply cash dividends at ex-date. Price series must be split-adjusted;
            # split events are informational and must not multiply shares again.
            for ticker, pos in positions.items():
                if ticker in bars:
                    dividend = float(bars[ticker].get('dividend', 0.))
                    if dividend < 0:
                        raise ValueError('Negative dividend')
                    credit = pos.shares * dividend
                    cash += credit
                    cash_flow.append(("DIVIDEND", credit))
                    pos.realized_pnl += credit
                    pos.account.realized += credit
            # Execute decisions recorded at prior close, with no lookahead.
            for proposal in prioritize_pending(pending):
                ticker = proposal.ticker
                fill_genome = pending_genomes.get(ticker)
                if ticker not in bars:
                    if ticker in positions:
                        raise ValueError("Held ticker disappeared: " + ticker)
                    continue
                price = bars[ticker]["open"]
                if proposal.action == "EXIT" and ticker in positions:
                    pos = positions.pop(ticker)
                    proceeds = pos.shares * price * (1-fee)
                    unsettled.append((i + 1, proceeds))
                    ret, actual_r = pos.account.finish(proceeds)
                    completed.append((ticker, ret, i-pos.entered, pos.low/pos.entry-1))
                    trade_r.append(actual_r)
                    mae_r.append(max(0., 1-pos.low/pos.entry) / pos.initial_stop)
                    ledger.settle(identity, ticker, pos.origin_session, ret,
                                  ret > 0, max(1, i-pos.entered))
                elif proposal.action == "REDUCE" and ticker in positions:
                    pos = positions[ticker]
                    qty = max(1, pos.shares // 2)
                    proceeds = qty * price * (1-fee)
                    unsettled.append((i + 1, proceeds))
                    original_shares = pos.shares
                    allocated_cost = pos.cost * qty / original_shares
                    pos.realized_cost += allocated_cost
                    pos.realized_pnl += proceeds - allocated_cost
                    pos.account.sell(proceeds, qty/original_shares)
                    pos.shares -= qty
                    pos.cost -= allocated_cost
                    if pos.shares == 0:
                        ret, actual_r = pos.account.finish(0.)
                        completed.append((ticker, ret, i-pos.entered, pos.low/pos.entry-1))
                        trade_r.append(actual_r)
                        mae_r.append(max(0., 1-pos.low/pos.entry) / pos.initial_stop)
                        ledger.settle(identity, ticker, pos.origin_session, ret,
                                      ret > 0, max(1, i-pos.entered))
                        positions.pop(ticker)
                elif proposal.action in ("ENTER", "INCREASE") and not defensive and not previous_defense and bars[ticker]["eligible"]:
                    if proposal.action == "INCREASE" and ticker in positions:
                        pos = positions[ticker]
                        equity = cash + sum(p.shares * bars[t]["open"] for t,p in positions.items())
                        budget = min(cash, max(0., equity * .30 - pos.shares * price), equity * proposal.requested_weight, max(0., equity * .02 / pos.initial_stop - pos.shares * price))
                        qty = int(budget / (price * (1+fee)))
                        if qty:
                            cost = qty * price * (1+fee)
                            cash -= cost
                            cash_flow.append(("BUY", -cost))
                            pos.shares += qty
                            pos.cost += cost
                            pos.account.buy(cost, pos.initial_stop)
                            pos.entry = (pos.entry * (pos.shares-qty) + price * qty) / pos.shares
                    elif ticker not in positions and len(positions) < (max(g.capacity for g in niche_bank.values()) if niche_bank else genome.capacity) and sum(p.sector == bars[ticker].get("sector", "UNKNOWN") for p in positions.values()) < 3:
                        equity = cash + sum(p.shares * bars[t]["open"] for t,p in positions.items())
                        stop = fill_genome.stop_pct if fill_genome else .02
                        budget = min(cash, equity * proposal.requested_weight, equity * .02 / stop)
                        qty = int(budget / (price * (1+fee)))
                        if qty > 0:
                            cost = qty * price * (1+fee)
                            cash -= cost
                            cash_flow.append(("BUY", -cost))
                            account=TradeAccount()
                            account.buy(cost,stop)
                            positions[ticker] = Position(qty, price, cost, i, price, proposal.session, initial_stop=stop, chromosome_id=fill_genome.identity() if fill_genome else "", high=price, sector=bars[ticker].get("sector", "UNKNOWN"),account=account)
                            niche = previous.get(ticker, {}).get("controlling_niche") or "NON_NICHE"
                            niche_entry_counts[niche] = niche_entry_counts.get(niche, 0) + 1
                            entry_signature.append(f"{day}:{ticker}")
            for ticker, pos in list(positions.items()):
                if ticker not in bars:
                    raise ValueError("Held ticker disappeared: " + ticker)
                pos.low = min(pos.low, bars[ticker]["low"])
                pos.high = max(pos.high, bars[ticker]["close"])
        nav.append(cash + sum(amount for _, amount in unsettled) + sum(p.shares * bars[t]["close"] for t,p in positions.items()))
        pending = []
        pending_genomes = {}
        if i == session_count-1:
            continue
        for ticker, bar in bars.items():
            if not bar.get("eligible",False) and ticker not in positions:
                continue
            held = ticker in positions
            chosen = active_genome(bar)
            signal = passes(chosen, bar) if chosen is not None else False
            if signal and bar.get("eligible", False):
                niche = bar.get("controlling_niche") or "NON_NICHE"
                niche_signal_counts[niche] = niche_signal_counts.get(niche, 0) + 1
            age = i - positions[ticker].entered if held else 0
            pnl = bar["close"]/positions[ticker].entry-1 if held else 0.
            if held:
                exit_now = defensive or pnl <= -positions[ticker].initial_stop
                exit_now |= chosen is not None and chosen.exit_rule == "signal_decay" and not signal
                exit_now |= chosen is not None and chosen.exit_rule == "reversal" and pnl < -.005
                exit_now |= chosen is not None and chosen.exit_rule == "volatility" and abs(pnl) > .04
                action = "EXIT" if exit_now else "HOLD"
                if action == "HOLD" and chosen is not None:
                    strength = score_signal(chosen, bar)
                    if strength > .75 and pnl > .03:
                        action = "INCREASE"
                    elif pnl < -.01 or strength < .45:
                        action = "REDUCE"
            elif signal and not defensive and bar["eligible"]:
                action = "ENTER"
            else:
                action = "PASS"
            if action == "PASS" and not record_pass:
                continue
            # Feature score is NOT a calibrated probability.
            score = score_signal(chosen, bar) if chosen else 0.
            score = max(0., min(1., score)) if score == score else 0.
            request = Proposal(i, ticker, identity, action, score,
                (score-.5)*.1, .02, chosen.entry_pct if action=="ENTER" else (.03 if action=="INCREASE" else 0.),
                0, score, False).validate()
            ledger.record(request)
            pending.append(request)
            pending_genomes[ticker] = chosen
    # Research liquidation at final close, not a next-open signal fill.
    for ticker, pos in list(positions.items()):
        proceeds = pos.shares * sessions[-1][1][ticker]["close"] * (1-fee)
        cash += proceeds
        cash_flow.append(("TERMINAL_SELL", proceeds))
        ret, actual_r = pos.account.finish(proceeds)
        completed.append((ticker, ret, len(sessions)-1-pos.entered, pos.low/pos.entry-1))
        trade_r.append(actual_r)
        mae_r.append(max(0., 1-pos.low/pos.entry) / pos.initial_stop)
        ledger.settle(identity, ticker, pos.origin_session, ret,
                      ret > 0, max(1, len(sessions)-1-pos.entered))
        del positions[ticker]
    terminal_settlements = sum(amount for _, amount in unsettled)
    cash += terminal_settlements
    cash_flow.append(("TERMINAL_SETTLEMENT", terminal_settlements))
    independently_reconciled = starting_cash + sum(amount for _, amount in cash_flow)
    if abs(independently_reconciled-cash)>max(1e-7,abs(cash)*1e-10):
        raise ArithmeticError("Portfolio cash does not reconcile with cashflow journal")
    nav[-1] = cash
    peak = starting_cash
    mdd = 0.
    for value in nav:
        peak = max(peak,value)
        mdd = max(mdd, 1-value/peak)
    years = len(sessions)/252
    cagr = (cash/starting_cash)**(1/years)-1
    n = len(completed)
    mean = sum(x[1] for x in completed)/n if n else 0.
    variance = sum((x[1]-mean)**2 for x in completed)/(n-1) if n>1 else 0.
    effective_n = max(1., n/2.)
    se = sqrt(variance/effective_n) if n>1 else None
    fitness = mean-1.96*se if se is not None else -1.
    risk_stop = max(g.stop_pct for g in niche_bank.values()) if niche_bank else genome.stop_pct
    r_values = trade_r
    mean_r = sum(r_values) / n if n else 0.
    var_r = sum((x-mean_r)**2 for x in r_values)/(n-1) if n>1 else 0.
    conservative_r = mean_r - 1.96*sqrt(var_r/effective_n) if n>1 else -1.
    mae_stop_ratio = sum(mae_r)/n if n else 0.
    mae_p90 = sorted(mae_r)[min(n-1, int(.9*(n-1)))] if n else 0.
    return {"r_sum":sum(r_values),"r_sumsq":sum(x*x for x in r_values),"fitness":conservative_r, "ev_r":mean_r, "conservative_ev_r":conservative_r, "mae_stop_ratio":mae_p90, "mae_stop_mean":mae_stop_ratio, "mae_stop_p90":mae_p90,"fitness_lcb_net_ev":fitness,"effective_trades":effective_n,
            "net_ev_se":se,"return_per_session":sum(x[1]/max(1,x[2]) for x in completed)/n if n else 0.,
            "final_nav":cash,"cash_reconciliation_error":independently_reconciled-cash,"cagr":cagr,"mdd":mdd,
            "calmar":cagr/mdd if mdd else None,
            "ev":sum(x[1] for x in completed)/len(completed) if completed else 0.,
            "mae":sum(x[3] for x in completed)/n if n else 0., "trades":len(completed),
            "avg_hold":sum(x[2] for x in completed)/len(completed) if completed else 0.,
            "requests":len(ledger.requests),"outcomes":len(ledger.outcomes),
            "niche_signal_counts":niche_signal_counts,
            "niche_entry_counts":niche_entry_counts,
            "entry_signature":entry_signature}, ledger
