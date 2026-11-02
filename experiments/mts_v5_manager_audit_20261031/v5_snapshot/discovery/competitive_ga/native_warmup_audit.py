"""Audit first 21 sessions of genuine native GA6 replay for shadow warmup.
Native replay uses chromosome-specific position exits (not fixed horizon).
Research audit only: ledger currently lacks immutable per-fill owner provenance.
"""
import json
from discovery.competitive_ga.ga6_native_position_replay import run

def audit():
    result,replay,trace=run(output=False,return_trace=True)
    dates=[x[0] for x in replay.nav]
    if len(dates)<22:raise ValueError("insufficient sessions")
    boundary=dates[20]
    warmup=[x for x in replay.ledger if x[0]<=boundary]
    mature=[x for x in warmup if x[2]=="SELL"]
    return {"warmup_sessions":21,"warmup_through":boundary,
            "native_shadow_fills":len(warmup),
            "native_shadow_sells":len(mature),
            "full_period_native_fills":len(replay.ledger),
            "owner_attribution_ready":False,
            "limitation":"Replay has native exits but no per-fill immutable chromosome provenance. Do not treat sells as calibrated chromosome outcomes."}
if __name__=="__main__":print(json.dumps(audit(),indent=2))
