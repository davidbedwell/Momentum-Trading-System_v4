from ga6.policy_research import evaluate_policy

def split(paths,cutoff):
 train=[];valid=[];excluded=0
 for path in paths:
  if not path:continue
  first=str(path[0][0])[:10];last=str(path[-1][0])[:10]
  if last<cutoff:train.append(path)
  elif first>=cutoff:valid.append(path)
  else:excluded+=1
 return train,valid,excluded

def assess(paths,genes,cutoff,fee=.001,cash_daily=0.):
 train,valid,excluded=split(paths,cutoff)
 return {'train':evaluate_policy(train,genes,fee,cash_daily),'validation':evaluate_policy(valid,genes,fee,cash_daily),'excluded':excluded}
