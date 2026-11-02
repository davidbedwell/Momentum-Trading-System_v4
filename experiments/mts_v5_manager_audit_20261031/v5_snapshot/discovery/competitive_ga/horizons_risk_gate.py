"""Pre-execution long-only portfolio risk gates; research-only.
Reject rather than silently shrink exposure when mandatory inputs are absent.
"""
import math
from .horizons_next_open_execution import equity

def validate(book,decisions,prices,sector_by_ticker=None,max_sector=.30,max_stock=.10):
 if not 0<max_stock<=.10 or not 0<max_sector<=1:raise ValueError('invalid risk limits')
 if sector_by_ticker is None:raise ValueError('sector map required')
 if not decisions: return True
 total=equity(book,prices)
 if total<=0:raise ValueError('nonpositive equity')
 targets={t:float(q)*float(prices[t])/total for t,q in book.shares.items() if q>0}
 for t,proposal in decisions.items():
  w=float(proposal['target_weight'])
  if not math.isfinite(w) or w<0 or w>max_stock+1e-12:raise ValueError('symbol exposure cap')
  targets[t]=w
 sectors={}
 for t,w in targets.items():
  if w<=0:continue
  if t not in sector_by_ticker:raise ValueError('sector classification missing: '+t)
  sector=sector_by_ticker[t]
  sectors[sector]=sectors.get(sector,0.)+w
 if any(w>max_sector+1e-12 for w in sectors.values()):raise ValueError('sector concentration cap')
 if sum(targets.values())>1+1e-12:raise ValueError('gross exposure exceeds equity')
 return True
