"""Actual-source diagnostic, NOT a certified four-family manager launch.

No model training date is invented: research actions bypass the authenticated
proposal type and are confined to independent diagnostic books. The shared
bank receives zero eligible proposals while lineage/PIT inputs are unknown.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from types import SimpleNamespace
import numpy as np
import pandas as pd
from .first_year_features import RAW, COLUMNS
from .first_year_manifest import digest
from .first_year_parity import ga6_features, required_ga6
from .archived_genomes import ga6, ga7, ga7_bars
from .funded_shadow import FundedShadow
from .chronological_manager_replay import run
from engines.portfolio_replay.kernel import Bar

GA6_ID='000040b4691c2c84a9bea15a1b3a17a6d489a616480782c5fffddad2d267ea97'
GA7_ID='5633a66d50bdadc95dab'
BANK=Path('/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite')
CHECKPOINT=Path('/opt/mts/ga7-deploy/ga7_unbounded/runs/preflight_16/checkpoint.json')


@dataclass(frozen=True)
class DiagnosticAction:
    decision_date: str
    ticker: str
    family: str
    chromosome_id: str
    action: str
    target_weight: float


def smoke(sessions=32, *, audit_prefix=False):
    if type(sessions) is not int or not 3 <= sessions <= 32:
        raise ValueError('3..32 diagnostic sessions only')
    started, cpu=time.perf_counter(),time.process_time()
    sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign','/opt/mts/ga7-deploy/ga7_unbounded']
    from ga5_feature_adapter import LEGACY
    from ga6.native_position_decision_adapter import native_action
    from ga7.runner import COLUMNS as SEVEN_COLUMNS, passes
    from ga7.request_replay import score_signal, replay_requests
    candidate=ga6(BANK,[GA6_ID])[GA6_ID]
    genomes,checkpoint_hash=ga7(CHECKPOINT,[GA7_ID]);genome=genomes[GA7_ID]
    cache=Path('/tmp/mts_phase3_feature_audit')
    provenance=json.loads((cache/'provenance.json').read_text())
    if any(digest(p)!=h for p,h in provenance['hashes'].items()) or digest(cache/'full.parquet')!=(cache/'full.sha256').read_text():
        raise ValueError('native feature cache provenance changed')
    # Smoke uses training only. Optional action audit reuses the previously
    # open engineering prefix, without forward outcomes or parameter selection.
    # No archive hash is presented as a verified training cutoff.
    cutoff='2023-06-30' if audit_prefix else '2022-12-30'
    raw=pd.read_parquet(RAW,columns=COLUMNS,filters=[('Date','<=',pd.Timestamp(cutoff))]).rename(columns=str.lower)
    four=pd.read_parquet(cache/'full.parquet',filters=[('date','<=',pd.Timestamp(cutoff))])
    six=ga6_features(raw,four)
    all_dates=tuple(pd.Timestamp(d).strftime('%Y-%m-%d') for d in sorted(raw.date.unique()))
    smoke_dates=tuple(d for d in all_dates if d<='2022-12-30')[-sessions:]
    dates=all_dates if audit_prefix else smoke_dates
    six=six.loc[six.date>=dates[0]].copy()
    tickers=tuple(sorted(raw.ticker.unique()))
    rows={pd.Timestamp(d).strftime('%Y-%m-%d'):{r['ticker']:r for r in g.to_dict('records')} for d,g in six.groupby('date')}
    panels={d:ga7_bars(six.loc[six.date==d],decision_date=d,eligibility=dict.fromkeys(tickers,True),columns=SEVEN_COLUMNS) for d in dates}
    for section in panels.values():
        for bar in section.values():
            bar['eligible']=bool(np.isfinite([bar['features'][genome.feature_a],bar['features'][genome.feature_b]]).all())
    raw_rows={pd.Timestamp(d).strftime('%Y-%m-%d'):{r['ticker']:r for r in g.to_dict('records')} for d,g in raw.loc[raw.date>=dates[0]].groupby('date')}
    bars={d:{t:Bar(float(r['open']),float(r['close'])) for t,r in raw_rows[d].items()} for d in dates}
    needed=required_ga6(candidate,LEGACY)
    counts=Counter(); probe=Counter(); seven_reference=Counter(); native_calls=Counter()

    from .ga7_native_daily_producer import decision
    def ga7_action(bar,state,defense=False):
        def signal(g,b):
            native_calls['GA7_native_passes']+=1
            return passes(g,b)
        def strength(g,b):
            native_calls['GA7_native_score_signal']+=1
            return score_signal(g,b)
        return decision(genome,bar,state,defensive=defense,
            signal_evaluator=signal,strength_evaluator=strength) or ('PASS',0.)

    from .ga6_native_daily_producer import decision as decision6
    # Direct native GA6 flat + hypothetical held states on real feature rows.
    # These probes establish amount/action semantics, not observed holdings.
    for i,date in enumerate(dates):
        for ticker,row in rows[date].items():
            for label,entry_ratio in (('flat',None),('held',1.),('adverse_entry',1.10)):
                state=None if entry_ratio is None else dict(shares=10.,entry=row['close']*entry_ratio,
                    peak=row['close']*max(1.,entry_ratio),entry_session=i-5,weight=.1)
                held=None if state is None else SimpleNamespace(shares=state['shares'],entry_price=state['entry'],peak_price=state['peak'],entry_session=state['entry_session'])
                action,amount=native_action(candidate,row,held,i);native_calls['GA6_native_action']+=1
                probe[label+':'+action]+=1
                # Do not manufacture proposal lineage merely to compare the
                # authenticated wrapper. Validate raw native semantics here.
                diagnostic_row=dict(row,eligible=True)
                def evaluate(*args):
                    native_calls['GA6_native_action']+=1
                    return native_action(*args)
                if action=='NO_DATA':
                    if state is not None:
                        try:decision6(candidate,diagnostic_row,state,session=i,evaluator=evaluate)
                        except ValueError as exc:
                            if 'missing held GA6' not in str(exc):raise
                        else:raise ValueError('GA6 held warmup did not fail closed')
                    elif decision6(candidate,diagnostic_row,state,session=i,evaluator=evaluate) is not None:
                        raise ValueError('GA6 flat warmup did not fail closed')
                    continue
                converted=decision6(candidate,diagnostic_row,state,session=i,evaluator=evaluate)
                if action=='NO_ENTRY':
                    if converted is not None:raise ValueError('GA6 false entry')
                else:
                    target=0. if action=='EXIT' else float(amount) if state is None else state['weight']
                    if action=='REDUCE':target=state['weight']*amount
                    if action=='ADD':target=min(.30,state['weight']+amount)
                    expected_action='HOLD' if action=='ADD' and target<=state['weight'] else action
                    if converted!=(expected_action,target):raise ValueError('native GA6 held-action parity failed')
                if action not in ('NO_ENTRY','ENTER','HOLD','ADD','REDUCE','EXIT'):
                    raise ValueError('unrecognized native GA6 action')

    # Independent native GA7 replay oracle on each actual consecutive triple.
    # Known first-entry holdings permit held-action comparison without mirroring
    # the native multi-position funding engine or inspecting interpreter frames.
    for i in range(len(dates)-2):
        ds=dates[i:i+3]
        for ticker in tickers:
            sample=[]
            for d in ds:
                bar=dict(panels[d][ticker],open=raw_rows[d][ticker]['open'],low=raw_rows[d][ticker]['low'],high=raw_rows[d][ticker]['high'])
                sample.append((d,{ticker:bar},False))
            _,ledger=replay_requests(genome,sample,passes,cash_yield=0.,record_pass=True)
            native_calls['GA7_native_replay_requests']+=1
            requested={r['session']:r['action'] for r in ledger.requests}
            state=None
            if requested.get(0)=='ENTER':
                price=sample[1][1][ticker]['open']
                qty=int(100000.*genome.entry_pct/(price*1.001))
                cash=100000.-qty*price*1.001
                close=sample[1][1][ticker]['close']
                if qty:state=dict(entry=price,weight=qty*close/(cash+qty*close))
            action,_=ga7_action(sample[1][1][ticker],state)
            expected={'INCREASE':'ADD'}.get(requested.get(1,'PASS'),requested.get(1,'PASS'))
            if action!=expected:
                raise ValueError('native GA7 held-action oracle mismatch')
            seven_reference[('held:' if state else 'flat:')+action]+=1
    book=FundedShadow([('GA6',GA6_ID),('GA7',GA7_ID)],sessions=smoke_dates,settlement_sessions=1)
    def shadow(date,session,market,defense,book):
        states=book.native_states(market)
        result=[]
        for ticker,row in rows[date].items():
            state=states.get(('GA6',GA6_ID),{}).get(ticker)
            held=None if state is None else SimpleNamespace(shares=state['shares'],entry_price=state['entry'],peak_price=state['peak'],entry_session=state['entry_session'])
            action,amount=native_action(candidate,row,held,session);native_calls['GA6_native_action']+=1
            if action not in ('NO_DATA','NO_ENTRY'):
                target=(amount if state is None else state['weight'])
                if action=='EXIT':target=0.
                if action=='REDUCE':target=state['weight']*amount
                if action=='ADD':target=min(.30,state['weight']+amount)
                result.append(DiagnosticAction(date,ticker,'GA6',GA6_ID,action,target))
            state=states.get(('GA7',GA7_ID),{}).get(ticker)
            action,target=ga7_action(panels[date][ticker],state)
            if action!='PASS':result.append(DiagnosticAction(date,ticker,'GA7',GA7_ID,action,target))
        counts.update(p.family+':'+p.action for p in result)
        return result
    # Strict missing-eligibility/model-lineage gate: capital remains idle.
    result=run([(d,bars[d],[],[],False) for d in smoke_dates],shadow_book=book,
        shadow_native=shadow,settlement_sessions=1,max_sessions=sessions)
    from .ledger_audit import funded_shadow as audit_ledger
    reconciliation=audit_ledger(owners=book.cash,sessions=smoke_dates,bars=bars,
        fills=book.fills,nav_history=book.nav_history)
    evidence=dict(shadow_reconciliation=reconciliation,status='DIAGNOSTIC_ONLY_NOT_LAUNCH_READY',first_date=smoke_dates[0],last_date=smoke_dates[-1],sessions=len(smoke_dates),tickers=500,
        action_audit_sessions=len(dates),action_audit_first=dates[0],action_audit_last=dates[-1],
        shared_bank_fills=len(result['ledger']),shared_bank_nav=result['nav'][-1][1],
        shared_bank_gate='BLOCKED_UNKNOWN_PIT_AND_MODEL_TRAINING_LINEAGE',
        shadow_fills=len(book.fills),shadow_completed=len(book.completed),shadow_rejections=len(book.rejections),
        actions=dict(sorted(counts.items())),GA6_state_probes=dict(sorted(probe.items())),
        GA7_native_oracle=dict(sorted(seven_reference.items())),
        parity_scope=dict(GA6_sessions=len(dates),GA6_tickers=500,GA6_states_per_row=3,
            GA7_oracle_sessions=len(dates)-2,GA7_first_oracle_date=dates[1],GA7_last_oracle_date=dates[-2],
            GA7_missing_boundary_oracle_dates=[dates[0],dates[-1]],required_feature_warmup_gate=True),
        native_calls=dict(native_calls),
        sources={str(p):digest(p) for p in [RAW,BANK,CHECKPOINT,Path('/opt/mts/ga6/native_position_decision_adapter.py'),Path('/opt/mts/ga7-deploy/ga7_unbounded/ga7/request_replay.py'),Path(__file__),Path(__file__).with_name('ga6_native_daily_producer.py'),Path(__file__).with_name('ga7_native_daily_producer.py'),Path(__file__).with_name('funded_shadow.py'),Path(__file__).with_name('ledger_audit.py'),Path('/opt/mts/ga7-deploy/ga7_unbounded/ga7/runner.py'),Path('/opt/mts/ga7-deploy/ga7_unbounded/ga7/fold_features.py'),Path('/opt/mts/ga5_redesign/fast_decision.py')]},
        checkpoint_sha256=checkpoint_hash,model_trained_through=None,eligibility='ALL_TRUE_DIAGNOSTIC_ONLY',
        corporate_actions='NO_SUPPLIED_EVENT_STREAM; defaults are an unverified diagnostic convention',
        proof_values_read=False,validation_values_read=audit_prefix,
        validation_scope='previously open engineering prefix; no tuning or forward outcome columns' if audit_prefix else 'not read',
        deterministic_sha256=hashlib.sha256(json.dumps(dict(fills=book.fills,nav=book.nav_history,actions=dict(counts)),sort_keys=True).encode()).hexdigest(),
        performance=dict(wall_seconds=time.perf_counter()-started,cpu_seconds=time.process_time()-cpu,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024),
        limitations=['GA4 and Horizons blocked, not evaluated','GA6 hypothetical held probes are not authentic historical portfolios',
            'GA7 isolated 3-session oracle verifies decisions, not full funded native ledger parity',
            'Unknown lineage never passes authenticated proposal or DailyFeed gates','No certified eligibility, earnings, niche or risk inputs; no performance claim'])
    return evidence


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sessions',type=int,default=32)
    parser.add_argument('--audit-prefix',action='store_true',help='audit raw decisions across the existing 393-session open engineering prefix; smoke remains 32 training sessions')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();target=args.output.resolve()
    if not (target.is_relative_to(Path(__file__).resolve().parents[2]) or target.is_relative_to('/tmp')):parser.error('workspace or /tmp output required')
    result=smoke(args.sessions,audit_prefix=args.audit_prefix);target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    return 2

if __name__=='__main__':raise SystemExit(main())
