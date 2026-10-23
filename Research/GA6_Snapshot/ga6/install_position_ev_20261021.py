from pathlib import Path
p=Path('/opt/mts/ga6/fast_portfolio_evaluator_20261021.py')
s=p.read_text()
assert 'ga6_completed_position_metrics' not in s
s=s.replace('pending=None;positions={};risk_positions={};','pending=None;positions={};completed_positions=[];position_entry_session={};risk_positions={};',1)
old='''     risk_positions[t]=PositionRisk(e0)
    risk_positions[t].buy(qty,price,fee_paid/(qty*price))'''
new='''     risk_positions[t]=PositionRisk(e0)
     position_entry_session[t]=i
    risk_positions[t].buy(qty,price,fee_paid/(qty*price))'''
assert old in s
s=s.replace(old,new,1)
old='''     if not risk_positions[t].remaining_shares:risk_positions.pop(t)'''
new='''     if not risk_positions[t].remaining_shares:
      closed=risk_positions.pop(t)
      entry_session=position_entry_session.pop(t)
      completed_positions.append((closed.cumulative_realized_pnl,closed.entry_equity,i-entry_session))'''
assert old in s
s=s.replace(old,new,1)
needle=' portfolio_diagnostics={'
assert needle in s
s=s.replace(needle,''' count=len(completed_positions)
 wins=sum(pnl>0 for pnl,_,_ in completed_positions)
 stats={'completed_trades':count,'win_rate':wins/count if count else None,
        'net_ev_entry_equity':sum(pnl/equity for pnl,equity,_ in completed_positions)/count if count else None,
        'avg_sessions':sum(days for _,_,days in completed_positions)/count if count else None,
        'net_realized_pnl':sum(pnl for pnl,_,_ in completed_positions),
        'open_positions_excluded':len(risk_positions),
        'basis':'actual completed cash-constrained positions net of fees; entry-time equity'}
 portfolio_diagnostics={''',1)
s=s.replace('"ga6_portfolio_diagnostics":portfolio_diagnostics,','"ga6_portfolio_diagnostics":portfolio_diagnostics,"ga6_completed_position_metrics":stats,',1)
compile(s,str(p),'exec')
p.write_text(s)
print('COMPILED AND INSTALLED EV ACCOUNTING')
