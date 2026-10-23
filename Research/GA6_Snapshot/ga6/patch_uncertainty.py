from pathlib import Path
p=Path('/opt/mts/ga6/evaluator_adapter.py');s=p.read_text();needle="    r['ga6_trade_metrics']=ga6";assert s.count(needle)==1;s=s.replace(needle,"    from ga6.episode_uncertainty import assess\n    r['ga6_episode_uncertainty']=assess(trades)\n"+needle);p.write_text(s)
p=Path('/opt/mts/ga6/runner.py');s=p.read_text();needle="+a.entry_mode).encode()).hexdigest()";assert s.count(needle)==1;s=s.replace(needle,"+digest_file(Path(__file__).resolve().parent / 'episode_uncertainty.py')"+needle);p.write_text(s)
print('Added episode-block bootstrap uncertainty and cache fingerprint')
