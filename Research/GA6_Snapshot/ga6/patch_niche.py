from pathlib import Path
p=Path('/opt/mts/ga6/evaluator_adapter.py')
s=p.read_text()
s=s.replace('def enrich(result, trades):','def enrich(result, trades, niche_labels=None):')
s=s.replace("    r['ga6_trade_metrics']=ga6","    r['ga6_trade_metrics']=ga6\n    if niche_labels is not None:\n        from ga6.niche_evidence import summarize\n        from optimizer_v3 import NICHES\n        r['ga6_niche_evidence']=summarize(trades,niche_labels,NICHES)")
s=s.replace('    raw=ga6_raw_evaluate(*args, **kwargs)','    labels=kwargs.get("niche_labels")\n    raw=ga6_raw_evaluate(*args, **kwargs)')
s=s.replace('return enrich(raw,trades)','return enrich(raw,trades,labels)')
p.write_text(s)
print('GA6 per-niche evidence wired to evaluator')
