import json, os, urllib.request, pathlib, datetime
root=pathlib.Path("/home/ubuntu/Momentum-Trading-System_v4")
packet_path=root/"Research/Reviews/MTS_ASTRA_GA_REDESIGN_REVIEW_PACKET_2026-10-05.md"
out_dir=root/"Research/Reviews"
raw_path=out_dir/"MTS_CLAUDE_OPUS_GA_REDESIGN_REVIEW_RAW_2026-10-05.json"
text_path=out_dir/"MTS_CLAUDE_OPUS_GA_REDESIGN_REVIEW_2026-10-05.md"
meta_path=out_dir/"MTS_CLAUDE_OPUS_GA_REDESIGN_REVIEW_META_2026-10-05.json"
packet=packet_path.read_text()
instruction="""Perform the independent MTS GA redesign review requested in the attached packet. Treat the packet's governance as authoritative. Do not weaken, simplify, reinterpret, or expose protected DV25/A25/A75/B100 evidence. Audit approved design versus executed implementation, separate research-design defects from implementation defects and disappointing results, and produce the complete implementable GA instruction set requested in Sections A-M. Finish with the requested GA IMPLEMENTATION DIRECTIVE distinguishing MUST / MAY / MUST NOT. Do not ask follow-up questions; make the strongest review supported by the packet."""
payload={"model":"anthropic/claude-opus-5.5","messages":[{"role":"user","content":instruction+"\n\n--- BEGIN VERIFIED REVIEW PACKET ---\n"+packet+"\n--- END VERIFIED REVIEW PACKET ---"}],"max_tokens":32000,"reasoning":{"effort":"max"}}
req=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+os.environ["OPENROUTER_API_KEY"],"Content-Type":"application/json"},method="POST")
with urllib.request.urlopen(req,timeout=1800) as resp:
    body=resp.read().decode()
raw_path.write_text(body)
obj=json.loads(body)
parts=[]
for item in obj.get("output",[]):
    if item.get("type")=="message":
        for c in item.get("content",[]):
            if c.get("type")=="output_text": parts.append(c.get("text",""))
text="\n".join(parts)
text_path.write_text(text)
meta={"response_id":obj.get("id"),"model":obj.get("model"),"status":obj.get("status"),"usage":obj.get("usage"),"packet_bytes":packet_path.stat().st_size,"packet_sha256":"53728fccdd583b6b7c2f9271fd5fc60726f97cf799395edc456d386a3ad45857","raw_response_file":str(raw_path),"verbatim_text_file":str(text_path),"created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
meta_path.write_text(json.dumps(meta,indent=2))
print("CLAUDE_STATUS="+str(obj.get("status")))
print("CLAUDE_MODEL="+str(obj.get("model")))
print("RESPONSE_ID="+str(obj.get("id")))
print("TEXT_CHARS="+str(len(text)))
print("USAGE="+json.dumps(obj.get("usage")))
print("RAW="+str(raw_path))
print("TEXT="+str(text_path))
print("META="+str(meta_path))
