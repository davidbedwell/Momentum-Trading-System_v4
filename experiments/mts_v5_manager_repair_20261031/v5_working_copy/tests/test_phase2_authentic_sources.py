"""Small deterministic native-source checks; fixtures are not research outcomes."""
import json
from pathlib import Path
import sqlite3
import pytest


def test_restore_archived_ga6_and_native_amount_parity(monkeypatch):
    import sys
    monkeypatch.setattr(sys,'path',['/opt/mts','/opt/mts/ga5_redesign',*sys.path])
    from discovery.competitive_ga.archived_genomes import ga6
    from discovery.competitive_ga.ga6_native_daily_producer import produce
    from ga6.native_position_decision_adapter import native_action,HeldState
    from ga5_feature_adapter import LEGACY
    from discovery.competitive_ga.synthetic_native_feature_gate import leaves
    path=Path('/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite')
    with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) as db:
        cid=db.execute('select id from chromosomes order by id limit 1').fetchone()[0]
    candidate=ga6(path,[cid])[cid]
    g=candidate.genome
    fields={getattr(g,k) for k in ('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature')}|leaves(candidate.entry_tree)
    row={LEGACY.get(f,f):.8 for f in fields};row['close']=101
    action,amount=native_action(candidate,row,HeldState(1,100,105,0),4)
    proposals=produce(candidate,{'A':row},decision_date='2026-01-12',session=4,
        chromosome_id=cid,trained_through='2026-01-01',source_hash='fixture',
        snapshot_hash='fixture',held={'A':dict(entry=100,peak=105,shares=1,entry_session=0,weight=.1)})
    assert action=='ADD' and proposals[0].action==action
    assert proposals[0].target_weight==pytest.approx(.1+amount)
    with pytest.raises(ValueError,match='missing or ambiguous'):
        ga6(path,['missing-id'])


def test_restore_ga7_and_native_eligible_ranks(monkeypatch):
    import sys
    monkeypatch.setattr(sys,'path',['/opt/mts/ga7-deploy/ga7_unbounded',*sys.path])
    import pandas as pd
    from ga7.engine import Genome
    from ga7.runner import COLUMNS
    from discovery.competitive_ga.archived_genomes import ga7,ga7_bars
    path=Path('/opt/mts/ga7-deploy/ga7_unbounded/runs/preflight_16/checkpoint.json')
    cid=Genome(**json.loads(path.read_text())['population'][0]).identity()
    restored,digest=ga7(path,[cid])
    assert restored[cid].identity()==cid and len(digest)==64
    frame=pd.DataFrame([dict(date='2026-01-12',ticker=t,close=100,
        **{k:v for k in COLUMNS}) for t,v in [('A',-.2),('B',.2),('C',.2),('D',10)]])
    bars=ga7_bars(frame,decision_date='2026-01-12',
        eligibility={'A':True,'B':True,'C':True,'D':False},columns=COLUMNS)
    assert [bars[t]['features'][COLUMNS[0]] for t in ('A','B','C')]==pytest.approx([1/3,5/6,5/6])
    with pytest.raises(ValueError,match='missing archived'):
        ga7(path,['missing-id'])
