"""No-compute end-to-end conveyor tests: 0/1 prerequisites, 2-10 handoffs, restart."""
import json
import sys
from pathlib import Path
from Core.layered_ga import conveyor


def _gate(root, i, decision="PASS"):
    p = root / conveyor.STAGE_DIRS[i] / "gate.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"decision": decision}))


def _configure(tmp_path, monkeypatch):
    monkeypatch.setattr(conveyor, "RUN", tmp_path)
    monkeypatch.setattr(conveyor, "STATE", tmp_path / "conveyor_state.json")
    runners = {}
    for i in range(2, 11):
        runner = tmp_path / f"runner_{i}.py"
        runner.write_text(
            "import json, pathlib, sys\n"
            "root=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path(__file__).parent\n"
            f"i={i}\n"
            "log=root/'calls.txt'\n"
            "with log.open('a') as f:f.write(str(i)+'\\n')\n"
            "p=root/'fail_once.txt'\n"
            "if p.exists() and p.read_text().strip()==str(i):\n"
            " p.unlink();sys.exit(7)\n"
            f"g=root/{conveyor.STAGE_DIRS[i]!r}/'gate.json'\n"
            "g.parent.mkdir(parents=True,exist_ok=True)\n"
            "g.write_text(json.dumps({'decision':'PASS'}))\n"
        )
        runners[i] = runner
    monkeypatch.setattr(conveyor, "RUNNERS", runners)
    _gate(tmp_path, 0)
    _gate(tmp_path, 1)


def test_all_ten_stage_handoffs(tmp_path, monkeypatch):
    _configure(tmp_path, monkeypatch)
    assert conveyor.main() == 0
    assert (tmp_path / "calls.txt").read_text().splitlines() == [str(i) for i in range(2, 11)]
    assert json.loads((tmp_path / "conveyor_state.json").read_text())["status"] == "COMPLETE"
    assert conveyor.main() == 0
    assert len((tmp_path / "calls.txt").read_text().splitlines()) == 9


def test_restart_after_interruption(tmp_path, monkeypatch):
    _configure(tmp_path, monkeypatch)
    (tmp_path / "fail_once.txt").write_text("6")
    assert conveyor.main() == 7
    assert json.loads((tmp_path / "conveyor_state.json").read_text())["status"] == "STOPPED_ENGINEERING"
    assert conveyor.main() == 0
    assert (tmp_path / "calls.txt").read_text().splitlines() == [
        "2", "3", "4", "5", "6", "6", "7", "8", "9", "10"
    ]


def test_scientific_failure_does_not_advance(tmp_path, monkeypatch):
    _configure(tmp_path, monkeypatch)
    _gate(tmp_path, 4, "FAIL")
    # Stage 4's runner is not invoked because the gate exists but is not PASS;
    # its runner may recompute the gate. Test failure returned by a runner instead.
    runner = tmp_path / "runner_4.py"
    runner.write_text("import pathlib,json\np=pathlib.Path(__file__).parent/'stage4-entry-mae-20261007/gate.json'\np.parent.mkdir(exist_ok=True)\np.write_text(json.dumps({'decision':'FAIL'}))\n")
    assert conveyor.main() == 30
    assert (tmp_path / "calls.txt").read_text().splitlines() == ["2", "3"]
    assert json.loads((tmp_path / "conveyor_state.json").read_text())["status"] == "STOPPED_SCIENTIFIC"
