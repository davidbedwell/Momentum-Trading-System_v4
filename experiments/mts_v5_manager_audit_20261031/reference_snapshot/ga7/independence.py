"""Reject overlapping forward evaluation periods and report dependent training windows."""

def assert_nonoverlapping_forward(windows):
    ordered=sorted(windows,key=lambda x:x['test_start'])
    for w in ordered:
        if w['train_end_exclusive']>w['test_start']:
            raise ValueError('Training crosses forward start')
        if w['test_start']>=w['test_end_exclusive']:
            raise ValueError('Invalid forward window')
    for a,b in zip(ordered,ordered[1:]):
        if a['test_end_exclusive']>b['test_start']:
            raise ValueError('Overlapping forward windows')
    return True

def unique_training_epochs(windows):
    """Nonoverlapping annual epochs; avoid double-counting expanding training history."""
    starts=sorted(set(w['train_end_exclusive'] for w in windows))
    first=min(w['train_start'] for w in windows)
    return tuple((start,end) for start,end in zip((first,*starts[:-1]),starts) if start<end)
