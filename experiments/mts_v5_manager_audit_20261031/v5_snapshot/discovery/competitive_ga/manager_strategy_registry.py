"""Manager research strategy registry. No family silently omitted.
Availability means adapter is validated, not that the family is profitable.
"""
from dataclasses import dataclass

FAMILIES=('GA4','HORIZONS','GA6','GA7')

@dataclass(frozen=True)
class AdapterStatus:
    family:str
    adapter:str
    available:bool
    reason:str

def readiness():
    return (
      AdapterStatus('GA4','original feature factory',False,'native chromosome proposal and held-state bridge not connected'),
      AdapterStatus('HORIZONS','horizons_signed_decisions',False,'1000-genome weight parity and 28-feature formula parity tested; external publication-time/PIT certification and full execution parity/short accounting remain blocked; next-open long-only ledger is research-only'),
      AdapterStatus('GA6','native_position_decision_adapter',True,'research-only native action pilot; no parity certification'),
      AdapterStatus('GA7','ga7_proposal_adapter',False,'authentic producer and synthetic-feature bridge not connected'),
    )

def require_all(adapters=None):
    statuses=readiness() if adapters is None else tuple(adapters)
    names={s.family for s in statuses}
    if names!=set(FAMILIES) or len(statuses)!=len(FAMILIES):raise ValueError('incomplete family registry')
    unavailable=[s.family for s in statuses if not s.available]
    if unavailable:raise RuntimeError('full manager experiment blocked: '+', '.join(unavailable))
    return True
