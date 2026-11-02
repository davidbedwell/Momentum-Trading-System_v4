from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parent
m=json.loads((R/'run_metadata.json').read_text());z=pd.read_csv(R/'pooled_results.csv');t=pd.read_csv(R/'trades_with_features.csv.gz',parse_dates=['entry_date','feature_date'])
assert len(z)==525 and not z.duplicated(['analysis_set','system','feature','outcome']).any()
assert z.q_bh.dropna().between(0,1).all() and z.p_bonferroni.dropna().between(0,1).all()
assert (z.p>=z.p_month_cluster-1e-14).all() and (z.p>=z.p_hac63-1e-14).all() and (z.p>=z.p_hac126-1e-14).all()
assert len(t)==m['trades'] and (t.feature_date<t.entry_date).all()
assert t.close_mae_proxy.dropna().le(0).all()
assert set(z.outcome)=={'r','win','close_mae_proxy'}
for p,digest in m['hashes'].items():
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest,p
assert np.isfinite(z.effect).all()
print('PASS: 525 unique corrected tests; chronology; proxy bounds; input/code hashes; reconciled trade counts')
