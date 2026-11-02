"""Validate archived evidence and request without network or experiment execution."""
from pathlib import Path
import json,hashlib,ast
O=Path(__file__).resolve().parent;B=O.parent
manifest=json.loads((O/'source_manifest.json').read_text());checks=[]
for e in manifest:
 for p in (B/e['path'],O/'evidence'/e['path']):
  raw=p.read_bytes();assert len(raw)==e['bytes'] and hashlib.sha256(raw).hexdigest()==e['sha256'],str(p)
checks.append('All source and archived evidence bytes/SHA256 match')
for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
checks.append('Package/submission/validation Python syntax valid; no code executed by this check')
request=json.loads((O/'request.json').read_text());assert request['model']=='anthropic/claude-sonnet-4.6';assert request['messages'][1]['content']==(O/'package.md').read_text()
assert not any('authorization' in k.lower() for k in request)
checks.append('Exact requested model; request content equals package; no Authorization field stored')
meta=json.loads((O/'submission_metadata.json').read_text());response=json.loads((O/'response.json').read_text())
result={'local_artifacts_valid':True,'manifest_entries':len(manifest),'checks':checks,'package_bytes':(O/'package.md').stat().st_size,'package_sha256':hashlib.sha256((O/'package.md').read_bytes()).hexdigest(),'request_file_sha256':hashlib.sha256((O/'request.json').read_bytes()).hexdigest(),'http_200_verified':meta.get('http_status')==200,'provider_response_verified':meta.get('provider_response_verified',False),'external_review_obtained':not response.get('local_failure',False) and meta.get('provider_response_verified',False),'status':meta['status'],'no_experiment_or_test_replays':True}
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
