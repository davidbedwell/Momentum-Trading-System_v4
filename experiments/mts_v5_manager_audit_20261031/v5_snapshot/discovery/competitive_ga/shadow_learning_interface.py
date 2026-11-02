"""Causal learning view of independently matured native shadow outcomes.
Research features only: never train on same-session or future exits.
"""
from collections import defaultdict
from math import sqrt

class ShadowLearningView:
    def __init__(self, prior_strength=20, min_samples=5, uncertainty_penalty=.5):
        self.outcomes=[]
        self.prior_strength=prior_strength
        self.min_samples=min_samples
        self.uncertainty_penalty=uncertainty_penalty
        self.seen=set()

    def ingest(self,outcome):
        if outcome.maturity_session<=outcome.decision_session:
            raise ValueError('noncausal maturity')
        key=(outcome.family,outcome.chromosome_id,outcome.genome_hash,outcome.ticker,outcome.context,outcome.decision_session,outcome.maturity_session)
        if key in self.seen:raise ValueError('duplicate shadow outcome')
        self.seen.add(key)
        self.outcomes.append(outcome)

    def snapshot(self,asof_session):
        rows=[o for o in self.outcomes if o.maturity_session<asof_session]
        prior=sum(o.net_r for o in rows)/len(rows) if rows else 0.
        groups=defaultdict(list)
        for o in rows:
            controlling,specialized,distance=o.context
            fit='MATCH' if controlling is not None and controlling==specialized else 'OTHER'
            bucket='NEAR' if distance is not None and distance<=.5 else 'FAR_OR_UNKNOWN'
            groups[(o.family,o.chromosome_id,o.genome_hash,controlling,fit,bucket)].append(o.net_r)
        estimates={}
        for key,values in groups.items():
            n=len(values)
            if n<self.min_samples:continue
            mean=(sum(values)+self.prior_strength*prior)/(n+self.prior_strength)
            raw=sum(values)/n
            se=sqrt(sum((x-raw)**2 for x in values)/(n*(n-1))) if n>1 else 0.
            estimates[key]={'net_ev':mean,'uncertainty':se,'conservative_ev':mean-self.uncertainty_penalty*se,'samples':n}
        return {'asof_session':asof_session,'matured_count':len(rows),'estimates':estimates}
