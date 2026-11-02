"""Matched GA6 holding-duration diagnostic. Research, not training validation."""
import json
from pathlib import Path
from collections import defaultdict
from discovery.competitive_ga.ga6_native_position_replay import run
OUT=Path('/opt/mts/synthetic-market-lab/reports/ga6_hold_duration_attribution_2020.json')
def analyze():
    a,ra,_=run(max_hold=40,output=False,return_trace=True)
    b,rb,_=run(max_hold=None,output=False,return_trace=True)
    # Daily NAV difference and exposure, with identical chronological input.
    differences=[]
    for x,y in zip(ra.nav,rb.nav):
        assert x[0]==y[0]
        da,db=x[1],y[1]
        differences.append({'date':x[0],'nav_delta_forced_minus_unlimited':round(da-db,2),
                            'cash_forced':round(x[2],2),'cash_unlimited':round(y[2],2),
                            'holdings_forced':len(x[3]),'holdings_unlimited':len(y[3])})
    first=next((d for d in differences if abs(d['nav_delta_forced_minus_unlimited'])>.01),None)
    maxdiv=max(differences,key=lambda x:abs(x['nav_delta_forced_minus_unlimited']))
    # Monthly snapshots provide attribution targets without claiming causal identification.
    monthly={}
    for d in differences:monthly[d['date'][:7]]=d
    result={'comparison':'2020 matched native GA6 replay, imposed 40-session exit vs no imposed exit',
            'forced':a,'unlimited':b,'first_nav_divergence':first,
            'largest_absolute_nav_divergence':maxdiv,
            'month_end_snapshots':list(monthly.values()),
            'fill_delta_forced_minus_unlimited':len(ra.ledger)-len(rb.ledger),
            'interpretation_limit':'Portfolio path differences include reinvestment, opportunity displacement, fees and endogenous decisions; NAV delta does not identify causal holding-time effect. In-sample diagnostic only; no GA learning/validation.'}
    OUT.write_text(json.dumps(result,indent=2))
    return {'first_nav_divergence':first,'largest_absolute_nav_divergence':maxdiv,
            'month_end_snapshots':list(monthly.values()),'fill_delta':result['fill_delta_forced_minus_unlimited']}
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
