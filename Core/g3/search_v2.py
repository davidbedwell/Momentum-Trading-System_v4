from __future__ import annotations
import random
from Core.g3.starter import Specialist

def recombine(a:Specialist,b:Specialist,rng:random.Random)->Specialist:
    """Recombine independently useful structural and lifecycle genes without inventing new values."""
    return Specialist(
        gate=a.gate if rng.random()<.5 else b.gate,
        signal=a.signal if rng.random()<.5 else b.signal,
        side=a.side if rng.random()<.5 else b.side,
        take_profit=a.take_profit if rng.random()<.5 else b.take_profit,
        stop_loss=a.stop_loss if rng.random()<.5 else b.stop_loss,
        max_horizon=a.max_horizon if rng.random()<.5 else b.max_horizon,
        add_at=a.add_at if rng.random()<.5 else b.add_at,
        reduce_at=a.reduce_at if rng.random()<.5 else b.reduce_at,
    )
