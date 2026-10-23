"""Synthetic-testable frozen A/B/C -> DEFENSIVE -> R1 -> NORMAL transition controller.
Input flags must be separately certified causal detections; this controller does not derive market indicators.
Never use protected heldout datasets for calibration or validation.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    date: str
    defensive: bool
    entered_defensive: bool
    exited_defensive: bool
    source: str

def build_state_tape(rows):
    """rows chronological: dict(date,A,B,C,R1_evidence); boolean flags are declarations at session close.
    R1 evidence must be an already-qualified three-consecutive-session declaration, not raw evidence.
    A/B/C take priority over R1 when simultaneous. No same-session defensive roundtrip.
    """
    out=[]; defensive=False;last=None
    for row in rows:
        dt=row['date']
        if last is not None and not dt>last:raise ValueError('Dates must be strictly increasing')
        last=dt
        for k in ('A','B','B1','C','R1_evidence'):
            if k not in row or type(row[k]) is not bool:raise ValueError('Missing or invalid '+k)
        triggered=tuple(k for k in ('A','B','B1','C') if row[k])
        entered=False;exited=False
        if triggered:
            if not defensive:entered=True
            defensive=True
        elif defensive and row['R1_evidence']:
            defensive=False;exited=True
        out.append(State(dt,defensive,entered,exited,'+'.join(triggered)))
    return out

def defensive_tape(rows):
    return {s.date:s.defensive for s in build_state_tape(rows)}

def qualify_evidence(rows):
    """Consecutive-session qualification of precomputed, causal raw Boolean conditions.
    A: five, B/C: three, R1: three. Does not calculate indicator percentiles.
    """
    runs={k:0 for k in ('A','B','B1','C','R1_evidence')}
    required={'A':5,'B':3,'B1':1,'C':3,'R1_evidence':3}
    out=[];last=None
    for row in rows:
        dt=row['date']
        if last is not None and not dt>last:raise ValueError('Dates must be strictly increasing')
        last=dt
        result={'date':dt}
        for k in runs:
            if k not in row or type(row[k]) is not bool:raise ValueError('Missing or invalid '+k)
            runs[k]=runs[k]+1 if row[k] else 0
            result[k]=runs[k]>=required[k]
        out.append(result)
    return out

def qualify_statefully(rows):
    """Qualify crash triggers globally, but count R1 only during an existing Defensive spell.
    No R1 streak from NORMAL may be carried into DEFENSIVE; crash wins ties.
    """
    runs={'A':0,'B':0,'B1':0,'C':0};recovery=0;defensive=False;out=[];last=None
    for row in rows:
        dt=row['date']
        if last is not None and dt<=last:raise ValueError('Dates must be strictly increasing')
        last=dt
        for k in ('A','B','B1','C','R1_evidence'):
            if k not in row or type(row[k]) is not bool:raise ValueError('Missing or invalid '+k)
        for k in runs:runs[k]=runs[k]+1 if row[k] else 0
        active=[k for k,n in [('A',5),('B',3),('B1',1),('C',3)] if runs[k]>=n]
        entered=False;exited=False
        if active:
            entered=not defensive;defensive=True;recovery=0
        elif defensive:
            recovery=recovery+1 if row['R1_evidence'] else 0
            if recovery>=3:exited=True;defensive=False;recovery=0
        else:recovery=0
        out.append(State(dt,defensive,entered,exited,'+'.join(active)))
    return out
