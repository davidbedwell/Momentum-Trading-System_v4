from pathlib import Path
p=Path('/opt/mts/ga6/evaluator_adapter.py');s=p.read_text()
s=s.replace('def evaluate(*args, **kwargs):','_INDEX_CACHE={}\ndef evaluate(*args, **kwargs):')
s=s.replace('    return enrich(raw,trades,labels)','    result=enrich(raw,trades,labels)\n    if args and trades:\n        from ga6.path_replay import price_index,replay\n        prepared=args[0]\n        key=id(prepared)\n        if key not in _INDEX_CACHE:\n            _INDEX_CACHE.clear()\n            _INDEX_CACHE[key]=price_index(prepared)\n        result["ga6_exit_reentry_research"]=replay(trades,_INDEX_CACHE[key],fee=kwargs.get("fee",.001),cash_daily=(1+kwargs["annual_cash_yield"])**(1/252)-1)\n    return result')
p.write_text(s)
print('GA6 chronological path replay connected to evaluator diagnostics')
