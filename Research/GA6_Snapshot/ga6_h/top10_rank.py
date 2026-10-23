import sqlite3,json
p='/opt/mts/ga6/runs/A_v2_full_evolution_20261022/structural_evaluations.sqlite'
c=sqlite3.connect('file:'+p+'?mode=ro',uri=True)
rows=c.execute("select key,json_extract(result,'$.cagr_diagnostic'),json_extract(result,'$.mdd_diagnostic'),json_extract(result,'$.ga6_completed_position_metrics.completed_trades') from evaluations order by json_extract(result,'$.cagr_diagnostic') desc limit 15").fetchall()
print(json.dumps(rows))
