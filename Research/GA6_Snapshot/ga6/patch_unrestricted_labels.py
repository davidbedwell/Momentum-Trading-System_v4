from pathlib import Path
p=Path('/opt/mts/ga6/runner.py');s=p.read_text()
a='_WORKER_POLICY=(blocked,membership,veto,cash_yield,niche_labels if entry_mode=="origin" else None)';b='_WORKER_POLICY=(blocked,membership,veto,cash_yield,niche_labels,entry_mode)';assert s.count(a)==1;s=s.replace(a,b)
a='blocked,membership,veto,cash_yield,niche_labels=_WORKER_POLICY';b='blocked,membership,veto,cash_yield,niche_labels,entry_mode=_WORKER_POLICY';assert s.count(a)==1;s=s.replace(a,b)
a='niche_labels=niche_labels)';b='niche_labels=niche_labels if entry_mode=="origin" else None,evidence_labels=niche_labels)';assert s.count(a)==1;s=s.replace(a,b);p.write_text(s)
p=Path('/opt/mts/ga6/evaluator_adapter.py');s=p.read_text();a='    labels=kwargs.get("niche_labels")\n    raw=ga6_raw_evaluate(*args, **kwargs)';b='    labels=kwargs.pop("evidence_labels",None)\n    if labels is None:labels=kwargs.get("niche_labels")\n    raw=ga6_raw_evaluate(*args, **kwargs)';assert s.count(a)==1;s=s.replace(a,b);p.write_text(s)
print('Unrestricted execution now retains independent 13-niche evidence labels')
