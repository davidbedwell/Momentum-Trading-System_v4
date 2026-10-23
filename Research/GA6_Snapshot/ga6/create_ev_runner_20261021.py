from pathlib import Path
root=Path('/opt/mts/ga6')
src=(root/'production_portfolio_20261021.py').read_text()
src=src.replace('from ga6.portfolio_pareto_20261021 import fitness, rank_scored','from ga6.ev_selection_20261021 import fitness, rank_scored')
src=src.replace('scored=rank_scored(scored)','scored=rank_scored(scored)')
src=src.replace("if best is None or scored[0][0]>best['fitness']:","if best is None or scored[0][0]>best['fitness']:")
src=src.replace("'architecture':'GA6 EV-led niche-protected evolutionary population'","'architecture':'GA6 completed-position net-EV conservative selection'")
src=src.replace("'research_validity':'NICHE_ENTRY_HOLD_EXIT_SINGLE_TRADE_RETROSPECTIVE_NOT_OOS'","'research_validity':'IN_SAMPLE_EV_DISCOVERY_NOT_OUT_OF_SAMPLE_CERTIFIED'")
src=src.replace('from ga6.fast_portfolio_evaluator_20261021 import evaluate','from ga6.fast_portfolio_evaluator_20261021 import evaluate')
(root/'production_ev_20261021.py').write_text(src)
selection='''"""Completed-position EV selection. One score, no CAGR/MDD in breeding."""
from math import isfinite,sqrt
def fitness(r):
 m=r.get('ga6_completed_position_metrics',{})
 n=m.get('completed_trades',0)
 ev=m.get('net_ev_entry_equity')
 if not n or ev is None or not isfinite(float(ev)):return -100.
 # Conservative effective sample size: correlated trades can overstate evidence.
 # This penalty is deliberately a provisional regularizer, not a confidence bound.
 return float(ev)*n/(n+100)
def rank_scored(scored):
 return sorted(scored,key=lambda x:(-x[0],x[1].identity()))
'''
(root/'ev_selection_20261021.py').write_text(selection)
compile(src,str(root/'production_ev_20261021.py'),'exec')
compile(selection,str(root/'ev_selection_20261021.py'),'exec')
print('EV_SELECTION_RUNNER_CREATED')
