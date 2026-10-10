"""Certified-domain mutation, trade-signal similarity, and durable JSONL journal primitives."""
import hashlib,json,os,pathlib,tempfile
import numpy as np

def domain_catalog():
 from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces
 return {fam:{g.gene_id:tuple(g.values) for g in space.genes} for fam,space in stage2_search_spaces().items()}

def validate_genes(genes,catalog):
 if not genes or len({f for f,_ in genes})!=len(genes):return False
 for family,gene in genes:
  schema=catalog.get(family)
  if schema is None or set(gene)!=set(schema):return False
  if any(not any(type(v)==type(allowed) and v==allowed for allowed in domain) for key,v in gene.items() for domain in [schema[key]]):return False
 return True

def domain_mutate(genes,rng,catalog):
 genes=json.loads(json.dumps(genes))
 candidates=[(i,key,tuple(v for v in values if not(type(v)==type(g[key]) and v==g[key])))
             for i,(family,g) in enumerate(genes) for key,values in catalog[family].items() if key in g]
 candidates=[x for x in candidates if x[2]]
 if not candidates:return genes
 i,key,values=rng.choice(candidates);genes[i][1][key]=rng.choice(values)
 assert validate_genes(genes,catalog)
 return genes

def packed_signal(mask):
 mask=np.asarray(mask,dtype=np.bool_)
 return {'size':int(mask.size),'count':int(mask.sum()),'bits':np.packbits(mask).tobytes().hex()}

def overlap(a,b):
 if a['size']!=b['size']:raise ValueError('Different observation universes')
 x=np.unpackbits(np.frombuffer(bytes.fromhex(a['bits']),dtype=np.uint8))[:a['size']].astype(bool)
 y=np.unpackbits(np.frombuffer(bytes.fromhex(b['bits']),dtype=np.uint8))[:b['size']].astype(bool)
 union=np.count_nonzero(x|y)
 return float(np.count_nonzero(x&y)/union) if union else 1.0

def atomic_json(path,obj):
 path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=str(path.parent))
 try:
  with os.fdopen(fd,'w') as f:
   json.dump(obj,f,allow_nan=True);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
  dirfd=os.open(path.parent,os.O_RDONLY)
  try:os.fsync(dirfd)
  finally:os.close(dirfd)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def recover_jsonl(path):
 path=pathlib.Path(path)
 if not path.exists():return []
 rows=[];end=0
 with path.open('rb+') as f:
  while True:
   raw=f.readline()
   if not raw:break
   if not raw.endswith(b'\n'):break
   try:rows.append(json.loads(raw));end=f.tell()
   except (ValueError,UnicodeError):break
  f.truncate(end);f.flush();os.fsync(f.fileno())
 return rows

def durable_append(path,rows):
 path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('ab') as f:
  for row in rows:f.write((json.dumps(row,allow_nan=True)+'\n').encode())
  f.flush();os.fsync(f.fileno())
