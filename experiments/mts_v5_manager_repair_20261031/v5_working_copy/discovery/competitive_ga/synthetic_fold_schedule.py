from dataclasses import dataclass

@dataclass(frozen=True)
class SessionFold:
    scenario: int
    number: int
    train_stop: int
    test_start: int
    test_stop: int

def make_folds(scenario, dates):
    dates=tuple(dates)
    if scenario not in range(1,6) or len(dates)<10:
        raise ValueError('invalid scenario')
    if dates!=tuple(sorted(set(dates))):
        raise ValueError('dates not strictly increasing')
    boundaries=[len(dates)*i//5 for i in range(6)]
    return tuple(SessionFold(scenario,i,boundaries[i],boundaries[i],boundaries[i+1]) for i in range(1,5))
