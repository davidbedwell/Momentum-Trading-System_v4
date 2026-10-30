"""Bounded evidence ingestion and fail-closed chronological plumbing proof.

Raw recovery never implies membership, action reconciliation or model eligibility.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .ticker_lineage import EVENTS, historical_identity, XLNX
from .execution import Panel, Gene, Manager, replay
from .screening import daily_screen, ScreenPolicy


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ingest(gaps, batches):
    wanted = {(r.ticker, r.date) for r in pd.read_csv(gaps, dtype=str).itertuples()}
    recovered, provenance = {}, []
    for batch in sorted(map(Path, batches)):
        report = json.loads((batch/'report.json').read_text())
        provenance.extend(dict(path=str(batch/name), sha256=sha(batch/name))
                          for name in ('report.json', 'recovered_raw.json'))
        requests = {r['source_file']: r for r in report['requests'] if r.get('http_status') == 200}
        for row in json.loads((batch/'recovered_raw.json').read_text()):
            key = row['ticker'], row['date']
            if key not in wanted:
                raise ValueError('Recovered row outside requested gaps')
            name = row['source_file']
            if Path(name).name != name or name not in requests:
                raise ValueError('Untracked response')
            req = requests[name]
            path = batch/name
            if sha(path) != row['source_sha256'] or sha(path) != req['source_sha256']:
                raise ValueError('Response hash mismatch')
            params = req['params']
            if params['feed'] != 'sip' or params['adjustment'] != 'raw' or params['symbols'] != key[0]:
                raise ValueError('Wrong vendor identity/feed/adjustment')
            source = json.loads(path.read_text()).get('bars', {}).get(key[0], [])
            matches = [b for b in source if b['t'] == row['t']]
            fields = ('o', 'h', 'l', 'c', 'v')
            if len(matches) != 1 or any(matches[0][k] != row[k] for k in fields):
                raise ValueError('Row differs from response')
            day = pd.Timestamp(row['t']).tz_convert('America/New_York').date().isoformat()
            values = [row[k] for k in fields]
            if day != key[1] or not np.isfinite(values).all() or min(values[:4]) <= 0 or row['v'] < 0 or row['h'] < max(values[:4]) or row['l'] > min(values[:4]):
                raise ValueError('Invalid OHLCV/session')
            if key[0] == 'XLNX' and key[1] > XLNX.effective_at:
                raise ValueError('Unexpected post-last-trade XLNX bar')
            evidence = dict(ticker=key[0], date=key[1], **{k: row[k] for k in fields},
                            response=str(path), response_sha256=sha(path), asof=params.get('asof'),
                            admission='QUARANTINED_RAW_ONLY')
            if key[0] in ('FB', 'XLNX'):
                evidence['lineage'] = historical_identity(*key)
            if key in recovered and any(recovered[key][k] != evidence[k] for k in fields):
                raise ValueError('Conflicting recovery batches')
            recovered.setdefault(key, evidence)
        for name in sorted(requests):
            if sha(batch/name) != requests[name]['source_sha256']:
                raise ValueError('Response hash mismatch')
            provenance.append(dict(path=str(batch/name), sha256=sha(batch/name)))
    corrections = sorted(k for k in wanted if k[0] == 'XLNX' and k[1] > XLNX.effective_at)
    remaining = sorted(wanted - set(recovered) - set(corrections))
    return dict(raw=[recovered[k] for k in sorted(recovered)],
                corrections=[dict(ticker=s, date=d, reason='POST_LAST_TRADE_NO_BAR_EXPECTED',
                                  evidence_digest=XLNX.digest, retrospective_only=True) for s,d in corrections],
                remaining=[dict(ticker=s,date=d, status='QUARANTINED') for s,d in remaining],
                provenance=provenance, original_gaps=len(wanted), corrected_expected_gaps=len(wanted)-len(corrections))


def empty_proof(dates):
    """Exercise actual screen, gene scoring, competition and execution with zero admission."""
    dates = pd.DatetimeIndex(dates)
    if len(dates) < 2 or not dates.is_monotonic_increasing or dates.has_duplicates:
        raise ValueError('At least two unique increasing observed sessions required')
    empty = np.empty((len(dates), 0))
    frame = pd.DataFrame(empty, index=dates)
    score, mask = daily_screen(frame, frame, frame.astype(bool), ScreenPolicy())
    from .execution import FAMILIES
    panel = Panel(dates, [], empty, empty, empty, empty,
                  {k:empty for k in FAMILIES}, empty.astype(int), np.zeros(len(dates)),
                  eligible=empty.astype(bool), screen_score=score, screen_mask=mask)
    result = replay(panel, [Gene('momentum')], Manager(), dates[0], dates[-1]+pd.Timedelta(days=1), detail=True)
    result['execution_stages'] = [dict(date=str(d.date()), stage='NEXT_OPEN', pending_orders=0,
                                       fills=0, reason='EMPTY_PIT_ADMISSION') for d in dates[1:]]
    return result


def run(gaps, batches, output):
    evidence = ingest(gaps, batches)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    dump = lambda name, value: (out/name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')
    # These are observed historical peer sessions, not a certified exchange calendar.
    dates = sorted(pd.read_csv(gaps).date.unique())[:6]
    proof = empty_proof(dates)
    dump('evidence.json', evidence)
    dump('lineage.json', [dict(**asdict(e),digest=e.digest) for e in EVENTS])
    dump('eligible_universe.json', [])
    dump('replay.json', proof)
    pd.DataFrame(evidence['remaining']).to_csv(out/'remaining_quarantined.csv',index=False)
    pd.DataFrame(evidence['corrections']).to_csv(out/'expected_session_corrections.csv',index=False)
    from .alpaca_repair import reuse_benchmark
    cache = Path(__file__).parent/'artifacts/alpaca_repair_live_batch_20261029'
    benchmark_raw = reuse_benchmark(cache) if cache.exists() else None
    report = dict(status='BLOCKED_TRADING_EMPTY_UNIVERSE_PROOF_EXECUTED',
                  original_gaps=evidence['original_gaps'], raw_recovered=len(evidence['raw']),
                  corrected_expected_gaps=evidence['corrected_expected_gaps'],
                  removed_post_last_trade_sessions=len(evidence['corrections']), remaining=len(evidence['remaining']),
                  admitted_symbols=0, sessions=len(dates), fills=proof['metrics']['fills'],
                  final_nav=proof['metrics']['final_nav'], max_drawdown=proof['metrics']['max_drawdown'],
                  benchmark=dict(primary='QQQ', frozen=True, executed=False, result=None,
                                 raw_evidence=benchmark_raw,
                                 blocker='Raw QQQ cache found; distributions/splits and availability not reconciled' if benchmark_raw else 'Raw QQQ cache unavailable; no fallback'),
                  blockers=['No verified starting roster or complete PIT event chain with stable security IDs',
                            'Recovered raw OHLCV lacks reconciled corporate actions and historical availability evidence',
                            'GOOGL and all unresolved identity/membership records remain quarantined',
                            'QQQ total-return certification and independent session calendar remain unverified'],
                  session_basis='First six real observed vendor peer sessions in gap audit; calendar unverified',
                  candidate_model='Fixed plumbing Gene(momentum); no fitted chromosome eligibility claimed',
                  gap_source=dict(path=str(gaps),sha256=sha(gaps)),
                  code_sha256={p.name:sha(p) for p in [Path(__file__),Path(__file__).with_name('execution.py'),Path(__file__).with_name('screening.py')]},
                  long_generations=0)
    dump('report.json', report)
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--gaps', required=True); p.add_argument('--batch', action='append', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    print(json.dumps(run(a.gaps,a.batch,a.output),indent=2))
