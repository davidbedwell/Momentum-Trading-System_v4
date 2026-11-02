"""Executable Phase 4 readiness matrix. Diagnostics never certify a launch."""
import argparse
import json
from pathlib import Path
from .first_year_manifest import digest

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=('PHASE4_INPUT_MANIFEST.json','PHASE4_PREFIX_CHECK.json','PHASE4_CACHE_BENCHMARK.json',
          'PHASE4_NATIVE_SMOKE.json','PHASE4_NATIVE_ACTION_AUDIT.json','PHASE4_CONTROL_DISCOVERY.json')


def matrix(root=ROOT):
    evidence={}
    errors=[]
    for name in EVIDENCE:
        path=Path(root)/name
        try:
            record=json.loads(path.read_text())
            for source,signature in record.get('sources',{}).items():
                if digest(source)!=signature:errors.append(name+': stale source '+source)
            if record.get('proof_values_read',False):errors.append(name+': proof seal violated')
            evidence[name]=dict(sha256=digest(path),status=record.get('status'),record=record)
        except (OSError,ValueError,TypeError) as exc:
            errors.append(name+': unavailable or invalid evidence: '+str(exc))
    data={k:v['record'] for k,v in evidence.items()}
    feature=data.get(EVIDENCE[0],{})
    prefix=data.get(EVIDENCE[1],{})
    smoke=data.get(EVIDENCE[3],{})
    action=data.get(EVIDENCE[4],{})
    for dependent,field in ((EVIDENCE[1],'reference_sha256'),(EVIDENCE[2],'cold_manifest_sha256')):
        if dependent in data and EVIDENCE[0] in evidence and data[dependent].get(field)!=evidence[EVIDENCE[0]]['sha256']:
            errors.append(dependent+': stale feature reference')
    if smoke.get('deterministic_sha256')!=action.get('deterministic_sha256'):
        errors.append('bounded smoke and extended audit disagree')
    families={
        'GA4':dict(feature_sessions=feature.get('value_sessions'),native_exit='MISSING_APPROVED_ARCHIVE_LINK',funded_native_shadow='BLOCKED'),
        'HORIZONS':dict(feature_sessions=0,stress='MISSING_JOINT_SCENARIO_PUBLICATION_AND_NORMALIZATION',native_parity='BLOCKED'),
        'GA6':dict(feature_sessions=feature.get('value_sessions'),native_action_sessions=action.get('parity_scope',{}).get('GA6_sessions'),
                   historical_training_cutoff='UNKNOWN',observed_shadow_fills=0),
        'GA7':dict(feature_sessions=feature.get('value_sessions'),native_held_oracle_sessions=action.get('parity_scope',{}).get('GA7_oracle_sessions'),
                   native_boundary_oracle='INCOMPLETE_FIRST_AND_LAST_DATES',synthetic_niche_provenance='UNKNOWN')}
    for row in families.values():
        row.update(authentic_launch='BLOCKED',PIT_earnings_corporate_actions='UNKNOWN',model_training_lineage='UNKNOWN')
    return dict(schema_version=1,status='BLOCKED',authentic_families_ready=0,total_families=4,
        evidence_errors=errors,proof_opened=False,
        coverage=dict(available_sessions=feature.get('available_sessions'),value_sessions=feature.get('value_sessions'),
                      sealed_sessions=feature.get('sealed_sessions'),prefix_invariant_sessions=prefix.get('sessions')),
        families=families,execution=dict(shared_bank='WIRED_AND_FIXTURE_TESTED',settlement='EXPLICIT_RESEARCH_T_PLUS_0_1_2',
            shared_bank_native_smoke_fills=smoke.get('shared_bank_fills'),funded_shadow_fills=smoke.get('shadow_fills'),
            journal_reconciliation=smoke.get('shadow_reconciliation'),aggregate_incumbent_risk='NOT_CERTIFIED',
            defense_timing='CLOSE_TO_NEXT_OPEN_TESTED_NOT_GOVERNED_INPUT_CERTIFICATION',
            native_funded_portfolio_parity='NOT_CERTIFIED',action_utility='ENTRY_CONTEXT_ESTIMATES_NOT_CERTIFIED_ADD_REDUCE'),
        required_dependencies=[
            'Approved calendar authority preserving an untouched independent proof set; existing 867-session seal remains closed',
            '500-name dated membership/security mapping, selected native earnings schedules or explicit absence coverage, and publication timestamps',
            'Corporate-action identity, adjustment convention, dividend pay-date and settlement contracts',
            'Independently verified GA4/Horizons/GA6/GA7 archived model training cutoffs and immutable daily feature snapshots',
            'Approved executable GA4 exit policy linked to frozen archive; experimental callback is excluded from authentic runner',
            'Horizons stress jointly generated with fictional OHLCV, dated publication and approved mapping/normalization',
            'Chronological synthetic GA7 niche models/distances and publication times; DEV79 archive has zero synthetic ticker overlap',
            'Dated synthetic defense/risk/gap/correlation controls plus aggregate incumbent risk implementation and native-ledger reconciliation',
            'Complete remaining sealed-date feature/action parity after calendar authorization; GA7 boundary held oracle and native funded ledger comparisons',
            'Validated incremental action utility, then bounded authentic training and frozen validation without proof selection'],
        evidence={k:{a:b for a,b in v.items() if a!='record'} for k,v in evidence.items()})


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();target=args.output.resolve()
    if not (target.is_relative_to(ROOT) or target.is_relative_to('/tmp')):parser.error('workspace or /tmp output required')
    result=matrix();target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 2

if __name__=='__main__':raise SystemExit(main())
