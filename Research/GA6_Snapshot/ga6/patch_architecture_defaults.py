from pathlib import Path
p=Path('/opt/mts/ga6/runner.py');s=p.read_text()
a="p.add_argument('--population',type=int,default=28)"
b="p.add_argument('--population',type=int,default=500)"
c="p.add_argument('--entry-mode',choices=('origin','unrestricted'),default='origin')"
d="p.add_argument('--entry-mode',choices=('origin','unrestricted'),default='unrestricted')"
assert s.count(a)==1 and s.count(c)==1
s=s.replace(a,b).replace(c,d)
p.write_text(s)
print('GA6 defaults: 500 candidates; unrestricted cross-niche portfolio entry')
