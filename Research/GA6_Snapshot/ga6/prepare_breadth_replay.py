import pathlib,hashlib
root=pathlib.Path('/opt/mts/ga6');source=(root/'structural_evolution_v3_20261022/structural_portfolio_evaluator.py').read_text();out=root/'research_breadth_replay_evaluator.py'
old='pending=(ds,exits,[(t,w) for t,w,_ in entries if t not in risk_pending],adjustments)'
new='pending=(ds,exits,[(t,w) for t,w,_ in entries if t not in risk_pending and (breadth_limit is None or float(rows[t].get("ga4_breadth_above_sma_200__v1",float("nan")))<=breadth_limit)],adjustments)'
assert source.count(old)==1
source=source.replace('niche_labels=None,entry_tree=None):','niche_labels=None,entry_tree=None,breadth_limit=None):',1).replace(old,new)
out.write_text(source);print('CREATED',out,'SHA256',hashlib.sha256(source.encode()).hexdigest())
