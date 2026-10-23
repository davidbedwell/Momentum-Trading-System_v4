"""Shared cash, next-open portfolio replay and exact frozen-reference fill parity.

Research infrastructure, NOT an adaptive selector. Proposals must be generated
at decision time from matured evidence. No use of hindsight trade outcomes.
"""
from math import isfinite

def replay_orders(sessions, proposals, *, starting_cash, fee, annual_cash_yield,
                  ledger_class, order_class, max_positions=10, max_hold=40,
                  membership=None, earnings_allowed=None, risk_veto=None,
                  corporate_actions=None):
    """sessions: ordered (date, open_prices, close_prices); proposals by decision date.

    Proposals: {decision_date: [{symbol, chromosome, action, weight}]};
    actions ENTER, EXIT, SCALE_IN, SCALE_OUT, HOLD, DECLINE.
    Each position has one immutable chromosome owner. A new order executes
    at the next available session open; missing prices fail closed.
    All controls are required, including execution-date risk/eligibility.
    """
    if not 1 <= max_hold <= 40 or not 1 <= max_positions <= 79:
        raise ValueError("invalid portfolio limits")
    if not 0 <= annual_cash_yield < 1 or not 0 <= fee < 1:
        raise ValueError("invalid rates")
    if any(x is None for x in (membership, earnings_allowed, risk_veto, corporate_actions)):
        raise ValueError("explicit PIT policies and corporate actions required")
    ledger=ledger_class(starting_cash, fee, price_basis="split_adjusted")
    owners={}; entered={}; pending=[]; nav=[]; events=[]; rejects=[]; last={}
    for i,(ds,opens,closes) in enumerate(sessions):
        if i and ds<=sessions[i-1][0]: raise ValueError("nonchronological sessions")
        if ds not in risk_veto: raise ValueError("missing defense state")
        ledger.start_session(ds,i,annual_cash_yield)
        for symbol, split, dividend in corporate_actions.get(ds,[]):
            ledger.apply_ex_date(ds,symbol,split,dividend)
        # All open positions are forcibly exited in defense or at 40 sessions.
        mandatory={s for s in owners if risk_veto[ds] is not True or i-entered[s]>=max_hold}
        for p in pending:
            if p["action"]=="EXIT": mandatory.add(p["symbol"])
        # Sell before buy; no same-open reversal.
        sold=set()
        for symbol in sorted(mandatory):
            if symbol not in owners: continue
            if symbol not in opens: raise ValueError("missing mandatory exit open")
            qty=ledger.holdings[symbol]
            ledger.execute_open(order_class(pending[0]["decision_date"] if pending else sessions[i-1][0],
                                            symbol,"SELL",qty),ds,opens[symbol])
            events.append((ds,symbol,"EXIT",owners[symbol],qty))
            sold.add(symbol); del owners[symbol]; del entered[symbol]
        for p in pending:
            symbol=p["symbol"]; action=p["action"]; chromosome=str(p["chromosome"])
            if action in ("HOLD","DECLINE"): continue
            if action=="EXIT": continue
            if symbol in sold:
                rejects.append((ds,symbol,action,"same_session_exit")); continue
            if symbol not in opens:
                rejects.append((ds,symbol,action,"missing_open")); continue
            if action in ("ENTER","SCALE_IN"):
                if risk_veto.get(p["decision_date"]) is not True or risk_veto[ds] is not True:
                    rejects.append((ds,symbol,action,"defense")); continue
                if not membership.get((ds,symbol),False):
                    rejects.append((ds,symbol,action,"membership")); continue
                if not earnings_allowed.get((ds,symbol),False):
                    rejects.append((ds,symbol,action,"earnings")); continue
            if action=="ENTER":
                if symbol in owners:
                    rejects.append((ds,symbol,action,"already_owned")); continue
                if len(owners)>=max_positions:
                    rejects.append((ds,symbol,action,"capacity")); continue
            elif action in ("SCALE_IN","SCALE_OUT"):
                if symbol not in owners or owners[symbol]!=chromosome:
                    rejects.append((ds,symbol,action,"owner_mismatch")); continue
            else:
                raise ValueError("invalid action")
            weight=float(p["weight"])
            if not isfinite(weight) or not 0<weight<=1: raise ValueError("invalid weight")
            px=opens[symbol]
            if px<=0 or not isfinite(px): raise ValueError("invalid open")
            equity=ledger.cash+sum(q*opens.get(s,last.get(s,0)) for s,q in ledger.holdings.items())
            if action=="SCALE_OUT":
                qty=min(ledger.holdings[symbol],max(1,int(ledger.holdings[symbol]*weight)))
                side="SELL"
            else:
                target=int(equity*weight/(px*(1+fee)))
                if action=="SCALE_IN":
                    target=min(target,max(0,int(equity*.30/(px*(1+fee)))-ledger.holdings[symbol]))
                qty=min(target,int(ledger.available_cash()/(px*(1+fee))))
                side="BUY"
            if qty<=0:
                rejects.append((ds,symbol,action,"insufficient_settled_cash_or_allocation")); continue
            ledger.execute_open(order_class(p["decision_date"],symbol,side,qty),ds,px)
            events.append((ds,symbol,action,chromosome,qty))
            if action=="ENTER": owners[symbol]=chromosome; entered[symbol]=i
            if action=="SCALE_OUT" and not ledger.holdings.get(symbol):
                del owners[symbol]; del entered[symbol]
        pending=[]
        if any(s not in closes for s in ledger.holdings if ledger.holdings[s]):
            raise ValueError("missing held-security close")
        last.update(closes)
        nav.append((ds,ledger.nav(closes)))
        proposals_today=proposals.get(ds,[])
        seen=set()
        for p in proposals_today:
            symbol=p["symbol"]; action=p["action"]
            if symbol in seen: raise ValueError("multiple competing actions on symbol")
            seen.add(symbol)
            if p.get("evidence_cutoff",ds)>ds: raise ValueError("future evidence")
            if action not in ("ENTER","EXIT","SCALE_IN","SCALE_OUT","HOLD","DECLINE"):
                raise ValueError("unknown action")
            pending.append(dict(p,decision_date=ds))
    return dict(nav=nav,events=events,rejections=rejects,owners=owners,
                fills=ledger.fills,final_nav=nav[-1][1],
                status="SHARED_CAPITAL_EXECUTION_RESEARCH_NOT_SELECTOR_CERTIFIED")

def verify_reference_parity(reference, replay, *, tolerance=0.01):
    """Fail closed on every fill and NAV; final NAV equality alone is insufficient."""
    expected=reference["metrics"]["calendar_nav"]
    actual=replay["nav"]
    if len(expected)!=len(actual): raise AssertionError("session count mismatch")
    for (ed,ev),(ad,av) in zip(expected,actual):
        if str(ed)!=str(ad) or abs(ev-av)>max(tolerance,abs(ev)*1e-9):
            raise AssertionError("daily NAV parity mismatch")
    ef=reference["fills"]; af=replay["fills"]
    if len(ef)!=len(af): raise AssertionError("fill count mismatch")
    for a,b in zip(ef,af):
        for x,y in (("execution_date","execution_date"),("security","security"),
                    ("side","side"),("quantity","shares"),("price","price"),("fee","fee")):
            if x in ("price","fee"):
                if abs(float(a[x])-float(b[y]))>1e-7: raise AssertionError("fill mismatch")
            elif str(a[x])!=str(b[y]): raise AssertionError("fill mismatch")
    return dict(status="EXACT_FILL_AND_DAILY_NAV_PARITY",sessions=len(actual),fills=len(af))
