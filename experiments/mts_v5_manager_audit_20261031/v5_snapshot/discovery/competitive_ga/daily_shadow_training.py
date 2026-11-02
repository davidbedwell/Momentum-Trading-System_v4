"""Daily causal shadow training records; never sends orders or updates on unmatured outcomes."""
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass(frozen=True)
class ShadowPrediction:
    session: int
    ticker: str
    chromosome: str
    family: str
    predicted_edge: float
    horizon: int
    selected: bool = False

@dataclass
class DailyShadowTrainer:
    predictions: list = field(default_factory=list)
    matured: list = field(default_factory=list)
    weights: dict = field(default_factory=dict)
    aggregates: dict = field(default_factory=dict)
    last_session: int = -1

    def record_close(self, session, candidates):
        if session <= self.last_session:
            raise ValueError('sessions must be strictly chronological')
        for p in candidates:
            if p.session != session or p.horizon < 1:
                raise ValueError('invalid prediction session/horizon')
        self.predictions.extend(candidates)
        self.last_session = session

    def mature(self, session, realized_net_returns):
        """Caller supplies independently calculated net outcome keyed by (origin_session,ticker,chromosome)."""
        if session > self.last_session:
            raise ValueError('cannot mature beyond processed session')
        pending=[]
        new_count=0
        for p in self.predictions:
            if p.session + p.horizon > session:
                pending.append(p)
                continue
            key=(p.session,p.ticker,p.chromosome)
            if key not in realized_net_returns:
                pending.append(p)
                continue
            actual=float(realized_net_returns[key])
            if not __import__('math').isfinite(actual):
                raise ValueError('nonfinite matured return')
            self.matured.append((p,actual))
            group=(p.family,p.chromosome)
            n,total=self.aggregates.get(group,(0,0.))
            self.aggregates[group]=(n+1,total+actual)
            new_count+=1
        self.predictions=pending
        self.weights={key:{'observations':n,'mean_net_return':total/n} for key,(n,total) in self.aggregates.items()}
        return new_count
