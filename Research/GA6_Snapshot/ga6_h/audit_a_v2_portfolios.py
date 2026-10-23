import sqlite3,json,pathlib
p=pathlib.Path('/opt/mts/ga6/runs/A_v2_full_evolution_20261022')
db=sqlite3.connect('file:'+str(p/'structural_evaluations.sqlite')+'?mode=ro',uri=True,timeout=30)
print('rows',db.execute('select count(*) from evaluations').fetchone()[0])
best=None;best_lcb=None; valid=0
for key,payload in db.execute('select key,result from evaluations'):
    r=json.loads(payload)
    c=r.get('cagr_diagnostic'); m=r.get('mdd_diagnostic')
    if c is None or m is None:continue
    valid+=1
    x={'key':key,'cagr':c,'mdd':m,'trades':r.get('ga6_completed_position_metrics',{}).get('completed_trades'),'avg_sessions':r.get('ga6_completed_position_metrics',{}).get('avg_sessions_per_trade'),'ev95':r.get('ga6_completed_position_metrics',{}).get('net_ev_lower_confidence_95')}
    if best is None or c>best['cagr']:best=x
    if x['ev95'] is not None and (best_lcb is None or x['ev95']>best_lcb['ev95']):best_lcb=x
print('portfolio_rows',valid)
print('best_cagr',json.dumps(best))
print('best_ev95',json.dumps(best_lcb))
db.close()
