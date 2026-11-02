from full_market_matcher import match_all
from dataclasses import dataclass
@dataclass
class C:
    chromosome_id:str
library=[C(str(i)) for i in range(100)]
stocks={str(i):{"feature":i} for i in range(500)}
matches,counts=match_all("2026-10-27",stocks,library,
    lambda c,r,t:True,
    lambda c,r,h,t:("ENTER",.05) if c.chromosome_id=="99" else ("PASS",0))
assert counts["stocks_read"]==500,counts
assert counts["native_evaluations"]==50000,counts
assert len(matches)==500 and all(x.chromosome_id=="99" for x in matches)
print("PASS",counts)
