"""Niche-first adaptive screening with weekly exhaustive shadow audits.

All qualifying signals are compared on a shared opportunity scale downstream.
This module is routing only; it does not claim replay certification.
"""
from dataclasses import dataclass
from .hierarchical_search import screen_all

@dataclass(frozen=True)
class SearchPolicy:
 minimum_distinct_opportunities:int=5
 shadow_every_sessions:int=5
 def __post_init__(self):
  if self.minimum_distinct_opportunities<1 or self.shadow_every_sessions<1:
   raise ValueError('invalid search policy')

def search_session(stock_rows,candidates,niche_at_close,feature_gate,native_decision,asof,session_index,policy=SearchPolicy()):
 """Return adaptive matches, full-shadow matches on audit sessions, and counts.

 Full shadow always evaluates all eligible chromosomes on audit days. Adaptive
 expands when fewer than threshold distinct stock opportunities exist. A full
 shadow audit must not be interpreted as a fill or as hindsight selection.
 """
 full_audit=(session_index%policy.shadow_every_sessions==0)
 primary_bank=[c for c in candidates if c.family.upper() not in ('GA4','HORIZONS') and c.niche is not None and c.niche.upper() not in ('NO-NICHE','NO_NICHE')]
 primary,primary_counts=screen_all(stock_rows,primary_bank,niche_at_close,feature_gate,native_decision,asof)
 distinct=len({m[1] for m in primary if m[3] in ('ENTER','ADD')})
 expanded=distinct<policy.minimum_distinct_opportunities
 all_matches=[];all_counts={}
 if expanded or full_audit:
  all_matches,all_counts=screen_all(stock_rows,candidates,niche_at_close,feature_gate,native_decision,asof)
 active=all_matches if expanded else primary
 return {'active':active,'shadow':all_matches if full_audit else [],'counts':{'primary_distinct_stocks':distinct,'expanded':expanded,'full_shadow_audit':full_audit,'active_matches':len(active),'shadow_matches':len(all_matches) if full_audit else 0,'primary_scan_counts':primary_counts,'full_scan_counts':all_counts}}
