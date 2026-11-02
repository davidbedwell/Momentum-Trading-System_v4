"""Background, single-process funded replay enrichment. No optimizer inputs modified."""
import json,sqlite3,time,sys
from collections import defaultdict
from datetime import date
from .engine import load_panel,replay,Gene,Manager
from .run import RAW

def classify(breadth,vol):
    if breadth is None or not (0<=breadth<=1):return 'unknown'
    return ('bear' if breadth<.4 else 'bull' if breadth>.6 else 'mixed')+('_volatile' if vol>.018 else '_calm')

def analyze(fills,panel):
    lots=defaultdict(list);trades=[];unmatched=0;date_index={str(d.date()):i for i,d in enumerate(panel.dates)}
    for f in fills:
        key=f['ticker'];action=f['action'];qty=float(f['quantity']);price=float(f['price']);commission=float(f['notional'])*.0001
        idx=date_index[f['date']]
        if action in ('ENTRY','ADD'):
            lots[key].append(dict(q=qty,price=price,commission=commission,ti=idx,gene=f['gene'],niche=int(panel.niche[idx,panel.symbols.index(key)])))
        elif action in ('EXIT','REDUCE','REPLACE'):
            remaining=qty
            while remaining>1e-8 and lots[key]:
                lot=lots[key][0];take=min(remaining,lot['q']);entry_fee=lot['commission']*take/lot['q'];exit_fee=commission*take/qty
                pnl=take*(price-lot['price'])-entry_fee-exit_fee
                bi=lot['ti'];j=panel.symbols.index(key)
                b=float(panel.breadth[bi]);window=panel.returns[max(0,bi-19):bi+1];import numpy as np
                vol=float(np.nanmedian(np.abs(window))) if np.isfinite(window).any() else 0.
                trades.append(dict(ticker=key,gene=lot['gene'],entry_niche=lot['niche'],exit_niche=int(panel.niche[idx,j]),entry_regime=classify(b,vol),pnl=pnl,entry_notional=take*lot['price'],holding_sessions=idx-bi,entry_date=str(panel.dates[bi].date()),exit_date=f['date']))
                lot['q']-=take;lot['commission']-=entry_fee;remaining-=take
                if lot['q']<1e-8:lots[key].pop(0)
            if remaining>1e-8:unmatched+=1
    def stats(ts):
        wins=[t['pnl'] for t in ts if t['pnl']>0];losses=[t['pnl'] for t in ts if t['pnl']<0];n=len(ts)
        return dict(trades=n,win_rate=len(wins)/n if n else None,avg_win=sum(wins)/len(wins) if wins else None,avg_loss=sum(losses)/len(losses) if losses else None,profit_factor=sum(wins)/-sum(losses) if losses else None,net_expectancy=sum(t['pnl'] for t in ts)/n if n else None,avg_holding_sessions=sum(t['holding_sessions'] for t in ts)/n if n else None,total_realized_pnl=sum(t['pnl'] for t in ts))
    regimes=defaultdict(list);niches=defaultdict(list);genes=defaultdict(list)
    for t in trades:regimes[t['entry_regime']].append(t);niches[str(t['entry_niche'])].append(t);genes[str(t['gene'])].append(t)
    return dict(overall=stats(trades),by_entry_regime={k:stats(v) for k,v in regimes.items()},by_entry_niche={k:stats(v) for k,v in niches.items()},by_gene={k:stats(v) for k,v in genes.items()},unmatched_closures=unmatched,open_lots=sum(len(v) for v in lots.values()),method='PIT entry regime, realized FIFO lots, execution-price slippage and commission; partial exits counted as closed lots; no lookahead')

def main(path,limit=0):
    db=sqlite3.connect(path,timeout=60);db.execute('PRAGMA busy_timeout=60000')
    db.execute('CREATE TABLE IF NOT EXISTS replay_trade_evidence (id TEXT, training_phase INTEGER, training_start TEXT, training_end TEXT, evidence_json TEXT, PRIMARY KEY(id,training_phase))');db.commit()
    panel,_=load_panel(RAW,end='2023-01-01');rows=db.execute('''SELECT c.id,c.genes_json,c.manager_json,c.first_phase FROM chromosomes c WHERE EXISTS (SELECT 1 FROM evaluations e WHERE e.id=c.id AND e.phase=0 AND json_extract(e.metrics_json,'$.cagr')>=.15 AND json_extract(e.metrics_json,'$.max_drawdown')<.20 AND json_extract(e.metrics_json,'$.calmar')>=2.0) ORDER BY c.first_generation,c.id''').fetchall()
    def tup(x):return tuple(map(tup,x)) if isinstance(x,list) else x
    t0=time.monotonic();done=0
    for cid,gj,mj,phase in rows:
        if db.execute('SELECT 1 FROM replay_trade_evidence WHERE id=? AND training_phase=?',(cid,0)).fetchone():continue
        genes=[Gene(**dict(g,entry_tree=tup(g.get('entry_tree',())))) for g in json.loads(gj)]
        result=replay(panel,genes,Manager(**json.loads(mj)),'2022-01-01','2023-01-01',True)
        evidence=analyze(result['fills'],panel);evidence['replay_metrics']=result['metrics'];evidence['source']='2022 training replay, NOT independent validation'
        db.execute('INSERT OR REPLACE INTO replay_trade_evidence VALUES (?,?,?,?,?)',(cid,0,'2022-01-01','2023-01-01',json.dumps(evidence)))
        db.execute('INSERT OR REPLACE INTO extracted_evidence SELECT c.id, e.metrics_json, (SELECT count(*) FROM evaluations z WHERE z.id=c.id), 1, json_extract(e.metrics_json,"$.closed_trades"),json_extract(e.metrics_json,"$.fills"),json_extract(e.metrics_json,"$.exposure"),"exploratory_2022_attributed","funded_replay_completed","pending_forward_evidence" FROM chromosomes c JOIN evaluations e ON e.id=c.id WHERE c.id=? AND e.phase=0 ORDER BY json_extract(e.metrics_json,"$.cagr") DESC LIMIT 1',(cid,))
        db.execute('UPDATE chromosomes SET actual_origin_regime=?,origin_regime_status=? WHERE id=?',(max(evidence['by_entry_regime'],key=lambda k:evidence['by_entry_regime'][k]['total_realized_pnl']) if evidence['by_entry_regime'] else None,'exploratory_2022_attributed',cid))
        db.commit();done+=1
        if done%5==0:print('completed',done,'of',len(rows),'seconds',round(time.monotonic()-t0,1),flush=True)
        if limit and done>=limit:break
    print(json.dumps(dict(completed=done,eligible_at_start=len(rows),elapsed_seconds=round(time.monotonic()-t0,2))),flush=True)
if __name__=='__main__':main(sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else 0)
