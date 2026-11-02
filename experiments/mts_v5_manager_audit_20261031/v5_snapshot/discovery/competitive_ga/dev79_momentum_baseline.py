"""DEV79 simple causal momentum baseline, common execution; exploratory PIT caveats."""
import sys,json,math
from pathlib import Path
from collections import Counter
P=Path('/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518')
sys.path.insert(0,str(P))
source=(P/'ga6_ga7_common_execution_dev79_fullperiod_two_genome_v1_20261028.py').read_text()
# Reuse exact historical panel construction and shared execution, not prior GA results.
exec(compile(source.split('\nresults={}')[0].replace('R=Path(__file__).parent','R=Path("/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518")'),str(P/'ga6_ga7_common_execution_dev79_fullperiod_two_genome_v1_20261028.py'),'exec'))
from ga6_ga7_common_execution_reference_v1 import Order
from dataclasses import replace

def baseline(hold=10,threshold=0.):
    histories={};entry={};orders=[]
    def decide(i,day,holdings):
        for t,b in day.bars.items():histories.setdefault(t,[]).append(b.close)
        pending=[]
        for t,p in holdings.items():
            if i-p.entered>=hold:pending.append(Order(i,t,'EXIT'))
        if not day.defensive:
            for t,b in day.bars.items():
                if t in holdings or not b.eligible or day.date in blocked.get(t,set()):continue
                h=histories[t]
                if len(h)<21:continue
                mom=h[-1]/h[-21]-1
                if mom<=threshold:continue
                pending.append(Order(i,t,'ENTER',weight=.1,stop_pct=.02,earnings_clear=True,priority=mom))
        return pending
    cfg=Config(fee_bps=10,symbol_cap=.1,per_position_risk_cap=.02,aggregate_risk_cap=.1,
               sector_position_cap=3,max_positions=79,cash_yield=0.,price_basis='split_adjusted')
    r=run(days,config=cfg,decision_fn=decide)
    peak=100000.;dd=0.
    for v in r.nav:peak=max(peak,v);dd=min(dd,v/peak-1)
    years=(pd.Timestamp(days[-1].date)-pd.Timestamp(days[0].date)).days/365.25
    return {'cagr':(r.nav[-1]/100000)**(1/years)-1,'mdd':dd,'calmar':((r.nav[-1]/100000)**(1/years)-1)/abs(dd) if dd else None,
            'final_nav':r.nav[-1],'completed_trades':len(r.trades),'fills':dict(Counter(e['action'] for e in r.events)),
            'rejections':dict(Counter(x[2] for x in r.rejected))}
result={'scope':'DEV79_2009_2018_EXPLORATORY_NONCERTIFIED','same_panel':True,'same_execution':True,
        'momentum_20_positive_hold10':baseline(10,0.),'momentum_20_positive_hold20':baseline(20,0.),
        'previous_selected_GA6_GA7':json.loads((P/'ga6_ga7_common_execution_dev79_fullperiod_two_genome_v1_20261028.json').read_text())['results']}
output=P/'dev79_momentum_vs_native_baseline_20261028.json'
output.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
