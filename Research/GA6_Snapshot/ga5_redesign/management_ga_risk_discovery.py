import numpy as np,pandas as pd,json
from pathlib import Path
from sklearn.metrics import roc_auc_score
p=Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019/niche0001_signal_study')
df=pd.read_parquet(p/'intratrade_time_t_samples.parquet')
df.date=pd.to_datetime(df.date)
cols=['ret5','ret20','vol','rs','breadth']
train=df[df.date<'2016-12-15'];test=df[df.date>='2017-01-01']
rng=np.random.default_rng(20261020)
# percentile thresholds fit strictly on training history
qs=np.array([.1,.2,.3,.4,.5,.6,.7,.8,.9])
thr=np.array([np.nanquantile(train[c],qs) for c in cols])
def matrix(d):
 x=d[cols].to_numpy(dtype=float)
 return np.concatenate([(x[:,j,None]>=thr[j]).astype(np.uint8) for j in range(5)]+[(x[:,j,None]<thr[j]).astype(np.uint8) for j in range(5)],axis=1)
X=matrix(train);Y=train.future_adverse5.to_numpy(dtype=np.uint8)
Z=matrix(test);T=test.future_adverse5.to_numpy(dtype=np.uint8)
# each gene is 1 of 90 threshold conditions; chromosome ANDs 1-4 genes
def evaluate(chrom,x,y):
 mask=np.ones(len(y),dtype=bool)
 for g in chrom:mask &= x[:,g].astype(bool)
 n=mask.sum()
 if n<max(100,int(len(y)*.01)) or n>len(y)*.5:return -1e3,0,0
 rate=y[mask].mean();base=y.mean()
 # reward concentrated risk with sufficient coverage, penalize tiny sets
 return float((rate-base)*np.sqrt(n/len(y))),float(rate),float(n/len(y))
pop=[tuple(sorted(rng.choice(90,size=int(rng.integers(1,5)),replace=False).tolist())) for _ in range(140)]
seen={};history=[]
for gen in range(120):
 for c in pop:
  if c not in seen:seen[c]=evaluate(c,X,Y)
 ranked=sorted(seen,key=lambda c:seen[c][0],reverse=True)
 history.append({'generation':gen,'evaluated':len(seen),'best_training_fitness':seen[ranked[0]][0]})
 elite=ranked[:35];nextpop=elite[:]
 while len(nextpop)<140:
  a,b=rng.choice(len(elite),2,replace=True)
  genes=set(elite[a])|set(elite[b]) if rng.random()<.5 else set(elite[a])
  if rng.random()<.75:
   if rng.random()<.5 and len(genes)>1:genes.remove(int(rng.choice(list(genes))))
   else:genes.add(int(rng.integers(90)))
  while len(genes)>4:genes.remove(int(rng.choice(list(genes))))
  nextpop.append(tuple(sorted(genes)))
 pop=nextpop
ranked=sorted(seen,key=lambda c:seen[c][0],reverse=True)
def decode(g):
 j=(g%45)//9;q=g%9
 return cols[j]+(" >= " if g<45 else " < ")+format(thr[j,q],".5f")
out=[]
for c in ranked[:30]:
 fit,rate,coverage=seen[c];score,hr,hc=evaluate(c,Z,T)
 out.append({'rules':[decode(g) for g in c],'train_risk_rate':rate,'train_coverage':coverage,'holdout_risk_rate':hr,'holdout_coverage':hc,'holdout_lift':hr/T.mean() if hc else None,'holdout_score':score})
result={'train_n':len(Y),'test_n':len(T),'test_base_rate':float(T.mean()),'unique_chromosomes_evaluated':len(seen),'generations':120,'top_candidates':out,'history':history}
(p/'management_ga_risk_discovery.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='history'},indent=2),flush=True)
