"""Convert completed replay ledger round trips to causal calibration outcomes.
Single-owner long-only positions; reject partial closes and ambiguous scaling.
Fees included. Maturity at SELL session, never available until later.
"""
from collections import defaultdict
from causal_calibration import TradeOutcome,Calibrator

def completed_round_trips(ledger,session_by_date,owner_by_ticker,context_by_ticker):
    positions={}
    outcomes=[]
    for date,ticker,side,qty,price,fee in ledger:
        session=session_by_date[date]
        if side=="BUY":
            if ticker in positions:raise ValueError("scaling not yet supported")
            if ticker not in owner_by_ticker or ticker not in context_by_ticker:
                raise ValueError("missing owner/context")
            positions[ticker]=(session,qty,qty*price+fee,
                               owner_by_ticker[ticker],tuple(context_by_ticker[ticker]))
        elif side=="SELL":
            if ticker not in positions:raise ValueError("orphan sale")
            start,held,cost,cid,context=positions[ticker]
            if abs(qty-held)>max(1e-8,held*1e-8):
                raise ValueError("partial close not yet supported")
            net=qty*price-fee
            outcomes.append(TradeOutcome(cid,context,start,session,
                                         net/cost-1.,"actual"))
            del positions[ticker]
        else:raise ValueError("unexpected ledger side")
    return outcomes,positions
