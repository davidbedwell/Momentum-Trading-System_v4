"""Equivalent fast path for GA5 signal decisions. Research-only."""
from math import isfinite
from ga5_chromosome_decisions import PositionState

def evaluate(genome, features, position, price):
 if not isfinite(price) or price<=0:raise ValueError("Invalid price")
 if position.shares:
  stop=price<=position.entry_price*(1-genome.stop_loss)
  trail=price<=position.peak_price*(1-genome.trailing_stop)
  timeout=genome.time_exit_enabled and position.sessions_held>=genome.max_hold_sessions
  if stop or trail or timeout or features[genome.exit_feature]<genome.exit_threshold or features[genome.hold_feature]<genome.hold_threshold:
   return "EXIT",0.
  if features[genome.replace_feature]<genome.replace_threshold:return "REPLACE_CANDIDATE",0.
  strength=features[genome.sizing_feature]
  if strength>=genome.scale_in_threshold:return "SCALE_IN",min(genome.max_weight,genome.risk_budget,genome.base_weight*genome.scale_step)
  if strength<=genome.scale_out_threshold:return "SCALE_OUT",genome.scale_step
  return "HOLD",min(genome.max_weight,genome.base_weight)
 if features[genome.regime_feature]<genome.regime_threshold:return "NO_ENTRY",0.
 if features[genome.entry_feature]<genome.entry_threshold:return "NO_ENTRY",0.
 strength=max(0.,min(1.,.5+features[genome.sizing_feature]))
 return "ENTER",min(genome.max_weight,genome.risk_budget,genome.base_weight*(.5+strength))
