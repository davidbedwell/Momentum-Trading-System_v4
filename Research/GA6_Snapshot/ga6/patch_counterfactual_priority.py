from pathlib import Path
p=Path('/opt/mts/ga6/portfolio_counterfactuals.py');s=p.read_text();a="ordered=sorted(opportunities,key=lambda x:(x['decision_date'],x['ticker']))";b="ordered=sorted(opportunities,key=lambda x:(x['decision_date'],0 if x['action']=='EXIT' else 1 if x['action']=='HOLD' else 2,-float(x.get('priority',0)),x['ticker']))";assert s.count(a)==1;s=s.replace(a,b)
a="target=capital*min(1.,max(0.,float(o.get('weight',.03))))";b="target=(cash+sum(q*float(o.get('mark_prices',{}).get(t,price)) for t,q in active.items()))*min(1.,max(0.,float(o.get('weight',.03))))";assert s.count(a)==1;s=s.replace(a,b);p.write_text(s)
print('Exit-before-entry sequencing and signal-priority capital competition')
