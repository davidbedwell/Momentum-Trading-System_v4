"""Bounded original-native journal plus descriptive NAV accounting identity.

The additive components describe two endogenous paths; they do not assign causal
PnL to priority, sizing, eligibility or policy. No fixed tape is a policy oracle.
"""
import json
from collections import Counter
from pathlib import Path
from .first_year_manifest import digest
from .phase5_diagnostics import training_panels
from .ga7_native_journal import observe
from .ga7_native_kernels import HASHES


def components(panels, holdings, fees):
    """Independent mark identity from shares/prices, never cash engine output."""
    prior = {}; rows = []; previous_bars = None
    for i,(date,bars,_) in enumerate(panels):
        overnight=sum(q*(bars[t]['open']-previous_bars[t]['close']) for t,q in prior.items()) if i else 0.
        intraday=sum(q*(bars[t]['close']-bars[t]['open']) for t,q in holdings[i].items())
        rows.append(dict(date=date,overnight=overnight,intraday=intraday,fees=fees[i],
                         nav_change=overnight+intraday-fees[i]))
        prior=holdings[i]; previous_bars=bars
    return rows


def run():
    prior_path=Path('PHASE7_DIAGNOSTICS.json')
    if digest(prior_path) != '911d67d672e626b6d1c7633b8055a9403c2256391e79ac1a6ef04562bf5705d2':
        raise ValueError('Phase7 evidence identity changed')
    prior=json.loads(prior_path.read_text())
    for path,expected in prior['source_hashes'].items():
        if digest(Path(path)) != expected:
            raise ValueError('changed prior diagnostic source: '+path)
    if prior['native_source_hash'] != HASHES['request_replay.py']:
        raise ValueError('prior native implementation mismatch')
    g,_,_,panels,_=training_panels()
    if len(panels)!=32 or panels[0][0]!='2022-11-17' or panels[-1][0]!='2022-12-30' or any(len(b)!=500 for _,b,_ in panels):
        raise ValueError('exact authorized 32-session panel required')
    if any(b.get('dividend',0) or b.get('split',1)!=1 for _,bars,_ in panels for b in bars.values()):
        raise ValueError('mark identity only supports no-action diagnostic convention')
    from ga7.request_replay import replay_requests
    from ga7.runner import passes
    result,ledger,orders,daily=observe(replay_requests,g,panels,passes)
    if [x['date'] for x in daily] != [e['date'] for e in prior['events']]:
        raise ValueError('prior calendar differs')
    max_state=0.; max_fill=0.
    for i,(d,e) in enumerate(zip(daily,prior['events'])):
        n=d['state']; old=e['native']
        if {t:p['shares'] for t,p in n['positions'].items()} != {t:p['shares'] for t,p in old['positions'].items()}:
            raise ArithmeticError('prior native inventory differs')
        max_state=max(max_state,abs(n['cash']-old['cash']),abs(sum(a for _,a in n['receivables'])-old['receivable']),abs(d['marked_nav']-e['native_nav']))
        # Compare independently reconstructed Phase 7 fills to ACTUAL observed
        # native inventory deltas. They are accounting evidence, never an oracle.
        actual=[o for o in orders if o['session']==i and o['outcome']=='FILL']
        expected=e['native_fills']
        if len(actual)!=len(expected):
            raise ArithmeticError('prior fill count differs')
        for a,b in zip(actual,expected):
            if [a['ticker'],a['side'],a['filled_shares']] != b[:3]:
                raise ArithmeticError('prior ordered fill differs')
            max_fill=max(max_fill,abs(a['price']-b[3]),abs(a['fee']-b[4]))
    if max(max_state,max_fill)>1e-7:
        raise ArithmeticError('native prior evidence not reproduced')
    native_hold=[{t:p['shares'] for t,p in d['state']['positions'].items()} for d in daily]
    shadow_hold=[{t:p['shares'] for t,p in e['shadow_after_open']['positions'].items()} for e in prior['events']]
    nf=[sum(o['fee'] for o in orders if o['session']==i) for i in range(32)]
    sf=[sum(f[4] for f in e['shadow_fills']) for e in prior['events']]
    nc=components(panels,native_hold,nf); sc=components(panels,shadow_hold,sf)
    residual=0.; nn=sn=100000.
    for n,s,d,e in zip(nc,sc,daily,prior['events']):
        nn+=n['nav_change']; sn+=s['nav_change']
        residual=max(residual,abs(nn-d['marked_nav']),abs(sn-e['shadow_nav']))
    if residual>1e-7:
        raise ArithmeticError('independent marking identity failed')
    differences={k:sum(s[k]-n[k] for n,s in zip(nc,sc)) for k in ('overnight','intraday','fees')}
    gap=daily[-1]['marked_nav']*-1+prior['events'][-1]['shadow_nav']
    nsettled=sum(o['before']['cash']-(daily[o['session']-1]['state']['cash']) for j,o in enumerate(orders) if j==0 or orders[j-1]['session']!=o['session'])
    # Shadow settlement reconstructed from net sales minus outstanding T+1.
    ssettled=sum(q*p-fee for e in prior['events'] for _,side,q,p,fee in e['shadow_fills'] if side=='SELL')-prior['events'][-1]['shadow_after_open']['receivable']
    compact=[]
    for o in orders:
        compact.append({k:v for k,v in o.items() if k not in ('before','after')} if o['outcome']!='FILL' else o)
    return dict(status='RESEARCH_ONLY_NATIVE_PARITY_BLOCKED',proof_opened=False,
        first=panels[0][0],last=panels[-1][0],sessions=32,tickers=500,
        native_sources=HASHES,source_hashes=prior['source_hashes'],prior_phase7_sha256=digest(prior_path),
        native_result=result,native_requests=len(ledger.requests),
        native_ordered_observations=compact,native_daily=daily,
        actual_native_fills=sum(o['outcome']=='FILL' for o in orders),
        native_no_fill_actions=dict(Counter(o['action'] for o in orders if o['outcome']=='NO_FILL')),
        prior_native_max_state_residual=max_state,prior_reconstructed_max_fill_residual=max_fill,
        mark_identity_max_residual=residual,marked_gap=gap,
        descriptive_components_shadow_minus_native=differences,
        identity='gap = overnight difference + intraday difference - fee difference; descriptive path accounting, NOT causal policy attribution',
        native_fees=sum(nf),shadow_fees=sum(sf),native_settled=nsettled,shadow_settled=ssettled,
        settlement_nav_contribution=0.,native_components=nc,shadow_components=sc,
        first_native_fill=next(o for o in orders if o['outcome']=='FILL'),
        first_batch=dict(native_fills=sum(o['session']==1 and o['outcome']=='FILL' for o in orders),
                         shadow_fills=len(prior['events'][1]['shadow_fills']),
                         initial_native_enter_candidates=sum(p['session']==0 and p['action']=='ENTER' for p in ledger.requests),
                         native_first_choice=next(o['ticker'] for o in orders if o['session']==1 and o['action']=='ENTER'),
                         shadow_first_choice=prior['events'][1]['shadow_fills'][0][0]),
        first_shadow_fill=next(f for e in prior['events'] for f in e['shadow_fills']),
        blocked_measurements=['separate causal dollar effects of first-choice/priority, sizing/capacity and endogenous held decisions: interacting paths; no independently governed common policy',
            'certified event/pay-date/settlement, eligibility/earnings, niche/training-lineage, risk/defense/gap/group controls: unavailable source provenance',
            'native external-share/opening-state parity: no native seam; extracted kernels omit native policy and outcome reporting'],
        conventions='Existing adjusted-price/no-action diagnostic defaults and all-true warmup eligibility only; not market-control certification. Shadow journal is retained Phase7 evidence, not a new independent policy oracle.')


if __name__=='__main__':
    result=run()
    Path('PHASE9_DIAGNOSTICS.json').write_text(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('native_ordered_observations','native_daily','native_components','shadow_components','source_hashes','native_result','first_native_fill')},indent=2))
