"""Explicit close-known research stress controls; no estimated market inputs."""
from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType

@dataclass(frozen=True)
class RiskSnapshot:
    as_of: str
    # ticker -> (stop loss fraction, gap loss fraction, correlated group)
    exposures: dict
    max_loss: float = .02
    max_group_weight: float = .30
    max_gross: float = 1.
    max_open_gap: float = .10
    reference_close: dict = None

    def __post_init__(self):
        for v in (self.max_loss,self.max_group_weight,self.max_gross,self.max_open_gap):
            if not isfinite(v) or not 0 < v <= 1: raise ValueError('invalid risk limit')
        for stop,gap,group in self.exposures.values():
            if not group or not all(isfinite(v) and 0 <= v <= 1 for v in (stop,gap)):
                raise ValueError('invalid exposure risk')
        refs=dict(self.reference_close or {})
        if any(not isfinite(v) or v <= 0 for v in refs.values()): raise ValueError('invalid reference close')
        object.__setattr__(self,'exposures',MappingProxyType(dict(self.exposures)))
        object.__setattr__(self,'reference_close',MappingProxyType(refs))

    def metrics(self, weights):
        if set(weights)-set(self.exposures): raise ValueError('missing incumbent risk')
        groups={}
        loss=0.
        for t,w in weights.items():
            stop,gap,g=self.exposures[t]
            loss+=w*max(stop,gap)
            groups[g]=groups.get(g,0.)+w
        return loss,max(groups.values(),default=0.),sum(weights.values())

    def constrain(self, existing, targets, ordered, bars):
        # Reductions always proceed; do not sell incumbents merely to fund risk.
        weights={t:min(w,targets.get(t,w)) for t,w in existing.items()}
        self.metrics(weights)
        rejected=[]
        for s in ordered:
            t=s.ticker
            if t not in targets or targets[t] <= weights.get(t,0.): continue
            if t not in self.exposures or t not in self.reference_close:
                targets[t]=weights.get(t,0.);rejected.append((t,'missing risk/reference'));continue
            # Split-adjusted reference: an overnight split is not a price gap.
            gap=abs(bars[t].open*bars[t].split/self.reference_close[t]-1)
            if gap > self.max_open_gap:
                targets[t]=weights.get(t,0.);rejected.append((t,'open gap'));continue
            old=weights.get(t,0.);wanted=targets[t]
            # A maximum across groups is nonlinear: interpolating its change
            # can reject a feasible addition to a different, smaller group.
            # Bound the added dollars directly against each relevant capacity.
            loss,_,gross=self.metrics(weights)
            stop,gap,group=self.exposures[t]
            group_weight=sum(w for name,w in weights.items()
                             if self.exposures[name][2]==group)
            increase=wanted-old
            fraction=1.
            for used,slope,limit in ((loss,increase*max(stop,gap),self.max_loss),
                                     (group_weight,increase,self.max_group_weight),
                                     (gross,increase,self.max_gross)):
                if slope > 0:
                    fraction=min(fraction,max(0.,(limit-used)/slope))
            weights[t]=old+(wanted-old)*fraction
            targets[t]=weights[t]
            if fraction < 1: rejected.append((t,'aggregate risk'))
        return rejected
