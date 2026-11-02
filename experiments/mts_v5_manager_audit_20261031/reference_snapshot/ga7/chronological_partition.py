"""Fixed discovery/forward partition; no breeding on forward calendar dates."""
from ga7.independence import unique_training_epochs

DISCOVERY_END_EXCLUSIVE='2019-01-01'

def partition(windows, cutoff=DISCOVERY_END_EXCLUSIVE):
    if not windows:raise ValueError('No chronological windows')
    training=tuple((a,min(b,cutoff)) for a,b in unique_training_epochs(windows) if a<cutoff)
    forward=tuple(w for w in windows if w['test_start']>=cutoff)
    if not training or not forward:raise ValueError('Missing discovery or forward period')
    if any(a>=b or b>cutoff for a,b in training):raise ValueError('Training crosses cutoff')
    if any(w['test_start']<cutoff for w in forward):raise ValueError('Forward crosses cutoff')
    return training,forward
