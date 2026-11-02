"""Host-side bounded FB/XLNX evidence retrieval. Never writes accepted bars.

Explicit diagnostic scope includes protected FB; existing quarantine is unchanged.
"""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pandas as pd
from ga9.alpaca_repair import Client, bars, credentials
from ga9.ticker_lineage import EVENTS, historical_identity


def prior_recoveries(directories):
    """Only count gap rows supported by original SIP/raw response bytes."""
    found = set()
    for directory in directories:
        root = Path(directory).resolve()
        report = json.loads((root/'report.json').read_text())
        for rec in report['requests']:
            p = rec.get('params', {})
            symbol = p.get('symbols')
            if rec.get('http_status') != 200 or symbol not in ('FB','XLNX') or p.get('feed') != 'sip' or p.get('adjustment') != 'raw':
                continue
            path = (root/rec['source_file']).resolve()
            if path.parent != root:
                raise ValueError('Source path escapes evidence directory')
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != rec['source_sha256']:
                raise ValueError('Prior source hash mismatch')
            data = json.loads(raw)
            if set(data.get('bars', {})) - {symbol}:
                raise ValueError('Unexpected prior symbol')
            for bar in data.get('bars', {}).get(symbol, []):
                day = pd.Timestamp(bar['t']).tz_convert('America/New_York').date().isoformat()
                found.add((symbol, day))
    return found


def run(gaps, output, previous=(), credential_file='/root/.config/mts/alpaca.env', budget=8):
    if not 1 <= budget <= 16:
        raise ValueError('Request bound is 1..16')
    frame = pd.read_csv(gaps, dtype=str)
    wanted = sorted(set((r.ticker,r.date) for r in frame.itertuples() if r.ticker in ('FB','XLNX')) - prior_recoveries(previous))
    if len(wanted) > 150 or any(not '2022-01-01' <= d <= '2022-12-31' for _,d in wanted):
        raise ValueError('Only bounded 2022 identity gaps permitted')
    from datetime import date
    for _, day in wanted:
        date.fromisoformat(day)
    out = Path(output).resolve()
    allowed = Path(__file__).resolve().parent
    if not (out.is_relative_to(allowed) or out.is_relative_to(Path('/tmp'))):
        raise ValueError('Output must be under ga9 or /tmp')
    out.mkdir(parents=True, exist_ok=False)
    ledger = dict(observed_at=datetime.now(timezone.utc).isoformat(), events=[dict(**asdict(e), digest=e.digest) for e in EVENTS])
    with (out/'lineage.json').open('x') as f:
        json.dump(ledger,f,indent=2)
    report = dict(status='DIAGNOSTIC_ONLY_NOT_PIT_CERTIFIED', baseline_remaining=len(wanted),
                  gap_source_sha256=hashlib.sha256(Path(gaps).read_bytes()).hexdigest(),
                  previous_evidence=[str(Path(p).resolve()) for p in previous],
                  raw_recovered_gaps=0, certified_recovered_gaps=0, accepted_raw_rows=0,
                  work=[], requests=[], replay_executed=False, long_GA_executed=False)
    recovered = {}; client = None
    try:
        client = Client(out, credentials(credential_file), budget)
        for symbol in ('FB','XLNX'):
            dates = [d for s,d in wanted if s == symbol]
            if not dates: continue
            # FB is queried while its symbol was valid; no AMD request is possible.
            asof = '2022-06-08' if symbol == 'FB' else '2022-02-11'
            item = dict(ticker=symbol, asof=asof, dates=dates,
                        post_last_trade_dates=[d for d in dates if symbol == 'XLNX' and d > '2022-02-11'])
            report['work'].append(item)
            try:
                rows = bars(client, symbol, min(dates), max(dates), asof=asof)
                for row in rows:
                    if row['date'] not in dates: continue
                    identity = historical_identity(symbol,row['date'])
                    if identity.get('post_last_trade'):
                        item.setdefault('unexpected_post_last_trade_bars', []).append(row['date'])
                        continue
                    row.update(identity=identity, asof=asof, feed='sip', adjustment='raw',
                               verified_scope='VENDOR_RAW_DIAGNOSTIC_ONLY')
                    recovered[(symbol,row['date'])] = row
            except (ValueError, RuntimeError) as exc:
                item['error_type'] = type(exc).__name__
                if client.requests and client.requests[-1].get('http_status') in (401,403,429):
                    break
    except ValueError as exc:
        report['access_blocker'] = type(exc).__name__
    report['requests'] = client.requests if client else []
    report['raw_recovered_gaps'] = len(recovered)
    report['remaining'] = [dict(ticker=s,date=d, diagnosis=('POST_LAST_TRADE_NO_XLNX_BAR_EXPECTED' if s=='XLNX' and d>'2022-02-11' else 'UNRECOVERED')) for s,d in wanted if (s,d) not in recovered]
    (out/'recovered_raw.json').write_text(json.dumps(list(recovered.values()),indent=2)+'\n')
    (out/'accepted_raw.json').write_text('[]\n')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--gaps', required=True); p.add_argument('--output', required=True)
    p.add_argument('--previous', action='append', default=[])
    p.add_argument('--credential-file', default='/root/.config/mts/alpaca.env')
    p.add_argument('--max-requests',type=int,default=8)
    a = p.parse_args()
    r = run(a.gaps,a.output,a.previous,a.credential_file,a.max_requests)
    print(json.dumps({k:v for k,v in r.items() if k not in ('requests','work','remaining')},indent=2))
    return 2  # Retrieval never authorizes trading.

if __name__ == '__main__':
    raise SystemExit(main())
