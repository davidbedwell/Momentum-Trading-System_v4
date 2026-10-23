"""Reconstruct auditable position lifecycles from exact reference ledger fills.

Preserves partial exits and additions; no invented round-trip fills.
Corporate actions are not inferred: callers must supply a reconciled split
adjustment stream or fail closed when shares change without recorded fills.
"""
from collections import defaultdict
from math import isfinite

def reconstruct_positions(fills, *, max_sessions=40, session_index=None, corporate_actions=None):
    if not 1 <= max_sessions <= 40:
        raise ValueError("invalid swing cap")
    if session_index is None:
        raise ValueError("explicit chronological session index required")
    corporate_actions = list(corporate_actions or [])
    for action in corporate_actions:
        if action["price_basis"] != "split_adjusted":
            raise ValueError("unsupported corporate action price basis")
        if action["pre_split_shares"] != action["post_split_shares"]:
            raise ValueError("split-adjusted shares changed")
        expected = action["pre_split_shares"] * action["dividend"]
        if abs(action["cash_after"]-action["cash_before"]-expected) > 1e-6:
            raise ValueError("corporate action dividend cash mismatch")
    states = {}
    events = []
    completed = []
    for fill in fills:
        symbol = fill["security"]
        ds = str(fill["execution_date"])[:10]
        decision = str(fill["decision_date"])[:10]
        if ds not in session_index or decision not in session_index:
            raise ValueError("missing chronological session")
        if session_index[ds] <= session_index[decision]:
            raise ValueError("same-session or future decision")
        qty = int(fill["quantity"])
        px = float(fill["price"])
        fee = float(fill["fee"])
        if qty <= 0 or px <= 0 or fee < 0 or not all(map(isfinite,(px,fee))):
            raise ValueError("invalid executed fill")
        before = int(fill["inventory_before"])
        after = int(fill["inventory_after"])
        side = fill["side"]
        if after - before != (qty if side == "BUY" else -qty):
            raise ValueError("inventory mismatch")
        st = states.get(symbol)
        if before != (st["shares"] if st else 0):
            raise ValueError("unexplained inventory change: possible split or missing fill")
        if side == "BUY":
            if st is None:
                if before != 0:
                    raise ValueError("unexplained opening inventory")
                st = dict(symbol=symbol,entry_date=ds,entry_decision_date=decision,
                          entry_session=session_index[ds],shares=0,cost=0.,
                          realized=0.,gross_buy=0.,gross_sell=0.,fees=0.,
                          fill_count=0,scale_in_count=0,scale_out_count=0)
                states[symbol] = st
                action = "ENTER"
            else:
                st["scale_in_count"] += 1
                action = "SCALE_IN"
            st["shares"] += qty
            st["cost"] += qty*px+fee
            st["gross_buy"] += qty*px
        elif side == "SELL":
            if st is None or st["shares"] < qty:
                raise ValueError("sale without position")
            allocated_cost = st["cost"]*qty/st["shares"]
            st["cost"] -= allocated_cost
            st["shares"] -= qty
            proceeds = qty*px-fee
            st["realized"] += proceeds-allocated_cost
            st["gross_sell"] += qty*px
            action = "EXIT" if st["shares"] == 0 else "SCALE_OUT"
            if st["shares"] > 0:
                st["scale_out_count"] += 1
        else:
            raise ValueError("invalid side")
        st["fees"] += fee
        st["fill_count"] += 1
        held = session_index[ds] - st["entry_session"]
        if held > max_sessions:
            raise ValueError("holding cap exceeded")
        events.append(dict(symbol=symbol,decision_date=decision,execution_date=ds,
                           action=action,quantity=qty,price=px,fee=fee,
                           inventory_after=after,holding_sessions=held))
        if st["shares"] == 0:
            completed.append(dict(symbol=symbol,entry_date=st["entry_date"],
                                  exit_date=ds,entry_decision_date=st["entry_decision_date"],
                                  holding_sessions=held,realized_pnl=st["realized"],
                                  net_return=st["realized"]/st["gross_buy"] if st["gross_buy"] else 0.,
                                  gross_buy=st["gross_buy"],gross_sell=st["gross_sell"],
                                  fees=st["fees"],fill_count=st["fill_count"],
                                  scale_in_count=st["scale_in_count"],
                                  scale_out_count=st["scale_out_count"]))
            del states[symbol]
    return dict(events=events,completed=completed,open_positions=states,
                corporate_actions=corporate_actions,
                dividend_cash=sum(a["cash_after"]-a["cash_before"] for a in corporate_actions),
                status="FILL_RECONSTRUCTED_NO_DECISION_ATTRIBUTION")
