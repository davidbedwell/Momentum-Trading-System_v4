"""Append-only chromosome evidence registry, with SQLite unique-ID index.
No future outcomes used in discovery; unavailable evidence is explicitly pending.
"""
import json,sqlite3
from pathlib import Path

def connect(path):
    db=sqlite3.connect(path,timeout=60)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('CREATE TABLE IF NOT EXISTS chromosomes (id TEXT PRIMARY KEY, first_phase INTEGER, first_generation INTEGER, genes_json TEXT NOT NULL, manager_json TEXT NOT NULL, assigned_niches_json TEXT NOT NULL, families_json TEXT NOT NULL, parent_ids_json TEXT NOT NULL, actual_origin_regime TEXT DEFAULT NULL, origin_regime_status TEXT NOT NULL DEFAULT "pending_attribution", transfer_status TEXT NOT NULL DEFAULT "not_forward_tested")')
    db.execute('CREATE TABLE IF NOT EXISTS evaluations (id TEXT, phase INTEGER, generation INTEGER, metrics_json TEXT, audit_json TEXT, PRIMARY KEY(id,phase,generation))')
    db.execute('CREATE TABLE IF NOT EXISTS forward_evidence (id TEXT, phase INTEGER, metrics_json TEXT, trade_stats_json TEXT, regime_stats_json TEXT, PRIMARY KEY(id,phase))')
    return db

def record(db,rows,phase,generation):
    for r in rows:
        genes=r['genes']
        db.execute('INSERT OR IGNORE INTO chromosomes(id,first_phase,first_generation,genes_json,manager_json,assigned_niches_json,families_json,parent_ids_json) VALUES (?,?,?,?,?,?,?,?)',
          (r['id'],phase,generation,json.dumps(genes),json.dumps(r['manager']),json.dumps(sorted({g['niche'] for g in genes})),json.dumps(sorted({g['family'] for g in genes})),json.dumps(r.get('parents',[]))))
        db.execute('INSERT OR IGNORE INTO evaluations VALUES (?,?,?,?,?)',(r['id'],phase,generation,json.dumps(r['metrics']),json.dumps(r['audit'])))
    db.commit()

def backfill(journal,database):
    db=connect(database);n=0
    with Path(journal).open() as f:
        for line in f:
            d=json.loads(line);record(db,d['rows'],d['phase'],d['fold_generation']);n+=1
    print(json.dumps(dict(generations=n,chromosomes=db.execute('SELECT COUNT(*) FROM chromosomes').fetchone()[0],evaluations=db.execute('SELECT COUNT(*) FROM evaluations').fetchone()[0])))
    db.close()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('journal');p.add_argument('database');a=p.parse_args();backfill(a.journal,a.database)
