"""Kernel-sandboxed fold worker bootstrap."""
from __future__ import annotations
from pathlib import Path
from .sandbox import restrict_reads
def enter_fold_sandbox(repo:Path,fold_root:Path,fold:int,mode:str):
    data=(fold_root/f"fold{fold}"/mode).resolve()
    allowed=[
      data,
      (repo/"Core").resolve(),
      (repo/"Research/Data/Comparators").resolve(),
      (repo/"Research/Data/SAFE").resolve(),
      (repo/"Research/Data/CrashCausalPackV1").resolve(),
      (repo/".venv").resolve(),
      Path("/usr"),Path("/lib"),Path("/lib64"),Path("/etc"),Path("/dev"),Path("/proc"),Path("/tmp"),
    ]
    pit=repo/"Research/Data/PIT"
    if pit.exists():allowed.append(pit.resolve())
    restrict_reads([x for x in allowed if x.exists()])
    return data
