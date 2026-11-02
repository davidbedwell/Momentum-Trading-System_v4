"""Post-run functional evidence; never evaluates holdout again."""
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import numpy as np
from .engine import *
from .run import RAW


def main():
    root=Path('/opt/mts/ga8')
    p,_=load_panel(RAW)
    ledger=json.loads((root/'pilot_lineage.json').read_text())
    children=[x for x in ledger if x['parents'] and x['id'] not in x['parents']]
    child=children[0]
    first=next(x for x in ledger if x['id']==child['parents'][0])
    def run(row,m=None):
        return replay(p,[Gene(**x) for x in row['genes']],m or Manager(**row['manager']),'2022-01-01','2023-01-01',True)
    a,b=run(first),run(child)
    counter=run(first,Manager(slots=3,reserve=.5,correlation=.65))
    def digest(result):
        return hashlib.sha256(json.dumps(result['fills'],sort_keys=True).encode()).hexdigest()
    smoke=json.loads((root/'smoke.json').read_text())
    actions={action:sum(x['action']==action for x in smoke['fills']) for action in ['ENTRY','ADD','REDUCE','EXIT','REPLACE']}
    # Full independent shadow accounts for every unique pilot gene, including nonselected specialists.
    bank={json.dumps(g,sort_keys=True):g for row in ledger for g in row['genes']}
    shadows=[]
    for key,g in bank.items():
        result=replay(p,[Gene(**g)],Manager(),'2022-01-01','2023-01-01',True)
        shadows.append(dict(gene=g,**result))
    (root/'pilot_shadow_bank.json').write_text(json.dumps(dict(note='Each is an independent $100k native account; not funded portfolio equity',accounts=shadows),indent=2))
    # Only retrospective development labels. Terminal forward windows are purged.
    # No search fitness or thresholds reads this diagnostic table.
    label_rows=[]
    table=[]
    end=np.flatnonzero(p.dates<'2025-01-01')[-1]
    for t in range(60, end-20+1):
        for j in range(len(p.symbols)):
            if p.niche[t,j]<0 or not np.isfinite(p.open[t+1,j]) or not np.isfinite(p.close[t+20,j]):
                continue
            table.append(dict(date=str(p.dates[t].date()),ticker=p.symbols[j],niche=int(p.niche[t,j]),
                label_known_at=str(p.dates[t+20].date()),
                forward_20=(p.close[t+20,j]+p.dividends[t+2:t+21,j].sum())/p.open[t+1,j]-1,
                **{k:float(v[t,j]) for k,v in p.features.items()}))
    pd.DataFrame(table).to_parquet(root/'development_opportunities.parquet',index=False)
    for niche in range(3):
        for horizon in [5,20]:
            values=[]
            for t in range(60,end-horizon+1):
                # Entry next open and exit close h sessions later, causal time t key.
                available=(p.niche[t]==niche) & np.isfinite(p.open[t+1]) & np.isfinite(p.close[t+horizon])
                if available.any():
                    div=p.dividends[t+2:t+horizon+1,available].sum(axis=0)
                    values.extend(((p.close[t+horizon,available]+div)/p.open[t+1,available]-1).tolist())
            label_rows.append(dict(niche=niche,horizon=horizon,count=len(values),mean_forward_return=float(np.mean(values))))
    (root/'opportunity_labels.json').write_text(json.dumps(dict(purpose='Retrospective training diagnostic only; never used in live features or holdout selection',train_end_exclusive='2025-01-01',labels=label_rows),indent=2))
    result=dict(parent_id=first['id'],child_id=child['id'],parents=child['parents'],parent_fills_sha256=digest(a),
                offspring_fills_sha256=digest(b),manager_counterfactual_fills_sha256=digest(counter),
                offspring_changes_funded_decisions=digest(a)!=digest(b),manager_changes_funded_decisions=digest(a)!=digest(counter),
                smoke_actions=actions,smoke_audit=smoke['audit'],shadow_accounts=len(shadows),
                pilot_family_coverage=sorted(set(g['family'] for row in ledger for g in row['genes'])),
                nested_offspring=sum(bool(g.get('entry_tree')) for row in ledger for g in row['genes']),
                all_ledger_accounting_passed=all(x['audit']['max_identity_error']<1e-5 for x in ledger))
    assert result['offspring_changes_funded_decisions'] and result['manager_changes_funded_decisions']
    assert all(actions[x]>0 for x in ['ENTRY','ADD','REDUCE','EXIT','REPLACE'])
    assert result['all_ledger_accounting_passed']
    (root/'functionality_evidence.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__': main()
