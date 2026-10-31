import csv,statistics,pathlib
p=pathlib.Path('/opt/mts/sector-leadership-independent/universe_2019/forward_quarter_signals_2019_2020.csv')
rows=list(csv.DictReader(p.open()))
for r in rows:
 for k in ['year','quarter']:r[k]=int(r[k])
 for k in ['fwd_return_pct','mom6_pct','mom12_pct','above50','above200']:r[k]=float(r[k])
def rank(x):
 a=sorted(set(x));return [a.index(z)/(len(a)-1) if len(a)>1 else .5 for z in x]
for year in [2019,2020]:
 groups={}
 for r in rows:
  if r['year']==year:groups.setdefault((r['quarter'],r['sector']),[]).append(r)
 print('YEAR',year,'groups',len(groups))
 for label,fields in [('3_signal',['mom6_pct','mom12_pct','above50']),('3_signal_200',['mom6_pct','mom12_pct','above200']),('4_signal',['mom6_pct','mom12_pct','above50','above200']),('momentum_only',['mom6_pct','mom12_pct'])]:
  spreads=[];hits=0;top3=0;rankcorr=[]
  for g in groups.values():
   if len(g)!=5:continue
   rs=[rank([r[k] for r in g]) for k in fields]
   scores=[sum(z)/len(fields) for z in zip(*rs)]
   f=[r['fwd_return_pct'] for r in g]
   high=max(range(5),key=lambda i:(scores[i],-i));low=min(range(5),key=lambda i:(scores[i],i))
   spreads.append(f[high]-f[low]);hits+=f[high]>f[low]
   top3+=f[high]>=sorted(f,reverse=True)[2]
   # tie-aware pearson of midranks
   fr=rank(f)
   if len(set(scores))>1:rankcorr.append(statistics.correlation(scores,fr))
  print(label,'mean_spread',round(statistics.mean(spreads),2),'median_spread',round(statistics.median(spreads),2),'wins',hits,'/',len(spreads),'top3',top3,'/',len(spreads),'mean_rank_corr',round(statistics.mean(rankcorr),3))
