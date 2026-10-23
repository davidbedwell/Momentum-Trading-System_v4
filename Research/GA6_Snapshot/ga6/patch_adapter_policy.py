from pathlib import Path
p=Path('/opt/mts/ga6/evaluator_adapter.py');s=p.read_text()
needle='    return result\n'
assert s.count(needle)==1
addition='''    if args and trades:
        from ga6.prospective_replay import simulate
        from ga6.prospective_policy import Policy
        from ga6.chronological_validation import split
        paths=[]
        for tr in trades:
            rows=_INDEX_CACHE[key].get(tr['ticker'],[])
            begin=str(tr['entry_date'])[:10];end=str(tr['exit_date'])[:10]
            path=[row for row in rows if begin<=row[0]<=end]
            if len(path)>=3:paths.append(path)
        if paths:
            ordered=sorted(str(p[0][0])[:10] for p in paths)
            cutoff=ordered[(len(ordered)*7)//10]
            train,valid,excluded=split(paths,cutoff)
            daily=(1+kwargs['annual_cash_yield'])**(1/252)-1
            def summarize(group):
                reports=[simulate(path,Policy(),fee=kwargs.get('fee',.001),cash_daily=daily) for path in group]
                return {'count':len(reports),'mean_incremental':sum(x['incremental_net'] for x in reports)/len(reports) if reports else None}
            result['ga6_prospective_baseline']={'cutoff':cutoff,'train':summarize(train),'validation':summarize(valid),'excluded':excluded,'policy':'fixed_baseline_not_evolved'}
'''
s=s.replace(needle,addition+needle)
p.write_text(s)
print('Adapter now emits chronological prospective baseline')
