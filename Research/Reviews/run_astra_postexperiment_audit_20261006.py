import json, os, urllib.request, pathlib, datetime, hashlib
root=pathlib.Path("/home/ubuntu/Momentum-Trading-System_v4"); R=root/"Research/Reviews"; P=root/"Research/Protocols"; Q=root/"Research/Reports"
prompt=(R/"MTS_CLAUDE_POSTEXPERIMENT_AUDIT_PROMPT_20261006.md").read_text()
freeze=(P/"MTS_GA_REDESIGN_EXPERIMENT_FREEZE_20261005.md").read_text()
report=(Q/"MTS_GA_REDESIGN_FINAL_REPORT_20261006.md").read_text()
prior=(R/"MTS_CLAUDE_GA_REDESIGN_REVIEW_20261005_221916.md").read_text()
full=prompt+"\n\n--- CONTROLLING FREEZE ---\n"+freeze+"\n\n--- FINAL DEV117 REPORT ---\n"+report+"\n\n--- PRIOR CLAUDE DESIGN REVIEW (audit it; do not defer to it) ---\n"+prior
payload={"model":"gpt-6-astra","reasoning":{"effort":"max"},"input":[{"role":"user","content":[{"type":"input_text","text":full}]}]}
req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"},method="POST")
raw=R/"MTS_ASTRA_POSTEXPERIMENT_AUDIT_RAW_20261006.json"; out=R/"MTS_ASTRA_POSTEXPERIMENT_AUDIT_20261006.md"; meta=R/"MTS_ASTRA_POSTEXPERIMENT_AUDIT_META_20261006.json"
with urllib.request.urlopen(req,timeout=1800) as resp: body=resp.read().decode()
raw.write_text(body); obj=json.loads(body)
parts=[]
for item in obj.get("output",[]):
    if item.get("type")=="message":
        for x in item.get("content",[]):
            if x.get("type")=="output_text": parts.append(x.get("text",""))
textout="\n".join(parts); out.write_text(textout)
m={"response_id":obj.get("id"),"model":obj.get("model"),"status":obj.get("status"),"usage":obj.get("usage"),"input_sha256":hashlib.sha256(full.encode()).hexdigest(),"raw_response_file":str(raw),"verbatim_text_file":str(out),"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
meta.write_text(json.dumps(m,indent=2))
print("ASTRA_STATUS="+str(obj.get("status"))); print("ASTRA_MODEL="+str(obj.get("model"))); print("RESPONSE_ID="+str(obj.get("id"))); print("TEXT_CHARS="+str(len(textout))); print("USAGE="+json.dumps(obj.get("usage"))); print("RAW="+str(raw)); print("TEXT="+str(out)); print("META="+str(meta))
