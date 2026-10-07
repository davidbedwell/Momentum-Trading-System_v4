import json
from Core.layered_ga import v3_handoff_supervisor as s

def test_current_nonpassing_calibration_blocks_launch():
    result=s.inspect()
    assert result[0]=='STOPPED_ENGINEERING'
    assert result[2] is None

def test_supervisor_never_launches_without_positive_approval(tmp_path,monkeypatch):
    conf=tmp_path/'config.json';conf.write_text(json.dumps({'approved_launch':False,'dev117_only':True,'protected_bank_access':False,'stage2_script':'missing.py','stage2_script_sha256':'x','calibration_gate_sha256':'x'}))
    cal=tmp_path/'cal';cal.mkdir();(cal/'status.json').write_text(json.dumps({'state':'PASS'}))
    gate={'decision':'PASS','stage':'V3_MATCHED_EVOLUTIONARY_CALIBRATION',**{x:True for x in s.PASS_FIELDS}}
    (cal/'gate.json').write_text(json.dumps(gate))
    (cal/'durability_receipt.json').write_text(json.dumps({x:True for x in ('git_remote_sha_verified','backup_manifest_verified','critical_checksums_verified')}))
    monkeypatch.setattr(s,'CONFIG',conf);monkeypatch.setattr(s,'CAL',cal)
    assert s.inspect()[0]=='STOPPED_ENGINEERING'

def test_missing_durability_cannot_advance(tmp_path,monkeypatch):
    conf=tmp_path/'config.json';conf.write_text(json.dumps({'approved_launch':True,'dev117_only':True,'protected_bank_access':False,'stage2_script':'missing.py','stage2_script_sha256':'x','calibration_gate_sha256':'x'}))
    cal=tmp_path/'cal';cal.mkdir();(cal/'status.json').write_text(json.dumps({'state':'PASS'}))
    gate={'decision':'PASS','stage':'V3_MATCHED_EVOLUTIONARY_CALIBRATION',**{x:True for x in s.PASS_FIELDS}}
    (cal/'gate.json').write_text(json.dumps(gate))
    monkeypatch.setattr(s,'CONFIG',conf);monkeypatch.setattr(s,'CAL',cal)
    assert s.inspect()[0]=='WAITING_FOR_DURABILITY'
