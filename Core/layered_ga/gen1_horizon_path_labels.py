"""Outcome-only, genome-specific original-horizon path labels. Never predictors."""
import numpy as np
ORIGINAL_HORIZONS=(1,2,3,5,7,10,15,20,63)
CHECKPOINTS=(1,2,3,5,7,10,15,20)
def valid_checkpoints(horizon):
    if horizon not in ORIGINAL_HORIZONS: raise ValueError('Not an original Gen1 horizon')
    return tuple(c for c in CHECKPOINTS if c<horizon)
def labels(endpoint,costs,side,horizon,checkpoint,barrier=.02):
    """T+1 open entry; T+1+h open exit. Barrier in entry-notional units.
    First passage uses future executable opens strictly after checkpoint.
    Event=+1 recovery first, -1 adverse first, 0 censored, -2 unavailable.
    """
    if horizon not in ORIGINAL_HORIZONS or checkpoint not in valid_checkpoints(horizon):
        raise ValueError('Checkpoint must precede original terminal horizon')
    if side not in ('LONG','SHORT'):raise ValueError('Invalid side')
    if not (np.isfinite(barrier) and barrier>0):raise ValueError('Invalid barrier')
    e=np.asarray(endpoint);c=np.asarray(costs)
    if e.ndim!=2 or c.shape!=e.shape or e.shape[1]<horizon:raise ValueError('Array shape')
    s=1 if side=='LONG' else -1
    cp=s*e[:,checkpoint-1]
    terminal=s*e[:,horizon-1]-c[:,horizon-1]
    cpnet=cp-c[:,checkpoint-1]
    # Compare subsequent executable-open paths with checkpoint executable open.
    future=s*(e[:,checkpoint:horizon]-e[:,checkpoint-1,None])
    good=np.isfinite(future)
    recovery=good&(future>=barrier)
    adverse=good&(future<=-barrier)
    up=np.where(recovery.any(axis=1),recovery.argmax(axis=1)+1,999)
    down=np.where(adverse.any(axis=1),adverse.argmax(axis=1)+1,999)
    outcome=np.where(up<down,1,np.where(down<up,-1,0)).astype('int8')
    # Missing any intermediate open is censored as unavailable, not 'no event'.
    available=np.isfinite(cp)&np.isfinite(cpnet)&np.isfinite(terminal)&good.all(axis=1)
    outcome[~available]=-2
    return {'checkpoint_net':cpnet,'terminal_net':terminal,'distressed':available&(cpnet<0),
            'event':outcome,'first_recovery_sessions':np.where(up==999,-1,up),
            'first_adverse_sessions':np.where(down==999,-1,down),'available':available}
