"""Research-vs-trading release-time gate for archived stress inputs.
Archived files carry observation dates, not independently verified publication timestamps.
"""
from dataclasses import dataclass
@dataclass(frozen=True)
class StressStatus:
 research_reconstruction:bool
 live_or_pit_certified:bool
 reason:str

def status():
 return StressStatus(True,False,'VIX/VVIX/OFR archive has observation dates but no certified availability timestamps; VIX/VVIX closing values cannot be presumed known before close')

def require_certified(mode):
 if mode not in ('research','trading','pit_validation'):raise ValueError('unknown mode')
 s=status()
 if mode!='research' and not s.live_or_pit_certified:raise RuntimeError(s.reason)
 return True
