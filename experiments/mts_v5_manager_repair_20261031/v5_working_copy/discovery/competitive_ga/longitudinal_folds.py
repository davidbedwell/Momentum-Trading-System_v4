from dataclasses import dataclass

@dataclass(frozen=True)
class Fold:
    number: int
    train_start: int
    train_end: int
    evaluation_year: int

def expanding_folds(first_year=2017):
    return tuple(Fold(i,first_year,first_year+i-1,first_year+i) for i in range(1,5))

def validate_folds(folds):
    folds=tuple(folds)
    if len(folds)!=4:raise ValueError('four folds required')
    for i,f in enumerate(folds):
        if f.number!=i+1 or f.train_end>=f.evaluation_year:raise ValueError('lookahead')
        if i and (f.train_start!=folds[0].train_start or f.train_end!=folds[i-1].evaluation_year or f.evaluation_year!=folds[i-1].evaluation_year+1):raise ValueError('nonchronological')
    return True
