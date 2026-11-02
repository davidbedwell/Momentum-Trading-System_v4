"""Realized FIFO trade statistics from actual funded fill ledger."""
from collections import defaultdict

def trade_statistics(fills):
    lots=defaultdict(list);pnl=[];holding=[];unmatched=0
    for f in fills:
        key=f['ticker'];act=f['action'];q=float(f['quantity']);px=float(f['price']);fee=float(f['notional'])*.0001  # slippage is already included in execution price
        if act in ('ENTRY','ADD'):
            lots[key].append([q,px,fee]);continue
        if act not in ('EXIT','REPLACE','REDUCE'):continue
        remaining=q;realized=0.;basis=0.
        while remaining>1e-8 and lots[key]:
            lot=lots[key][0];take=min(remaining,lot[0]);fraction=take/lot[0]
            realized+=take*(px-lot[1])-lot[2]*fraction
            basis+=take*lot[1];lot[0]-=take;lot[2]*=(1-fraction);remaining-=take
            if lot[0]<1e-8:lots[key].pop(0)
        if remaining>1e-8:unmatched+=1
        if basis>0:pnl.append(realized-fee)
    wins=[x for x in pnl if x>0];losses=[x for x in pnl if x<0]
    return dict(realized_closures=len(pnl),wins=len(wins),losses=len(losses),win_rate=len(wins)/len(pnl) if pnl else None,
                avg_win_currency=sum(wins)/len(wins) if wins else None,avg_loss_currency=sum(losses)/len(losses) if losses else None,
                profit_factor=sum(wins)/-sum(losses) if losses else None,net_expectancy_currency=sum(pnl)/len(pnl) if pnl else None,
                unmatched_closures=unmatched,holding_period_status='pending_entry_date_matching',open_lots=sum(len(v) for v in lots.values()))
