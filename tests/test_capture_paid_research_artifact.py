from __future__ import annotations
import hashlib, sqlite3, subprocess, sys
from pathlib import Path
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "capture_paid_research_artifact.py"
def run_capture(source, primary, backup):
    return subprocess.run([sys.executable,str(SCRIPT),"--source",str(source),"--primary-root",str(primary),"--backup-root",str(backup)],text=True,capture_output=True)
def test_dual_copy_hash_manifest_and_idempotence(tmp_path):
    source=tmp_path/"RP-XOM-TEST.json"; payload=b'{"paid":"research","n":1}\n'; source.write_bytes(payload)
    primary=tmp_path/"primary"; backup=tmp_path/"backup"; digest=hashlib.sha256(payload).hexdigest()
    first=run_capture(source,primary,backup); assert first.returncode==0, first.stderr; assert "DURABLE_VERIFIED" in first.stdout; assert f"sha256={digest}" in first.stdout
    rel=Path("objects")/"paid_research"/digest[:2]/f"{digest}.json"
    assert (primary/rel).read_bytes()==payload; assert (backup/rel).read_bytes()==payload
    for root in (primary,backup):
        with sqlite3.connect(root/"catalog"/"durability_manifest.sqlite3") as conn: row=conn.execute("SELECT source_sha256, source_size FROM paid_artifact_captures").fetchone()
        assert row==(digest,len(payload))
    second=run_capture(source,primary,backup); assert second.returncode==0, second.stderr; assert "DURABLE_VERIFIED" in second.stdout
def test_rejects_nested_backup(tmp_path):
    source=tmp_path/"x.json"; source.write_text("{}",encoding="utf-8"); primary=tmp_path/"store"
    result=run_capture(source,primary,primary/"backup"); assert result.returncode!=0; assert "must be independent" in (result.stdout+result.stderr)
def test_fails_on_corrupt_existing_backup(tmp_path):
    source=tmp_path/"x.json"; payload=b'{"x":1}'; source.write_bytes(payload); primary=tmp_path/"primary"; backup=tmp_path/"backup"; digest=hashlib.sha256(payload).hexdigest(); rel=Path("objects")/"paid_research"/digest[:2]/f"{digest}.json"
    (backup/rel).parent.mkdir(parents=True); (backup/rel).write_bytes(b"corrupt")
    result=run_capture(source,primary,backup); assert result.returncode!=0; assert "collision/corruption" in (result.stdout+result.stderr)
def test_rejects_git_root(tmp_path):
    source=tmp_path/"x.json"; source.write_text("{}",encoding="utf-8"); primary=tmp_path/"repo"/"nexus"; (tmp_path/"repo"/".git").mkdir(parents=True); backup=tmp_path/"backup"
    result=run_capture(source,primary,backup); assert result.returncode!=0; assert "inside Git working tree" in (result.stdout+result.stderr)
