"""Artificial parser/checkpoint cases only; never research observations."""
import pytest
from sector_pipeline.exploratory import Tables, reconstruct, run
from sector_pipeline.storage import resume_source


def test_wikipedia_reverse_membership_and_missing_sectors():
    wiki={'current':[['Symbol','Security','GICS Sector','x','x','x','CIK'],['NEW','New','Tech','','','','123']],
          'changes':[['Date','Added','Added','Removed','Removed'],['January 5, 2010','NEW','New','OLD','Old']]}
    members,ciks,errors=reconstruct(wiki)
    assert not errors
    assert next(m for m in members if m['symbol']=='OLD')['end']=='2010-01-05'
    assert next(m for m in members if m['symbol']=='OLD')['sector']=='UNKNOWN'
    assert next(m for m in members if m['symbol']=='NEW')['start']=='2010-01-05'
    assert ciks=={'NEW':'123'}


def test_rowspan_changes_preserved():
    p=Tables(); p.feed('<table><tr><td rowspan="2">January 5, 2010</td><td>A</td><td>a</td><td>B</td><td>b</td></tr><tr><td>C</td><td>c</td><td>D</td><td>d</td></tr></table>')
    assert p.tables[0][1]==['January 5, 2010','C','c','D','d']


def test_retry_checkpoint_skips_success_and_checks_integrity(tmp_path):
    calls=[]
    def loader(): calls.append(1); return {'actual':'payload'}
    assert resume_source(tmp_path,'wiki',{},loader)==resume_source(tmp_path,'wiki',{},loader)
    assert len(calls)==1
    path=next(tmp_path.glob('*.json')); path.write_text(path.read_text().replace('actual": "payload','actual": "tampered'))
    with pytest.raises(ValueError,match='Corrupt'): resume_source(tmp_path,'wiki',{},loader)


def test_stage2_rejected_before_any_io():
    with pytest.raises(ValueError,match='Stage1'): run('/outside/workspace',start='2016',end='2016')


def test_fetch_failure_is_reported_without_claim(tmp_path,monkeypatch):
    import sector_pipeline.exploratory as e
    monkeypatch.setattr(e.adapters,'local',lambda p:tmp_path)
    monkeypatch.setattr(e,'wikipedia',lambda: (_ for _ in ()).throw(OSError('offline')))
    result=e.run(tmp_path,symbols=['A'])
    assert result['status'].startswith('BLOCKED')
    assert result['stage2']=='SEALED'
    assert not (tmp_path/'research_state').exists()
