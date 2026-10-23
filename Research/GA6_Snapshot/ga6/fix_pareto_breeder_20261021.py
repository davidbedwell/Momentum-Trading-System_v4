from pathlib import Path
r=Path('/opt/mts/ga6')
p=r/'breeder_portfolio_20261021.py'
x=(r/'breeder.py').read_text()
x=x.replace('ranked=sorted(scored,key=lambda x:(-x[0],x[1].identity()))','ranked=list(scored) # Pareto fronts and crowding already ranked by caller',1)
p.write_text(x)
q=r/'production_portfolio_20261021.py'
s=q.read_text().replace('from ga6.breeder import breed_ga6','from ga6.breeder_portfolio_20261021 import breed_ga6',1)
s=s.replace('digest_file(Path(__file__).resolve().parent / "breeder.py")','digest_file(Path(__file__).resolve().parent / "breeder_portfolio_20261021.py")',1)
s=s.replace('digest_file(Path(__file__).resolve().parent / "guarded_evaluator_ga6.py")','digest_file(Path(__file__).resolve().parent / "position_equity_risk_20261021.py")',1)
s=s.replace('digest_file(Path(__file__).resolve().parent.parent / "ga5_redesign" / "shadow_niche_single_exit.py")','digest_file(Path(__file__).resolve().parent / "fast_portfolio_evaluator_20261021.py")',1)
q.write_text(s)
compile(s,str(q),'exec');compile(x,str(p),'exec')
print('PARETO_BREEDER_INTEGRATED')
