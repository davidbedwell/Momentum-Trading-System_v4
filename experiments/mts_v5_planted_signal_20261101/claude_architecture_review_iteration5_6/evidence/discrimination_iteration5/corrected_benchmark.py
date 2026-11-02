"""Post-freeze engineering correction, evaluated descriptively on four already viewed tapes.
No predictions or signal ranking are accepted. Each entry uses equal notional across 24 names.
"""
import hashlib,json,time
from pathlib import Path
import experiment as e
O=Path(__file__).resolve().parent

def replay_equal(prices):
    cash=100000.;receivable=0.;held=[];peak=100000.;mdd=0.;costs=0.;trades=[];daily=[]
    for i in range(e.START,e.END):
        cash+=receivable;receivable=0.
        for t in held:
            proceeds=t['shares']*prices[i+1][t['j']]*(1-e.COST/2);receivable+=proceeds;costs+=t['shares']*prices[i+1][t['j']]*e.COST/2
            t.update(exit_index=i+1,net=proceeds/t['debit']-1);trades.append(t)
        held=[];opening=cash+receivable
        debit=min(cash/24,opening/24)
        for j in range(24):
            if debit<=1e-8:continue
            shares=debit/(prices[i+1][j]*(1+e.COST/2));risk=shares*prices[i+1][j]/opening*([.03,.06,.12,.24][j%4]+e.COST)
            assert risk<=.02
            held.append(dict(signal=i,j=j,shares=shares,debit=debit,entry_index=i+1,modeled_risk=risk));cash-=debit;costs+=shares*prices[i+1][j]*e.COST/2
        assert cash>=-1e-7
        nav=cash+receivable+sum(t['shares']*prices[i+1][t['j']] for t in held);peak=max(peak,nav);mdd=max(mdd,1-nav/peak);daily.append(dict(index=i,nav=nav,cash=max(0,cash)))
    for t in held:
        proceeds=t['shares']*prices[e.END+1][t['j']]*(1-e.COST/2);cash+=proceeds;costs+=t['shares']*prices[e.END+1][t['j']]*e.COST/2;t.update(exit_index=e.END+1,net=proceeds/t['debit']-1);trades.append(t)
    nav=cash+receivable;peak=max(peak,nav);mdd=max(mdd,1-nav/peak)
    # Integrated invariant checks do not execute additional portfolios.
    bydate={}
    for t in trades:bydate.setdefault(t['signal'],[]).append(t)
    assert all(len(ts)==24 and max(t['debit'] for t in ts)==min(t['debit'] for t in ts) for ts in bydate.values())
    return dict(total_return=nav/100000-1,cagr=(nav/100000)**2-1,mdd=mdd,costs=costs,final_nav=nav,trades=len(trades)),trades,daily

if __name__=='__main__':
    if (O/'corrected_benchmark_results.json').exists():raise SystemExit('No rerun permitted')
    start=time.monotonic();commit=dict(source_sha256=e.sha(__file__),phase='post-freeze correction on already viewed learnable tapes',reason='Original benchmark forecast-ranked cash-limited purchases; invalid independent control.',additional_replays=4)
    (O/'benchmark_correction_commitment.json').write_text(json.dumps(commit,indent=2))
    rows=[]
    import gzip
    with gzip.open(O/'corrected_benchmark_replays.jsonl.gz','wt') as f:
        for seed in json.loads((O/'seeds.json').read_text()):
            p,_,_=e.generate(seed,'learnable');metric,trades,daily=replay_equal(p);rows.append(dict(seed=seed,scenario='learnable',variant='corrected_equal_universe',**metric));f.write(json.dumps(dict(seed=seed,trades=trades,daily=daily))+'\n')
    (O/'corrected_benchmark_results.json').write_text(json.dumps(dict(runs=rows,elapsed_seconds=time.monotonic()-start,**commit),indent=2));e.writecsv('corrected_benchmark_metrics.csv',rows)
