import subprocess,sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
def test_pf10_landlock_train_can_read_blind_kernel_denied():
    code=r'''
from pathlib import Path
from Core.conforming_ga.foldworker import enter_fold_sandbox
repo=Path(".").resolve();root=Path("/home/ubuntu/mts-ga-fold-mirrors-20261006")
blind=next((root/"fold0"/"blind").glob("*.parquet"))
train=enter_fold_sandbox(repo,root,0,"train")
assert len(list(train.glob("*.parquet")))==80
try:
    blind.read_bytes()
    raise SystemExit(9)
except PermissionError:
    pass
'''
    p=subprocess.run([str(REPO/".venv/bin/python"),"-c",code],cwd=REPO)
    assert p.returncode==0
