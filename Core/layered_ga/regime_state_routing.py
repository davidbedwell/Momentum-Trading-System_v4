"""Controller-state routing for Normal entries; independent of calendar exclusions.

States are the controller's causal end-of-session declarations. At a close
where DEFENSIVE is declared, the next open is reserved for liquidation.
A NORMAL declaration by R-1 permits new Normal orders for the next open.
"""
import numpy as np

def normal_entry_eligibility(decision_dates, controller_dates, controller_states):
    dates=np.asarray(decision_dates,dtype="datetime64[D]")
    tape=np.asarray(controller_dates,dtype="datetime64[D]")
    states=np.asarray(controller_states,dtype=str)
    if len(tape)!=len(states) or len(tape)==0:raise ValueError("empty or misaligned controller tape")
    if len(np.unique(tape))!=len(tape) or np.any(tape[1:]<=tape[:-1]):
        raise ValueError("controller dates must be unique and strictly ascending")
    if not np.all(np.isin(states,["NORMAL","DEFENSIVE"])):
        raise ValueError("invalid controller state")
    idx=np.searchsorted(tape,dates,side="right")-1
    allowed=np.zeros(len(dates),dtype=bool)
    valid=idx>=0
    allowed[valid]=states[idx[valid]]=="NORMAL"
    return allowed

def defensive_transition_closes(controller_dates,controller_states):
    tape=np.asarray(controller_dates,dtype="datetime64[D]")
    states=np.asarray(controller_states,dtype=str)
    if len(tape)!=len(states) or len(tape)==0:raise ValueError("invalid tape")
    if len(np.unique(tape))!=len(tape) or np.any(tape[1:]<=tape[:-1]):raise ValueError("unsorted tape")
    if not np.all(np.isin(states,["NORMAL","DEFENSIVE"])):raise ValueError("invalid state")
    prev=np.concatenate((np.array(["UNKNOWN"]),states[:-1]))
    return tape[(states=="DEFENSIVE")&(prev!="DEFENSIVE")]