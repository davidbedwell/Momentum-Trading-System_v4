from pathlib import Path
p=Path('/opt/mts/ga6/runner.py');s=p.read_text()
a=" p.add_argument('--diagnostic-only',action='store_true')";b=a+"\n p.add_argument('--production',action='store_true')";assert s.count(a)==1;s=s.replace(a,b)
a=" if not a.diagnostic_only:raise ValueError('Research-only; explicit diagnostic flag required')";b=" if a.diagnostic_only==a.production:raise ValueError('Specify exactly one of --diagnostic-only or --production')";assert s.count(a)==1;s=s.replace(a,b)
a=" report={'status':'DIAGNOSTIC_ONLY','architecture':";b=" report={'status':'PRODUCTION_RESEARCH' if a.production else 'DIAGNOSTIC_ONLY','architecture':";assert s.count(a)==1;s=s.replace(a,b)
p.write_text(s)
print('Production mode added as explicit separate flag; unchanged evaluation and checkpoint algorithms')
