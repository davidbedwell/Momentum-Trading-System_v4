import os, json, urllib.request, datetime
from pathlib import Path
root=Path("/home/ubuntu/Momentum-Trading-System_v4")
packet_path=root/"Research/Reviews/MTS_ASTRA_GA_REDESIGN_REVIEW_PACKET_2026-10-05.md"
outdir=root/"Research/Reviews"
env_path=Path.home()/".openrouter_api_env"
for line in env_path.read_text().splitlines():
    s=line.strip()
    if not s or s.startswith("#"): continue
    if s.startswith("export "): s=s[7:].strip()
    if "=" in s:
        k,v=s.split("=",1)
        os.environ[k.strip()]=v.strip().strip('"').strip("'")
key=os.environ.get("OPENROUTER_API_KEY")
if not key: raise SystemExit("OPENROUTER_API_KEY_NOT_FOUND")
instruction="""Perform the independent MTS GA redesign review requested in the attached packet. Treat the packet's governance as authoritative. Do not weaken, simplify, reinterpret, or expose protected DV25/A25/A75/B100 evidence. Audit approved design versus executed implementation, separate research-design defects from implementation defects and disappointing results, and produce the complete implementable GA instruction set requested in Sections A-M. Finish with the requested GA IMPLEMENTATION DIRECTIVE distinguishing MUST / MAY / MUST NOT. Do not ask follow-up questions; make the strongest review supported by the packet."""
packet=packet_path.read_text()
prompt=instruction+"\n\n--- BEGIN VERIFIED REVIEW PACKET ---\n"+packet+"\n--- END VERIFIED REVIEW PACKET ---"
model="anthropic/claude-opus-5.5"
payload={"model":model,"messages":[{"role":"user","content":prompt}],"reasoning":{"effort":"high"}}
req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json","X-Title":"MTS GA Independent Review"},method="POST")
stamp=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
raw_path=outdir/f"MTS_CLAUDE_GA_REDESIGN_RAW_{stamp}.json"
review_path=outdir/f"MTS_CLAUDE_GA_REDESIGN_REVIEW_{stamp}.md"
meta_path=outdir/f"MTS_CLAUDE_GA_REDESIGN_METADATA_{stamp}.json"
with urllib.request.urlopen(req,timeout=1800) as resp: raw=resp.read()
raw_path.write_bytes(raw)
obj=json.loads(raw)
content=obj["choices"][0]["message"]["content"]
review_path.write_text(content)
meta={"requested_model":model,"returned_model":obj.get("model"),"id":obj.get("id"),"created":obj.get("created"),"usage":obj.get("usage"),"raw_path":str(raw_path),"review_path":str(review_path),"packet_sha256":"53728fccdd583b6b7c2f9271fd5fc60726f97cf799395edc456d386a3ad45857"}
meta_path.write_text(json.dumps(meta,indent=2))
print("CLAUDE_REVIEW_COMPLETE")
print("RETURNED_MODEL="+str(obj.get("model")))
print("RAW="+str(raw_path))
print("REVIEW="+str(review_path))
print("META="+str(meta_path))
print("USAGE="+json.dumps(obj.get("usage")))
