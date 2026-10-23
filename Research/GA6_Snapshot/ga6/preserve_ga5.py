from pathlib import Path
import json,hashlib,os,datetime
root=Path('/opt/mts/ga5_redesign')
out=Path('/opt/mts/ga5_preservation_20261021')
out.mkdir(exist_ok=True)
runs=[]
for p in root.rglob('all_evaluations.jsonl'):
    runs.append(p)
print('runs',[(str(p),p.stat().st_size) for p in runs],flush=True)
for ledger in runs:
    label=ledger.parent.name
    dest=out/label
    dest.mkdir(exist_ok=True)
    definitions={}
    count=0
    bad=0
    with ledger.open() as fh:
        for line in fh:
            try:
                rec=json.loads(line)
                g=rec.get('genome')
                cid=rec.get('chromosome_id')
                if g and cid:
                    if cid in definitions and definitions[cid]!=g:raise ValueError('Conflicting genome '+cid)
                    definitions[cid]=g
                count+=1
            except (json.JSONDecodeError,ValueError) as exc:
                bad+=1
                if not line.endswith('\n'):continue
                raise
    target=dest/'chromosome_definitions.jsonl'
    tmp=target.with_suffix('.tmp')
    with tmp.open('w') as fh:
        for cid in sorted(definitions):
            fh.write(json.dumps({'chromosome_id':cid,'genome':definitions[cid]},sort_keys=True)+'\n')
    os.replace(tmp,target)
    manifest={'source':str(ledger),'evaluations':count,'unique_definitions':len(definitions),'malformed_or_partial':bad,'definitions_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'ledger_sha256':hashlib.sha256(ledger.read_bytes()).hexdigest(),'checkpoint':str(ledger.parent/'checkpoint_unified.json'),'results_preserved_in_original_ledger':True,'complete_run_report_exists':(ledger.parent/'report.json').exists()}
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({'run':label,'evaluations':count,'unique_definitions':len(definitions),'bad':bad,'report':manifest['complete_run_report_exists']}),flush=True)
