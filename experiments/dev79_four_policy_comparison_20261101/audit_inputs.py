"""Read-only identity/price reconciliation and split-continuity evidence."""
import json
from pathlib import Path
import pandas as pd
from comparison import SOURCE,ROOT,digest

def main():
    raw=pd.read_parquet(SOURCE)
    enriched_path=Path('/opt/mts/ga6/data/ga6d_defensive_features.parquet')
    cols=['date','ticker','open','high','low','close','dividends','stock_splits','security_id']
    enriched=pd.read_parquet(enriched_path,columns=cols)
    merged=raw.merge(enriched,on=['date','ticker'],suffixes=('_raw','_enriched'),validate='one_to_one')
    differences={k:float((merged[k+'_raw']-merged[k+'_enriched']).abs().max()) for k in cols[2:-1]}
    assert len(merged)==len(raw)==len(enriched) and max(differences.values())==0
    assert (merged.security_id_raw==merged.security_id_enriched).all()
    rows=raw.sort_values(['ticker','date']).copy();rows['previous_close']=rows.groupby('ticker').close.shift(1)
    rows['open_ratio']=rows.open/rows.previous_close
    events=rows[rows.stock_splits>0].copy()
    events['error_adjusted']=(events.open_ratio-1).abs()
    events['error_if_unadjusted']=(events.open_ratio*events.stock_splits-1).abs()
    major=events.stock_splits>=1.5
    out=dict(raw_path=str(SOURCE),raw_sha256=digest(SOURCE),enriched_path=str(enriched_path),enriched_sha256=digest(enriched_path),joined_rows=len(merged),price_max_absolute_differences=differences,identity_matches=True,split_events=len(events),major_split_events=int(major.sum()),major_splits_favoring_adjusted=int((major&(events.error_adjusted<events.error_if_unadjusted)).sum()),split_basis_note='Continuity heuristic supports split-adjusted accounting, not vendor certification; no share multiplier.',raw_volume_min=float(raw.volume.min()),raw_volume_max=float(raw.volume.max()),enriched_volume_warning='Enriched volume is a signed transformed feature; raw archived volume used instead',per_ticker=raw.groupby('ticker').agg(start=('date','min'),end=('date','max'),bars=('date','size')).astype(str).to_dict('index'))
    p=ROOT/'artifacts';p.mkdir(exist_ok=True);(p/'input_audit.json').write_text(json.dumps(out,indent=2));events.to_csv(p/'split_continuity.csv',index=False)
    print(json.dumps({k:v for k,v in out.items() if k!='per_ticker'},indent=2))
if __name__=='__main__':main()
