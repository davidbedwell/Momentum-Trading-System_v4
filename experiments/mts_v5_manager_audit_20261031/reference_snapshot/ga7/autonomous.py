"""Resumable server-owned GA7 task orchestrator.

Usage:
 python -m ga7.autonomous --plan /path/to/ga7-plan.json --output /path/to/output
The plan explicitly specifies commands for each audited stage. No shell interpretation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

STAGES = ("preflight", "parity", "benchmark24", "benchmark32", "benchmark40", "select_universe",
          "evolution", "transport_excluded", "transport_dev79", "final_report", "backup_verify")

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def atomic_json(path, payload):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    os.replace(temp, path)

def utc():
    return datetime.now(timezone.utc).isoformat()

def run(plan_path, output):
    plan_path = Path(plan_path).resolve()
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    plan = json.loads(plan_path.read_text())
    if tuple(plan.get("stages", {})) != STAGES:
        raise ValueError("All stages must be present in canonical order")
    if not plan.get("inputs"):
        raise ValueError("Input manifest required")
    inputs = {name: digest(Path(path)) for name, path in plan["inputs"].items()}
    fingerprint = hashlib.sha256(json.dumps({"plan": plan, "inputs": inputs}, sort_keys=True).encode()).hexdigest()
    state_file = output / "orchestration_state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {"fingerprint": fingerprint, "stages": {}}
    if state["fingerprint"] != fingerprint:
        raise ValueError("Plan or input changed since checkpoint")
    for stage in STAGES:
        if state["stages"].get(stage, {}).get("status") == "complete":
            for artifact, old_digest in state["stages"][stage]["outputs"].items():
                if not Path(artifact).is_file() or digest(artifact) != old_digest:
                    raise ValueError("Checkpoint artifact mismatch: " + artifact)
            continue
        spec = plan["stages"][stage]
        command = spec.get("argv")
        artifacts = spec.get("outputs")
        if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
            raise ValueError("Stage must have explicit argv: " + stage)
        if not isinstance(artifacts, list) or not artifacts:
            raise ValueError("Stage must declare output artifacts: " + stage)
        log = output / (stage + ".log")
        state["stages"][stage] = {"status": "running", "started_utc": utc()}
        atomic_json(state_file, state)
        with log.open("a") as stream:
            completed = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=False)
        if completed.returncode:
            state["stages"][stage] = {"status": "failed", "exit_code": completed.returncode, "ended_utc": utc()}
            atomic_json(state_file, state)
            raise RuntimeError("Stage failed: " + stage + "; inspect " + str(log))
        outputs = {}
        for artifact in artifacts:
            path = Path(artifact).resolve()
            if not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError("Stage output missing or empty: " + str(path))
            outputs[str(path)] = digest(path)
        state["stages"][stage] = {"status": "complete", "ended_utc": utc(), "outputs": outputs}
        atomic_json(state_file, state)
    atomic_json(output / "pipeline_complete.json", {"fingerprint": fingerprint, "completed_utc": utc(), "stages": STAGES, "inputs": inputs})

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    run(a.plan, a.output)

if __name__ == "__main__":
    main()
