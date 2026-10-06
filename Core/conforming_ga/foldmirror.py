"""Build physically disjoint fold mirrors for kernel sandbox execution."""
from pathlib import Path
import os,shutil,hashlib
from .realdata import load_fold,RAW_ROOT
def build_fold_mirrors(repo:Path,root:Path):
    for f in range(4):
        tr,bl=load_fold(repo,f)
        for mode,tickers in (("train",tr),("blind",bl)):
            dest=root/f"fold{f}"/mode;dest.mkdir(parents=True,exist_ok=True)
            for old in dest.glob("*.parquet"):old.unlink()
            for t in tickers:
                src=RAW_ROOT/f"{t}.parquet"; out=dest/f"{t}.parquet"
                try:os.link(src,out)
                except OSError:shutil.copy2(src,out)
            got={x.stem for x in dest.glob("*.parquet")}
            if got!=set(tickers):raise RuntimeError((f,mode,len(got)))
    return root
