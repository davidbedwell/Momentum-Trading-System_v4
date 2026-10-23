"""Validate derived dataset against raw data, plus causal feature and label alignment."""
import json, random
from pathlib import Path
import numpy as np
import pandas as pd
R=Path('/opt/mts/ga6_h'); files=sorted((R/'derived_v1').glob('*.parquet'))
rng=random.Random(20261022)
sample=rng.sample(files,min(120,len(files)))
fail=[]
for path in sample:
    d=pd.read_parquet(path)
    raw=pd.read_parquet(R/'data/prices'/path.name)
    if len(d)!=len(raw): fail.append((path.stem,'length'));continue
    if not d['date'].equals(raw['date']): fail.append((path.stem,'date'));continue
    adj=d['Adj Close'].where(d['Adj Close'].gt(0))
    for n in (5,10,20,40,60,120,252):
        a=d[f'return_{n}'].to_numpy(float)
        b=(adj/adj.shift(n)-1).to_numpy(float)
        if not np.allclose(a,b,equal_nan=True,rtol=1e-10,atol=1e-12):fail.append((path.stem,f'return_{n}'))
    for n in (1,5,10,20,40):
        a=d[f'forward_adj_return_{n}'].to_numpy(float)
        b=(adj.shift(-n)/adj-1).to_numpy(float)
        if not np.allclose(a,b,equal_nan=True,rtol=1e-10,atol=1e-12):fail.append((path.stem,f'forward_{n}'))
    # Prefix invariance: features at t do not change if later observations disappear.
    cut=max(60,len(d)//2)
    for n in (5,10,20,40,60,120,252):
        if cut>n and not np.allclose(d[f'return_{n}'].iloc[:cut],(adj.iloc[:cut]/adj.iloc[:cut].shift(n)-1),equal_nan=True):fail.append((path.stem,'prefix'))
report={'total_files':len(files),'sampled_files':len(sample),'failures':fail,'passed':not fail,
 'caveats':['Forward labels must never be exposed to ranking at decision time.',
 'Raw close and adjusted close have different corporate-action treatment; execution requires unadjusted next-open prices and explicit dividend/split ledger.',
 'No quarterly embargo integrated into trade evaluator yet.']}
(R/'audits/derived_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
if fail:raise SystemExit(1)
