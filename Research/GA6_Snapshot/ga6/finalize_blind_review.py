import pathlib,json,hashlib,zipfile
p=pathlib.Path('/opt/mts/ga6/runs/independent_review')
files=sorted(p.glob('*.parquet'))+[p/'REVIEW_BRIEF.txt']
manifest={'review':'blind independent','files':[{'name':x.name,'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in files]}
(p/'MANIFEST.json').write_text(json.dumps(manifest,indent=2))
z=p/'GA6_BLIND_REVIEW.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=2) as out:
 for x in files+[p/'MANIFEST.json']:out.write(x,x.name)
print('ZIP',z,'SIZE',z.stat().st_size,'FILES',len(files)+1)
