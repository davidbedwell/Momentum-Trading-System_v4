from pathlib import Path
import json,hashlib,csv,re,collections
O=Path(__file__).resolve().parent;B=O.parent
manifest=json.loads((O/'source_manifest.json').read_text())
for x in manifest:assert hashlib.sha256((B/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
req=json.loads((O/'request.json').read_text());content=req['messages'][1]['content'];assert content==(O/'package.md').read_text()
blocks=[json.loads(x) for x in re.findall(r'### Structured numerical evidence\n```json\n(.*?)\n```',content,re.S)];assert len(blocks)==5
checks=0
for block,inv in zip(blocks,json.loads((O/'package_inventory.json').read_text())):
 directory=B/inv['directory']
 for m in block['exact_aggregate_matrices']:
  for suffix,key in [('ev','latent_ev_5x6'),('realized','realized_return_5x6')]:
   variant='' if m['variant']=='primary' else '_'+m['variant']
   path=directory/('confusion_aggregate_'+m['scenario']+variant+'_'+suffix+'.csv')
   rows=list(csv.reader(path.open()));matrix=[[int(v) for v in row[1:]] for row in rows[1:]]
   assert matrix==m[key],str(path)
   assert sum(map(sum,matrix))==m['n_opportunities']
   checks+=1
assert not re.search(r'sk-or-[A-Za-z0-9_-]+',json.dumps(req))
result={'passed':True,'five_reports':len(blocks),'source_hashes_checked':len(manifest),'exact_aggregate_csv_matrices_checked':checks,'package_bytes':len(content.encode()),'authorization_header_in_request':False,'submission_status':json.loads((O/'submission_metadata.json').read_text())['status']}
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
