"""Retention-aware policy promotion; measured portfolio fitness only.

Development-set promotion is not independent validation.
"""
from dataclasses import dataclass, asdict
import json
from pathlib import Path

@dataclass(frozen=True)
class Score:
    net_return: float
    max_drawdown: float
    observations: int

    def __post_init__(self):
        if self.observations < 2 or not 0 <= self.max_drawdown <= 1:
            raise ValueError("invalid replay score")

class RetentionGate:
    def __init__(self, max_regression=0.02, max_drawdown_increase=0.02):
        self.max_regression=max_regression
        self.max_drawdown_increase=max_drawdown_increase
        self.history=[]

    def evaluate(self, iteration, incumbent, challenger, previously_seen, novel):
        """All scores from independent causal full-portfolio replays.
        previously_seen: mapping market -> (incumbent score, challenger score).
        novel: (incumbent score, challenger score) on a new development market.
        """
        if not previously_seen:
            raise ValueError("retention tests required")
        if novel is None:
            raise ValueError("new market transfer test required")
        regressions={}
        for market,(old,new) in previously_seen.items():
            if new.net_return < old.net_return-self.max_regression or new.max_drawdown > old.max_drawdown+self.max_drawdown_increase:
                regressions[market]={"return_delta":new.net_return-old.net_return,"drawdown_delta":new.max_drawdown-old.max_drawdown}
        old,new=novel
        transfer=(new.net_return>old.net_return and new.max_drawdown<=old.max_drawdown+self.max_drawdown_increase)
        accepted=bool(transfer and not regressions)
        event={"iteration":iteration,"incumbent":incumbent,"challenger":challenger,"accepted":accepted,"transfer_improved":transfer,"retention_failures":regressions,
               "novel_return_delta":new.net_return-old.net_return,"novel_drawdown_delta":new.max_drawdown-old.max_drawdown}
        self.history.append(event)
        return event

    def save(self,path):
        dest=Path(path);dest.parent.mkdir(parents=True,exist_ok=True)
        tmp=dest.with_suffix(dest.suffix+".tmp")
        tmp.write_text("\n".join(json.dumps(x,sort_keys=True) for x in self.history)+"\n")
        tmp.replace(dest)
