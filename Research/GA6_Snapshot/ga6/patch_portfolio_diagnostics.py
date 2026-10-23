from pathlib import Path
p=Path('/opt/mts/ga6/guarded_evaluator_ga6.py');s=p.read_text()
needle=' return {"status":"GUARDED_RESEARCH_ONLY"'
assert s.count(needle)==1
addition=''' gross_notional=gross_buy+gross_sell
 average_nav=sum(v for _,v in nav)/len(nav)
 turnover=gross_notional/(2*average_nav*years) if average_nav>0 else None
 portfolio_diagnostics={'annualized_two_way_turnover':turnover,'executed_buy_notional':gross_buy,'executed_sell_notional':gross_sell,'fee_drag_starting_capital':fees/starting_cash,'cash_yield_earned':ledger.cash_yield_total,'settlement_enforced':True,'capacity_limit':max_positions,'rejected_capacity':rejected['capacity'],'rejected_unsettled':rejected['unsettled'],'nav_observations':len(nav)}
'''
s=s.replace(needle,addition+needle)
needle='"reconciliation":{"portfolio_basis"'
assert s.count(needle)==1
s=s.replace(needle,'"ga6_portfolio_diagnostics":portfolio_diagnostics,"reconciliation":{"portfolio_basis"')
p.write_text(s)
print('Portfolio diagnostics derived from executed fills and reconciled ledger')
