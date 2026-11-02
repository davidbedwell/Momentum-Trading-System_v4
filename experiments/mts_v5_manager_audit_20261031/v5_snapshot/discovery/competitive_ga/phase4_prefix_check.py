"""Independently rebuild the training prefix and compare every dated feature hash."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
import pandas as pd
from .streaming_first_year import inventory, chunks
from .first_year_manifest import Calendar, digest


def check():
    started,cpu=time.perf_counter(),time.process_time()
    sessions,tickers=inventory()
    calendar=Calendar(sessions,'2022-12-30','2023-06-30','2023-07-03')
    evidence=Path(__file__).resolve().parents[2]/'PHASE4_INPUT_MANIFEST.json'
    longer=json.loads(evidence.read_text())
    if longer['proof_values_read'] or longer['value_end']!=calendar.validation_end:
        raise ValueError('unexpected reference seal')
    if any(digest(p)!=h for p,h in longer['sources'].items()):
        raise ValueError('longer-reference sources changed')
    reference={d['date']:d for d in longer['daily']}
    count=0
    for panel in chunks(calendar=calendar,as_of=calendar.train_end,tickers=tickers,
                        cache='/tmp/mts_phase4_stream',chunk_sessions=47):
        columns=[c for c in panel if c.endswith('__v1')]
        for date,section in panel.groupby('date'):
            signature=hashlib.sha256(pd.util.hash_pandas_object(section.sort_values('ticker')[columns],index=False).to_numpy().tobytes()).hexdigest()
            if signature!=reference[date]['features_sha256']:
                raise ValueError('prefix invariance failed')
            count+=1
        print(f'prefix matched through {panel.date.max()}',flush=True)
    return dict(status='ENGINEERING_PREFIX_INVARIANCE_PASS',sessions=count,tickers=500,features=len(columns),
        shorter_end=calendar.train_end,longer_end=calendar.validation_end,shorter_chunk_sessions=47,longer_chunk_sessions=32,
        reference_sha256=digest(evidence),implementation_sha256=digest(__file__),proof_values_read=False,
        performance=dict(wall_seconds=time.perf_counter()-started,cpu_seconds=time.process_time()-cpu,
                         peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();target=args.output.resolve()
    if not (target.is_relative_to(Path(__file__).resolve().parents[2]) or target.is_relative_to('/tmp')):parser.error('workspace or /tmp output required')
    result=check();target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
