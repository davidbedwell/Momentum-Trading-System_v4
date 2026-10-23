"""Provisional research launch inputs. NOT PIT-certified or crash-protected."""
import sys,json
from pathlib import Path
import pandas as pd
ROOT=Path('/opt/mts')
sys.path.insert(0,str(ROOT/'ga5_redesign'))
from canonical_engine import prepare,digest_file
raw=ROOT/'portfolio_evolution_dev80/dev80_raw_no_smci.parquet'
predictors=ROOT/'thunder-migration/mts-layered-run-20261007/Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet'
r=pd.read_parquet(raw,columns=['date','ticker','security_id'])
p=pd.read_parquet(predictors,columns=['effective_date','ticker','security_id','sector_id'])
joined=r.merge(p,left_on=['date','ticker','security_id'],right_on=['effective_date','ticker','security_id'],how='left',validate='one_to_one')
if len(joined)!=len(r) or joined.sector_id.isna().any() or r.ticker.nunique()!=79:raise ValueError('79-ticker source reconciliation failed')
if joined.groupby('ticker').sector_id.nunique().max()!=1:raise ValueError('Changing sector map requires dated features')
sector=joined.groupby('ticker').sector_id.first().to_dict()
feature=ROOT/'ga5_redesign/exploratory79_features.parquet'
prepare(raw,feature,sector_map=sector)
dates=sorted(pd.to_datetime(r.date).dt.strftime('%Y-%m-%d').unique().tolist())
# Observed bars are NOT independent historical membership evidence.
membership=[[str(date)[:10],str(ticker),True] for date,ticker in r[['date','ticker']].itertuples(index=False,name=None)]
blocked=json.loads((ROOT/'ga5_redesign/earnings_reconciliation_79.json').read_text())['blocked']
policy={'membership':membership,'risk_veto':{d:True for d in dates},'blocked':blocked,'cash_proxy_annual_yield':0.03}
path=ROOT/'ga5_redesign/exploratory79_policy.json'
path.write_text(json.dumps(policy,separators=(',',':')))
manifest={'status':'EXPLORATORY_UNCERTIFIED','ticker_count':79,'raw_sha256':digest_file(raw),'predictor_sha256':digest_file(predictors),'earnings_reconciliation_sha256':digest_file(ROOT/'ga5_redesign/earnings_reconciliation_79.json'),'features_sha256':digest_file(feature),'policy_sha256':digest_file(path),'limitations':['Membership approximated by observed price bars, not verified historical index eligibility','Sector classification is static retrospectively assigned','Crash-risk veto is uniformly permissive; defensive risk control not tested','Earnings event dates retrospectively sourced, availability timing unverified','Cash proxy assumes 3 percent annual yield, not historical SGOV','Research diagnostic only; no blind/holdout promotion']}
(ROOT/'ga5_redesign/exploratory79_assumptions.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'features':str(feature),'policy':str(path),'rows':len(r),'tickers':79,'manifest':manifest},indent=2))
