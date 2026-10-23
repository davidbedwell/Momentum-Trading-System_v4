from pathlib import Path
p=Path('/opt/mts/ga6/evaluator_adapter.py');s=p.read_text()
a="train_validate(paths,random.Random(6106),cutoff,population=8,generations=2,fee="
b="train_validate(paths,random.Random(6106),cutoff,population=32,generations=5,fee="
assert s.count(a)==1
s=s.replace(a,b);p.write_text(s)
print('Policy search restored from 8x2 diagnostic shortcut to 32x5')
