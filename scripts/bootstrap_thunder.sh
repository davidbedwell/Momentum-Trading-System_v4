#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo " MTS V4 — THUNDER BOOTSTRAP"
echo "============================================================"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

echo
echo "=== SYSTEM PACKAGES ==="

sudo apt-get update
sudo apt-get install -y \
    git \
    gh \
    python3 \
    python3-pip \
    python3-venv

echo
echo "=== SYSTEM VERSIONS ==="
python3 --version
git --version
gh --version | head -n 1

python3 - <<'PYCHECK'
import sys

if sys.version_info < (3, 11):
    raise SystemExit(
        f"Python 3.11+ is required; found "
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

print(
    f"Python version check: PASS "
    f"({sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})"
)
PYCHECK

echo
echo "=== PYTHON VIRTUAL ENVIRONMENT ==="

if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
    echo "Created .venv"
else
    echo ".venv already exists"
fi

source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

echo
echo "=== INSTALL MTS V4 + DEVELOPMENT DEPENDENCIES ==="
python -m pip install -e ".[dev]"

echo
echo "=== VERIFY REQUIRED PYTHON PACKAGES ==="

python - <<'PY'
import importlib

required = [
    "numpy",
    "scipy",
    "yfinance",
    "pyarrow",
    "pandas",
    "pytest",
    "jsonschema",
]

failed = []

for name in required:
    try:
        module = importlib.import_module(name)
        version = getattr(module, "__version__", "version unavailable")
        print(f"{name}: PASS ({version})")
    except Exception as exc:
        print(f"{name}: FAIL ({exc})")
        failed.append(name)

if failed:
    raise SystemExit(
        "Bootstrap verification failed for: " + ", ".join(failed)
    )
PY

echo
echo "=== VERIFY MTS RUNTIME IMPORTS ==="

python - <<'PY'
from Core.deterministic_computation import execute_computations
from MTS_V4.discovery_methods import discovery_method_catalog
from MTS_V4.live_sources import YFinanceDailyOhlcvSource

assert callable(execute_computations)
assert discovery_method_catalog().all()
print("Core.deterministic_computation: PASS")
print("MTS_V4.discovery_methods: PASS")
print("YFinanceDailyOhlcvSource: PASS")
PY

echo
echo "=== GITHUB AUTH STATUS ==="

if gh auth status >/dev/null 2>&1; then
    echo "GitHub authentication: PASS"

    git config --global credential."https://github.com".helper "!gh auth git-credential"
    git config --global credential."https://gist.github.com".helper "!gh auth git-credential"

    echo "GitHub HTTPS credential helper: configured"
else
    echo "GitHub authentication: NOT CONFIGURED"
    echo "Run: gh auth login --web"
    echo "Then rerun this bootstrap script."
fi

echo
echo "============================================================"
echo " THUNDER BOOTSTRAP COMPLETE"
echo "============================================================"
