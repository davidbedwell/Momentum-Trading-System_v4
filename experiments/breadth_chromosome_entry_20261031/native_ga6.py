"""Separate native GA6 audit sensitivity; never pool with common replay R."""
import pandas as pd
from study import ROOT,load_features,contrast,bh,sha

def main():
 p='/opt/mts/ga6/runs/independent_review/trade_entries_prior_features.parquet'
 t=pd.read_parquet(p,columns=['chromosome','ticker','entry_date','exit_date','sessions','trade_return','mae','mfe']);t['entry_date']=pd.to_datetime(t.entry_date);t['exit_date']=pd.to_datetime(t.exit_date)
 f,sectors=load_features();t=t.join(f,on='entry_date');t['year']=t.entry_date.dt.year;t['win']=t.trade_return.gt(0);t['r']=t.trade_return
 t.to_csv(ROOT/'native_ga6_trades.csv.gz',index=False)
 t.groupby(['year','regime']).agg(n=('r','size'),chromosomes=('chromosome','nunique'),entry_dates=('entry_date','nunique'),mean_return=('r','mean'),win_rate=('win','mean'),mean_saved_mae=('mae','mean'),spy21=('spy_forward21','mean')).to_csv(ROOT/'native_ga6_results.csv')
 rows=[]
 for year,g in t.groupby('year'):
  z=contrast(g,g.regime.eq('weak'),g.regime.eq('strong'))
  if z:rows.append(dict(year=year,**z))
 z=pd.DataFrame(rows);z['q_bh']=bh(z.p);z.to_csv(ROOT/'native_ga6_contrasts.csv',index=False)
 (ROOT/'native_ga6_source.txt').write_text(p+'\nsha256='+sha(p)+'\n'+str(t.entry_date.min())+' through '+str(t.entry_date.max())+'\n')
 print(z.to_string(index=False))
if __name__=='__main__':main()
