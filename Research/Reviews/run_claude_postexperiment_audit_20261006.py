import json,os,urllib.request,pathlib,datetime,hashlib
root=pathlib.Path("/home/ubuntu/Momentum-Trading-System_v4"); R=root/"Research/Reviews"; P=root/"Research/Protocols"; Q=root/"Research/Reports"
prompt=(R/"MTS_CLAUDE_POSTEXPERIMENT_AUDIT_PROMPT_20261006.md").read_text(); freeze=(P/"MTS_GA_REDESIGN_EXPERIMENT_FREEZE_20261005.md").read_text(); report=(Q/"MTS_GA_REDESIGN_FINAL_REPORT_20261006.md").read_text(); prior=(R/"MTS_CLAUDE_GA_REDESIGN_REVIEW_20261005_221916.md").read_text()
full=prompt+"\n\n--- CONTROLLING FREEZE ---\n"+freeze+"\n\n--- FINAL DEV117 REPORT ---\n"+report+"\n\n--- YOUR PRIOR REVIEW (for self-audit) ---\n"+prior
payload={"model":"anthropic/claude-opus-5.5","messages":[{"role":"user","content":full}],"max_tokens":48000,"reasoning":{"effort":"max"}}
req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+os.environ["OPENROUTER_API_KEY"],"Content-Type":"application/json"},method="POST")
raw=R/"MTS_CLAUDE_POSTEXPERIMENT_AUDIT_RAW_20261006.json"; out=R/"MTS_CLAUDE_POSTEXPERIMENT_AUDIT_20261006.md"; meta=R/"MTS_CLAUDE_POSTEXPERIMENT_AUDIT_META_20261006.json"
with urllib.request.urlopen(req,timeout=1800) as resp: body=resp.read().decode()
raw.write_text(body); obj=json.loads(body); text=(obj.get("choices") or [{}])[0].get("message",{}).get("content","") or ""
if not text:
 parts=[]
 for item in obj.get("output",[]):
  if item.get("type")=="message":
   for c in item.get("content",[]):
    if c.get("type")=="output_text": parts.append(c.get("text",""))
 text="\n".join(parts)
out.write_text(text); meta.write_text(json.dumps({"id":obj.get("id"),"model":obj.get("model"),"usage":obj.get("usage"),"prompt_sha256":hashlib.sha256(full.encode()).hexdigest(),"chars":len(text),"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
print("MODEL="+str(obj.get("model"))); print("ID="+str(obj.get("id"))); print("CHARS="+str(len(text))); print("USAGE="+json.dumps(obj.get("usage"))); print("OUT="+str(out))