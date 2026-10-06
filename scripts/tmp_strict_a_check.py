import runpy,pandas as pd
ns=runpy.run_path('/home/ubuntu/Momentum-Trading-System_v4/scripts/run_path_a_2020_failure_autopsy_20261004.py')
g=ns['g'].copy()
rp=ns['rolling_pct']
eps=ns['episodes']
control=ns['control']
g['dd_badpct']=rp(-g.dd)
def test(thr,k,confirm):
    parts=pd.DataFrame(dict(funding=g.funding_pct>=thr,dd=g.dd_badpct>=thr,vvix=g.vvix_pct>=thr,b20=g.b20_badpct>=thr))
    s=(parts.sum(axis=1)>=k).rolling(confirm,min_periods=confirm).sum().ge(confirm)
    mask=s.copy()
    for a,b in list(eps.values())+[control]:
        mask.loc[a:b]=False
    starts=mask & ~mask.shift(1,fill_value=False)
    out=dict(thr=thr,k=k,confirm=confirm,false_eps=int(starts.sum()),false_days=int(mask.sum()))
    for e,(a,b) in eps.items():
        z=s.loc[a:b]
        z=z[z]
        out[e]=None if z.empty else str(z.index[0].date())
    z=s.loc[control[0]:control[1]]
    z=z[z]
    out['2015']=None if z.empty else str(z.index[0].date())
    return out
rows=[test(t,k,c) for t in [.80,.85,.90,.95] for k in [2,3,4] for c in [1,2,3,5]]
ranked=sorted(rows,key=lambda x:(x['false_eps'],sum(x[e] is None for e in eps),x['2020'] or '9999'))
for r in ranked[:25]:
    print(r)
