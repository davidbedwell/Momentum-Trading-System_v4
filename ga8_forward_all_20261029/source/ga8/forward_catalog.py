"""Chronological forward test of all distinct qualifying phase candidates.
Results are observational and never returned to evolutionary selection.
"""
import json
from pathlib import Path
from .engine import replay,rank
from .long_run import decode,atomic

def qualifying(row):
    m=row['metrics']
    return m['cagr']>=.15 and m['max_drawdown']<.20 and m['calmar']>=2.0

def catalog(journal,phase):
    candidates={}
    with Path(journal).open() as stream:
        for line in stream:
            record=json.loads(line)
            if record['phase']!=phase:continue
            for row in record['rows']:
                if qualifying(row):
                    old=candidates.get(row['id'])
                    if old is None or rank(row)>rank(old):candidates[row['id']]=row
    return sorted(candidates.values(),key=rank,reverse=True)

def forward_all(panel,journal,phase,start,end,output):
    """Incremental durable JSONL, idempotent across interruption and resume."""
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    candidates=catalog(journal,phase)
    done={}
    if output.exists():
        with output.open() as f:
            for line in f:
                r=json.loads(line);done[r['id']]=r
    with output.open('a') as f:
        for row in candidates:
            if row['id'] in done:continue
            genes,manager=decode(row)
            result=replay(panel,genes,manager,start,end,True)
            m=result['metrics'];training=row['metrics']
            r=dict(id=row['id'],phase=phase,train_metrics=training,forward_metrics=m,
                   transfer_cagr_delta=m['cagr']-training['cagr'],
                   transfer_ratio=m['cagr']/training['cagr'] if training['cagr']>0 else None,
                   forward_feasible=qualifying(dict(metrics=m)),
                   gene_niches=sorted(set(g.niche for g in genes)),
                   gene_families=sorted(set(g.family for g in genes)))
            # Funded replay fills retained separately for later trade-level attribution.
            from .trade_evidence import trade_statistics
            r['trade_statistics']=trade_statistics(result['fills'])
            r['regime_attribution_status']='pending_point_in_time_trade_attribution'
            f.write(json.dumps(r,allow_nan=False)+'\n');f.flush()
            done[r['id']]=r
    summary=dict(phase=phase,eligible=len(candidates),tested=len(done),
                 forward_qualifying=sum(x['forward_feasible'] for x in done.values()),
                 top_transferable=sorted(done.values(),key=lambda x:(x['forward_feasible'],x['forward_metrics']['cagr'],-x['forward_metrics']['max_drawdown']),reverse=True)[:25])
    from .chromosome_catalog import connect
    with connect(output.parent/'chromosome_library.sqlite') as db:
        for item in done.values():
            db.execute('INSERT OR REPLACE INTO forward_evidence VALUES (?,?,?,?,?)',
                (item['id'],phase,json.dumps(item['forward_metrics']),json.dumps(item.get('trade_statistics')),json.dumps(dict(status=item.get('regime_attribution_status','pending')))))
            db.execute('UPDATE chromosomes SET transfer_status=? WHERE id=?',('forward_tested',item['id']))
        db.commit()
    atomic(output.with_suffix('.summary.json'),summary)
    return summary
