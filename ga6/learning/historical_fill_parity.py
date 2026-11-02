"""Real historical execution-ledger parity against frozen evaluator fills.

Replays the *actual* frozen evaluator's executed orders through an independent
SettledLedger. Proves accounting/execution parity, not adaptive decision parity.
"""
from collections import defaultdict
from math import isclose

def replay_captured_reference(reference, prepared, *, starting_cash, fee,
                              annual_cash_yield, ledger_class, order_class):
    ledger=ledger_class(starting_cash,fee,price_basis="split_adjusted")
    fills=defaultdict(list)
    for f in reference["fills"]:
        fills[str(f["execution_date"])[:10]].append(f)
    actions=defaultdict(list)
    for a in reference["corporate_actions"]:
        actions[str(a["date"])[:10]].append(a)
    nav=[];last={}
    for i,(ds,rows,opens,closes) in enumerate(prepared.sessions):
        ledger.start_session(ds,i,annual_cash_yield)
        for a in actions[ds]:
            ledger.apply_ex_date(ds,a["ticker"],a["split"],a["dividend"])
        for f in fills[ds]:
            symbol=f["security"]
            if symbol not in opens or not isclose(opens[symbol],f["price"],rel_tol=1e-12,abs_tol=1e-9):
                raise AssertionError("captured fill price does not match real next open")
            if ledger.holdings.get(symbol,0)!=f["inventory_before"]:
                raise AssertionError("historical inventory drift before fill")
            if not isclose(ledger.cash,f["cash_before"],rel_tol=1e-10,abs_tol=1e-6):
                raise AssertionError("historical cash drift before fill")
            ledger.execute_open(order_class(f["decision_date"],symbol,f["side"],f["quantity"]),ds,opens[symbol])
            if ledger.holdings.get(symbol,0)!=f["inventory_after"]:
                raise AssertionError("historical inventory drift after fill")
            if not isclose(ledger.cash,f["cash_after"],rel_tol=1e-10,abs_tol=1e-6):
                raise AssertionError("historical cash drift after fill")
        if any(q and s not in closes for s,q in ledger.holdings.items()):
            raise AssertionError("missing held-security closing mark")
        last.update(closes)
        nav.append((ds,ledger.nav(closes)))
    from ga6.learning.shared_capital_replay import verify_reference_parity
    return verify_reference_parity(reference,{"nav":nav,"fills":ledger.fills})
