"""Per-trade executable checkpoint exit vs frozen horizon hold counterfactual.
Not a portfolio simulator: overlap, sizing and capital constraints still required.
"""
import numpy as np
def replay_trade_counterfactual(terminal_net,checkpoint_net,exit_signal,available):
 terminal=np.asarray(terminal_net,float);checkpoint=np.asarray(checkpoint_net,float)
 signal=np.asarray(exit_signal,bool);valid=np.asarray(available,bool)
 if not (terminal.shape==checkpoint.shape==signal.shape==valid.shape):raise ValueError('Shape mismatch')
 if not np.isfinite(terminal[valid]).all() or not np.isfinite(checkpoint[valid]).all():raise ValueError('Nonfinite valid returns')
 # At a checkpoint, net exit is executable-open mark less contemporaneous roundtrip costs.
 # No future information is used to choose exit_signal.
 chosen=np.where(signal,checkpoint,terminal)
 return {'eligible':int(valid.sum()),'exited':int((signal&valid).sum()),
         'hold_net_sum':float(terminal[valid].sum()),'policy_net_sum':float(chosen[valid].sum()),
         'incremental_net_sum':float((chosen[valid]-terminal[valid]).sum()),
         'hold_net_mean':float(terminal[valid].mean()) if valid.any() else None,
         'policy_net_mean':float(chosen[valid].mean()) if valid.any() else None,
         'status':'TRADE_COUNTERFACTUAL_ONLY_NO_PORTFOLIO_CERTIFICATION'}
