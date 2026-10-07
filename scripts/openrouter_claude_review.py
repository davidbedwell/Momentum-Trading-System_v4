#!/usr/bin/env python3
from pathlib import Path
import json, urllib.request, urllib.error, time, sys

ROOT = Path("/home/ubuntu/MTS_G3_specialist_design")
ENV = Path.home() / ".config/mts/openrouter.env"
PROMPT = ROOT / "Research/G3/MTS_G3_CLAUDE_V2_FAILURE_REVIEW_PROMPT_20261007.txt"
OUT = ROOT / "Research/G3/MTS_G3_CLAUDE_V2_FAILURE_REVIEW_RAW_20261007.json"

def main():
    vals = {}
    for line in ENV.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip("'").strip('"')
    key = vals.get("OPENROUTER_API_KEY", "")
    if not key:
        raise SystemExit("ERROR missing OPENROUTER_API_KEY")
    payload = {
        "model": "anthropic/claude-opus-4.6",
        "messages": [{"role": "user", "content": PROMPT.read_text()}]
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = resp.read()
            OUT.write_bytes(data)
            obj = json.loads(data)
            print("HTTP", resp.status)
            print("SECONDS", round(time.time()-t0, 2))
            print("BYTES", len(data))
            print("MODEL", obj.get("model"))
            print("HAS_RESPONSE", bool(obj.get("choices")))
    except urllib.error.HTTPError as e:
        print("HTTP_ERROR", e.code)
        try:
            obj = json.loads(e.read().decode())
            print("ERROR", str(obj.get("error", {}).get("message", ""))[:500])
        except Exception:
            pass
        sys.exit(2)

if __name__ == "__main__":
    main()
