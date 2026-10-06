"""Fail-closed external-data and sandbox certification checks."""
from pathlib import Path
import hashlib,shutil,subprocess
OFR_REL=Path("Research/Data/CrashCausalPackV1/ofr_fsi_raw_20261004.csv")
OFR_SHA="ad4de65362098ebace4077bdf598ef4d3f389f99ddcf9580173456ee36320b69"

def file_sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def ofr_available(repo:Path)->bool:
    p=repo/OFR_REL
    return p.is_file() and file_sha(p)==OFR_SHA

def pit_sector_registry(repo:Path):
    # Only an explicit effective-dated registry is acceptable; current GICS is forbidden historically.
    candidates=[repo/"Research/Data/PIT/sector_taxonomy_effective_dated.parquet",
                repo/"Research/Data/PIT/sector_taxonomy_effective_dated.csv"]
    return next((p for p in candidates if p.is_file()),None)

def earnings_registry(repo:Path):
    candidates=[repo/"Research/Data/PIT/earnings_events_published.parquet",
                repo/"Research/Data/PIT/earnings_events_published.csv"]
    return next((p for p in candidates if p.is_file()),None)

def contextual_layer_policy_compliant(repo:Path)->bool:
    """Frozen 2026-10-05 design permits PIT formal taxonomy, dynamic peers, both, or neither.
    If no effective-dated taxonomy exists, formal taxonomy must stay disabled; current GICS
    may never be projected backward. Dynamic peers are first-class causal context.
    """
    if pit_sector_registry(repo) is not None:return True
    feature_path=repo/"Core/conforming_ga/features.py"
    if not feature_path.is_file():return False
    src=feature_path.read_text().lower()
    return "trailing_peer_context" in src and "gics" not in src

def os_sandbox_available()->bool:
    # Prefer unprivileged Landlock: it works without user namespaces/root.
    try:
        from .sandbox import abi_version
        if abi_version()>=1:return True
    except Exception:
        pass
    if shutil.which("bwrap") or shutil.which("firejail"):return True
    if shutil.which("unshare"):
        try:
            p=subprocess.run(["unshare","--user","--map-root-user","true"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=3)
            return p.returncode==0
        except Exception:return False
    return False
