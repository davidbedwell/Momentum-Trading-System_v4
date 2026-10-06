import runpy,pandas as pd
ns=runpy.run_path('/home/ubuntu/Momentum-Trading-System_v4/scripts/run_path_a_2020_failure_autopsy_20261004.py')
g=ns['g'].copy(); rp=ns['rolling_pct']; eps=ns['episodes']; control=ns['control']
g['dd_badpct']=rp(-g.dd)
thr=.95
parts=pd.DataFrame(dict(funding=g.funding_pct>=thr,dd=g.dd_badpct>=thr,vvix=g.vvix_pct>=thr,b20=g.b20_badpct>=thr))
raw=parts.sum(axis=1)>=4
s=raw.rolling(3,min_periods=3).sum().ge(3)
mask=s.copy()
for a,b in list(eps.values())+[control]:
    mask.loc[a:b]=False
starts=mask & ~mask.shift(1,fill_value=False)
for dt in starts.index[starts]:
    window=g.loc[dt-pd.Timedelta(days=10):dt+pd.Timedelta(days=20),['dd','b20','vix','vvix','funding','funding_pct']]
    print('\nFALSE_START',dt.date(),'state',g.loc[dt,['dd','b20','vix','vvix','funding','funding_pct']].to_dict())
    print('next20_min_median_dd',float(window.dd.min()),'rows',len(window))
