"""Paired planted-minus-null calibration response; descriptive, not selection-adjusted."""
from math import isfinite

WINDOWS = {'FAST': (3, 7), 'MEDIUM': (10, 20), 'SLOW': (25, 45)}

def paired_recovery(side, shape, effect, *, ratio=.95, atol=1e-9):
    """Find contiguous planted response within the predeclared target window.

    Require at least two adjacent points with >=95% of the maximum positive
    paired uplift, and positive absolute LCB at those same horizons. The
    profile/target window is held by the auditor, never by the GA evaluator.
    """
    lo, hi = WINDOWS[shape]
    points = {int(p['horizon']): p for p in side['points']}
    delta = {int(p['horizon']): p for p in side['paired_delta']}
    if set(points) != set(range(1, 64)) or set(delta) != set(range(1, 64)):
        return {'pass': False, 'reason': 'incomplete or duplicate horizon path'}
    if effect == 0:
        null_ok = all(isfinite(float(delta[h]['delta_ev_net'])) and
                      abs(float(delta[h]['delta_ev_net'])) <= atol for h in range(1,64))
        return {'pass': null_ok, 'null_rejected': null_ok}
    peak = max(float(delta[h]['delta_ev_net']) for h in range(1,64))
    if not isfinite(peak) or peak <= atol:
        return {'pass': False, 'reason': 'no positive paired uplift'}
    selected = [h for h in range(lo,hi+1)
                if isfinite(float(delta[h]['delta_ev_net']))
                and float(delta[h]['delta_ev_net']) >= ratio*peak-atol
                and isfinite(float(points[h]['lcb95']))
                and float(points[h]['lcb95']) > 0]
    adjacent = any(b==a+1 for a,b in zip(selected,selected[1:]))
    return {'pass': adjacent, 'peak_paired_uplift': peak,
            'positive_lcb_stable_target_horizons': selected,
            'target_window': [lo,hi]}
