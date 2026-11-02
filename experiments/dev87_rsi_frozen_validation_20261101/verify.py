"""Audit persisted outputs without rerunning the study's accounting routines."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
P=Path(__file__).resolve().parent
v=json.loads((P/'verification.json').read_text());errors={}
for file,h in v['source_hashes'].items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h,file
mt=pd.read_csv(P/'metrics.csv');an=pd.read_csv(P/'annual.csv')
for era in ['2009-2018','2019-2025']:
 z=pd.read_csv(P/era/'monthly.csv');dy=pd.read_csv(P/era/'daily_nav.csv');cand=pd.read_csv(P/era/'candidate_features_flags.csv');sel=pd.read_csv(P/era/'selections.csv')
 assert (pd.to_datetime(cand.feature_date)<pd.to_datetime(cand.execution_date)).all()
 for (rid,kind),g in z.groupby(['strategy','kind']):
  r=g.net_return.to_numpy(); nav=np.cumprod(1+r);row=mt[(mt.period==era)&mt.strategy.eq(rid)&mt.kind.eq(kind)].iloc[0]
  np.testing.assert_allclose(nav,g.nav,atol=1e-12)
  np.testing.assert_allclose((1-g.fee)*(1+g.gross_return)-1,r,atol=1e-14)
  np.testing.assert_allclose(g.fee,g.turnover*.001,atol=1e-14)
  ar=an[an.period.eq(era)&an.strategy.eq(rid)&an.kind.eq(kind)]
  np.testing.assert_allclose(np.prod(1+ar.net_return),nav[-1],atol=1e-12)
  for yr,h in g.groupby(pd.to_datetime(g.execution_date).dt.year):
   np.testing.assert_allclose(np.prod(1+h.net_return)-1,ar[ar.year.eq(yr)].iloc[0].net_return,atol=1e-12)
  dn=np.r_[1,dy[f'{kind}:{rid}'].to_numpy()];mdd=1-np.min(dn/np.maximum.accumulate(dn))
  assert abs(mdd-row.daily_mdd)<1e-12
  assert abs(nav[-1]**(252/row.sessions)-1-row.cagr)<1e-12
  assert abs(r.mean()/r.std(ddof=1)*np.sqrt(12)-row.sharpe)<1e-12
  assert (g.terminal_close.to_numpy()==np.r_[np.zeros(len(g)-1,dtype=bool),True]).all()
  for rec in g.itertuples():
   endpoint=dy[(dy.date==rec.end_date)&dy.mark.eq('terminal_close' if rec.terminal_close else 'open')]
   assert len(endpoint)==1
   np.testing.assert_allclose(endpoint.iloc[0][f'{kind}:{rid}'],rec.nav,atol=1e-12)
  if kind=='selected':
   ss=sel[sel.strategy.eq(rid)&sel.executed]
   assert len(ss)==int(row.stock_months)
   assert int(g['count'].gt(0).sum())==row.active_months
   for date,cc in cand.groupby('execution_date'):
    expected=set(cc.loc[cc[rid],'ticker']);actual=set(sel[(sel.strategy==rid)&sel.execution_date.eq(date)].ticker);assert expected==actual
  errors[f'{era}:{kind}:{rid}']=float(np.max(abs(nav-g.nav)))
 assert dy.iloc[-1]['date']==v[era]['end'] and dy.iloc[-1]['mark']=='terminal_close'
out={'status':'PASS','source_hashes_verified':True,'persisted_accounting_metrics_annual_endpoints_and_memberships_verified':True,'max_saved_nav_error':max(errors.values()),'original_and_independent_ledger_errors':v['verification_errors']}
(P/'artifact_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
