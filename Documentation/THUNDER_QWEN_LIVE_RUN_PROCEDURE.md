# Thunder Qwen Live Run Procedure

This document records the operational launch sequence for MTS v4 live research on Thunder. It is infrastructure procedure only; it does not alter MTS scientific authority, research logic, or source code.

## 1. Enter the standalone v4 repository

```bash
cd /home/ubuntu/Momentum-Trading-System_v4
```

Before a controlled live proof, verify the intended Git revision explicitly.

## 2. Prepare the Thunder runtime environment

The vLLM virtual environment must be on `PATH` because FlashInfer may invoke helper executables such as `ninja` by name from child processes.

```bash
export PATH=/home/ubuntu/vllm-venv/bin:$PATH
```

`ninja` is installed in `/home/ubuntu/vllm-venv/bin`. It does not need to be reinstalled each Thunder session as long as the existing virtual environment persists. Reinstallation is needed only if that environment is rebuilt or replaced.

Load live-source credentials from the repository-local `.env` without printing secrets:

```bash
set -a
source .env
set +a
```

Optional non-secret preflight:

```bash
command -v vllm
command -v ninja
test -n "$UNUSUAL_WHALES_API_KEY" && echo "UW_KEY_LOADED" || echo "UW_KEY_MISSING"
```

Expected executables resolve under `/home/ubuntu/vllm-venv/bin`.

Do not commit `.env` or `.mts_rd_ai_env`.

## 3. Start Qwen

Use the approved Qwen configuration:

```bash
nohup vllm serve \
  /home/ubuntu/hf-cache/Qwen3-32B-AWQ \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 32768 \
  --reasoning-parser qwen3 \
  > /home/ubuntu/MTS_V4_QWEN_START_$(date +%Y%m%d_%H%M%S).txt 2>&1 &

echo "VLLM_PID=$!"
```

For controlled evidence runs where an exact output filename has already been assigned, use that exact filename instead of shell-generated naming.

## 4. Verify readiness before launching MTS

```bash
/home/ubuntu/vllm-venv/bin/python - <<'PY'
import time
import urllib.request

for i in range(60):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/v1/models", timeout=3) as r:
            print("QWEN_READY", r.status)
            break
    except Exception:
        if i == 59:
            print("QWEN_NOT_READY")
            raise
        time.sleep(5)
PY
```

Do not classify a live MTS test as failed if Qwen never reaches readiness. vLLM startup failures are infrastructure failures until the MTS process actually reaches the model and research loop.

## 5. Run MTS only after readiness

For large smoke-test or production outputs, redirect the complete output to a date-stamped Thunder text file. Do not dump large diagnostic output into the interactive terminal.

After completion, inspect only a short tail on Thunder if needed, then exit to macOS and copy the complete report into `~/Downloads` with `tnr scp` using the exact filename.

## 6. 2026-09-09 bounded-context live proof

Frozen candidate:

`b76611acb07cc916e0d286815150e64e42c32f3e`

The resumed AAPL campaign began from 8 RD decisions and 4 analyses, reacquired six live evidence sources, and progressed to 28 decisions and 20 analyses without reproducing the prior Qwen 32,768-token context overflow.

The campaign returned with `closed=False` because the orchestrator had reached its `max_analyses` execution budget. `ResearchLoopOrchestrator.run()` returns an open outcome with close reason `ANALYSIS_BUDGET_EXHAUSTED` whenever `analyses >= max_analyses`; it does not treat that deterministic execution budget as scientific closure. The checkpoint therefore correctly remained active for later resume.

Result for the defect under test:

**LIVE CONTEXT-OVERFLOW REPAIR: PASS**

The execution budget is an operational bound, not a scientific conclusion. RD retains authority to determine whether research should continue or close scientifically.
