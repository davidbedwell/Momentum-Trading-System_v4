"""Fail-closed historical research input gate. No inference of earnings completeness."""
from pathlib import Path
import json
import pandas as pd

def preflight(bars, schedules, verified_tickers, *, discovery_end, evidence=None):
    errors=[]
    required={'date','symbol','Open','High','Low','Close','Volume','Stock Splits','Dividends','tradable_bar'}
    if not required.issubset(bars.columns):errors.append('missing required bar fields')
    if not len(bars):errors.append('empty bars')
    if errors:return {'passed':False,'errors':errors}
    d=bars.copy();d['date']=pd.to_datetime(d.date,errors='coerce')
    if d.date.isna().any():errors.append('invalid dates')
    if d.duplicated(['symbol','date']).any():errors.append('duplicate symbol/date')
    if d.date.max()>pd.Timestamp(discovery_end):errors.append('discovery boundary exceeded')
    for col in ('Open','High','Low','Close','Volume','Stock Splits','Dividends'):
        d[col]=pd.to_numeric(d[col],errors='coerce')
        if d[col].isna().any():errors.append('invalid '+col)
    if not errors:
        if (d[['Open','High','Low','Close']]<=0).any().any():errors.append('nonpositive OHLC')
        if ((d.High<d[['Open','Close','Low']].max(axis=1)) | (d.Low>d[['Open','Close','High']].min(axis=1))).any():errors.append('inconsistent OHLC')
        if (d[['Volume','Stock Splits','Dividends']]<0).any().any():errors.append('negative volume/action')
    symbols=set(d.symbol.astype(str))
    if symbols-set(verified_tickers):errors.append('unverified earnings tickers')
    if symbols-set(schedules):errors.append('missing earnings schedules')
    # A caller cannot self-attest historical schedule completeness with an empty array.
    if evidence is None or not isinstance(evidence,dict):errors.append('earnings provenance absent')
    else:
        if not evidence.get('source') or not evidence.get('coverage_audited') or not evidence.get('asof_timestamp_audited'):
            errors.append('earnings provenance incomplete')
        if not evidence.get('corporate_actions_verified'):
            errors.append('corporate actions unverified')
    return {'passed':not errors,'errors':errors,'symbols':len(symbols),'rows':len(d)}


def audit_available_dataset(root='/opt/mts/ga6_h'):
    root=Path(root)
    price=json.loads((root/'audits/price_audit_summary.json').read_text())
    derived=json.loads((root/'audits/derived_validation.json').read_text())
    problems=[]
    if price['bad_ohlc_files']:problems.append(f"{price['bad_ohlc_files']} files have OHLC inconsistencies")
    if price['bad_price_files']:problems.append(f"{price['bad_price_files']} files have invalid prices")
    if derived['sampled_files']<derived['total_files']:problems.append('derived validation sampled, not exhaustive')
    problems.append('earnings audit covers a different 503-security universe, not the 4967-security GA6-H universe')
    problems.append('current-listed survivor-only universe, not historical point-in-time membership')
    return {'production_preflight_passed':False,'price_files':price['file_count'],'price_rows':price['total_price_rows'],
            'derived_sampled':derived['sampled_files'],'blockers':problems}

if __name__=='__main__':
    print(json.dumps(audit_available_dataset(),indent=2))
