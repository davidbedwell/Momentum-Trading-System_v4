"""Fail-closed genome-specific horizon and checkpoint governance audit."""
import pathlib,json,collections
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
def main():
 a=[json.loads(s) for s in (ROOT/'all_candidates.jsonl').open()]
 assert len(a)==4360
 distribution=collections.Counter(); invalid=[]; nonpositive=0
 assignments=[]
 for r in a:
  options=r['horizons']
  assert len({int(x['horizon']) for x in options})==len(options)
  # This is an exploratory DEV selection ONLY, not a frozen trade horizon.
  # No chosen horizon is authorized for heldout test until train-only selection.
  viable=[x for x in options if x.get('lcb95') is not None and x.get('n',0)>0]
  if not viable: invalid.append(r['index']);continue
  candidate=max(viable,key=lambda x:(float(x['lcb95']),-int(x['horizon'])))
  h=int(candidate['horizon']);distribution[h]+=1
  if float(candidate['lcb95'])<=0:nonpositive+=1
  checkpoints=[c for c in (1,2,3,5,7,10,15,20) if c<h]
  assignments.append({'genome_index':r['index'],'exploratory_horizon':h,'checkpoints_before_exit':checkpoints,
   'exploratory_lcb95':candidate['lcb95'],'eligible_for_certified_heldout':False})
 report={'status':'HORIZON_GOVERNANCE_FAIL_CLOSED','genomes':len(a),
 'available_horizons':[1,2,3,5,7,10,15,20,63],
 'exploratory_dev_lcb_best_distribution':dict(sorted(distribution.items())),
 'genomes_without_positive_best_lcb':nonpositive,'invalid':invalid,
 'error_corrected':'Universal 20-session endpoint is not genome-specific and must not be used for promotion.',
 'requirements':['Freeze genome horizon using training-only evidence, not all DEV observations.',
 'Allow checkpoints only strictly before horizon.',
 'Use horizon-specific net returns and side-specific costs.',
 'Train/calibrate/test with nonoverlap and horizon-aware embargo.',
 'For horizon 1, no checkpoint after entry is possible under current daily-open schedule.',
 'Horizon 63 requires outcome array availability and proper censoring.',
 'Do not treat DEV-screen optimum as out-of-sample-selected horizon.'],
 'protected_banks_touched':False}
 out=ROOT/'matched_winner_loser_checkpoint_v3_20261009'
 (out/'horizon_integrity_audit.json').write_text(json.dumps(report,indent=2))
 with (out/'exploratory_horizon_assignments.jsonl').open('w') as w:
  for x in assignments:w.write(json.dumps(x)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
