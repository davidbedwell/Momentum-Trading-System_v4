import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'discovery'/'competitive_ga'))
from retention import RetentionGate,Score

def s(ret,dd=.1): return Score(ret,dd,252)

def test_accepts_transfer_with_retention():
    g=RetentionGate()
    event=g.evaluate(1,"old","new",{"A":(s(.10),s(.11))},(s(.04),s(.09)))
    assert event["accepted"]
    assert len(g.history)==1

def test_rejects_forgetting_even_if_novel_improves():
    event=RetentionGate().evaluate(2,"old","new",{"A":(s(.20),s(.10))},(s(.01),s(.25)))
    assert not event["accepted"] and "A" in event["retention_failures"]

def test_rejects_no_transfer():
    event=RetentionGate().evaluate(3,"old","new",{"A":(s(.1),s(.11))},(s(.08),s(.07)))
    assert not event["accepted"]

def test_rejects_missing_replay_evidence():
    with pytest.raises(ValueError):
        RetentionGate().evaluate(1,"a","b",{},(s(.1),s(.2)))

def test_checkpoint_roundtrip(tmp_path):
    g=RetentionGate()
    g.evaluate(1,"old","new",{"A":(s(.10),s(.11))},(s(.04),s(.09)))
    p=tmp_path/"retention.jsonl"
    g.save(p)
    assert '"accepted": true' in p.read_text()
