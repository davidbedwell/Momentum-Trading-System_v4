import sqlite3,json,pathlib
p=pathlib.Path('/opt/mts/ga6/runs/A_v2_full_evolution_20261022')
db=sqlite3.connect('file:'+str(p/'structural_evaluations.sqlite')+'?mode=ro',uri=True)
keys=['c815bfda0dd8318e0fc377eaad576578bb36e715014baf8bab19a0a61c8c3f8c','ed2c09c9527d584bcf7084a25b4ff90d3cb7b2f963432b2b37aafe0a6d5086de']
for key in keys:
 row=db.execute('select result from evaluations where key=?',(key,)).fetchone()
 if row is None:print('MISSING',key);continue
 r=json.loads(row[0])
 print(json.dumps({'key':key,'first_date':r.get('first_date'),'last_date':r.get('last_date'),'sessions':r.get('sessions'),'cagr':r.get('cagr_diagnostic'),'mdd':r.get('mdd_diagnostic'),'final_nav':r.get('final_nav'),'position_metrics':r.get('ga6_completed_position_metrics'),'portfolio_diagnostics':r.get('ga6_portfolio_diagnostics'),'risk_pending':r.get('ga6_risk_pending_at_end'),'reconciliation':r.get('reconciliation'),'result_keys':list(r)},default=str))
db.close()
