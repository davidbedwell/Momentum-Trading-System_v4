"""Evolve only on pre-cutoff trades; validation never enters selection."""
from ga6.chronological_validation import split
from ga6.policy_research import evolve,evaluate_policy

def train_validate(paths,rng,cutoff,population=32,generations=5,fee=.001,cash_daily=0.):
 train,valid,excluded=split(paths,cutoff)
 if len(train)<50 or len(valid)<50:
  return {'eligible':False,'reason':'insufficient independent trade paths','train_count':len(train),'validation_count':len(valid),'excluded':excluded}
 # All evolutionary selection is confined to training paths.
 history=evolve(train,rng,population,generations)
 from ga6.policy_genes import ExitGenes
 winner=ExitGenes(**max(history,key=lambda h:h['best']['score'])['genes'])
 return {'eligible':True,'genes':winner.__dict__,'train':evaluate_policy(train,winner,fee,cash_daily),'validation':evaluate_policy(valid,winner,fee,cash_daily),'excluded':excluded,'generations':generations}
