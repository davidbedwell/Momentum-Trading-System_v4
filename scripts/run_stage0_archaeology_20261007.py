from pathlib import Path
import hashlib,json,re,subprocess,datetime
SRC=Path('/home/ubuntu/Momentum-Trading-System_v4')
ROOTS=[SRC,Path('/home/ubuntu/mts-v4-recovered-oct2'),Path('/home/ubuntu/mts-v4-recovery-integration-20261004'),Path('/home/ubuntu/research_restore_20261004')]
OUT=Path('Research/Runs/layered/stage0-ga0-archaeology-20261007'); OUT.mkdir(parents=True,exist_ok=True)
terms=re.compile(r'(genome|chromosome|crossover|mutat|pareto|cagr|drawdown|open_state_response|causal_wealth|cross_sectional_ga)',re.I)
rows=[]
for root in ROOTS:
 if not root.exists(): continue
 for p in root.rglob('*'):
  if not p.is_file() or p.suffix.lower() not in {'.py','.json','.md','.log','.txt'}: continue
  try:
   if p.stat().st_size>8_000_000: continue
   b=p.read_bytes()
   if terms.search(b.decode('utf-8','ignore')):
    rows.append({'path':str(p),'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'mtime':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()})
  except Exception: pass
# exact duplicate groups and priority candidates
byhash={}
for r in rows: byhash.setdefault(r['sha256'],[]).append(r['path'])
priority=[r for r in rows if re.search(r'(open_state_response|causal_wealth|cross_sectional_ga|allocation_architecture|early_recovery)',r['path'],re.I)]
report={'stage':'STAGE0','mode':'READ_ONLY_ARCHAEOLOGY','source_head':subprocess.check_output(['git','-C',str(SRC),'rev-parse','HEAD'],text=True).strip(),'evidence_files':len(rows),'priority_files':priority,'duplicate_groups':[v for v in byhash.values() if len(v)>1]}
(OUT/'evidence_inventory.json').write_text(json.dumps(report,indent=2))
# extract semantic identifiers without claiming certification
patterns=[r'class\s+(\w*(?:Genome|Chromosome)\w*)',r'def\s+(mutate\w*|crossover\w*|evaluate\w*)',r'family_signal\s*\([^)]*?["\']([^"\']+)']
hits={}
for r in priority:
 p=Path(r['path'])
 try: t=p.read_text(errors='ignore')
 except: continue
 vals=[]
 for pat in patterns:
  vals += re.findall(pat,t,re.I)
 if vals: hits[str(p)]=sorted(set(v if isinstance(v,str) else str(v) for v in vals))
(OUT/'semantic_hits.json').write_text(json.dumps(hits,indent=2))
status={'decision':'AMBIGUOUS','reason':'Certification requires provenance review of recovered candidates; inventory complete but no semantic claim is auto-certified.','evidence_files':len(rows),'priority_files':len(priority)}
(OUT/'gate.json').write_text(json.dumps(status,indent=2))
print(json.dumps({'out':str(OUT),'evidence_files':len(rows),'priority_files':len(priority),'semantic_files':len(hits)},indent=2))
