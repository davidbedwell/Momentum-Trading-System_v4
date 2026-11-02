import csv,statistics,math,pathlib
root=pathlib.Path('/opt/mts/sector-leadership-independent')
rows=list(csv.DictReader((root/'pilot_2019_sample.csv').open()))
for r in rows:r['ret']=float(r['return_2019_pct']);r['eps']=float(r['mean_eps_surprise_pct'])
out=[]
for sector in sorted(set(r['sector'] for r in rows)):
 g=sorted((r for r in rows if r['sector']==sector),key=lambda r:r['ret'],reverse=True)
 for i,r in enumerate(g):
  r['pilot_group']='top' if i==0 else 'bottom' if i==4 else 'middle'
  out.append(r)
  print(sector,r['symbol'],r['pilot_group'],r['ret'],r['eps'])
print('--- cohort summaries ---')
for c in ['top','middle','bottom']:
 g=[r for r in out if r['pilot_group']==c]
 print(c,'n',len(g),'mean_return',round(statistics.mean(r['ret'] for r in g),2),'mean_eps_surprise',round(statistics.mean(r['eps'] for r in g),2),'median_eps_surprise',round(statistics.median(r['eps'] for r in g),2))
x=[r['ret'] for r in rows];y=[r['eps'] for r in rows]
print('pooled_pearson_r',round(statistics.correlation(x,y),3))
with (root/'universe_2019'/'pilot_earnings_cohorts_2019.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['sector','symbol','pilot_group','return_pct','mean_eps_surprise_pct'])
 w.writerows([r['sector'],r['symbol'],r['pilot_group'],r['ret'],r['eps']] for r in out)
