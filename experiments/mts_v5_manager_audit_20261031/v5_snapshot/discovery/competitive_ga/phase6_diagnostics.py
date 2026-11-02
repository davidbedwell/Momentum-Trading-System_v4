"""Bounded, training-only fixed-native-tape accounting bridge."""
import json
from pathlib import Path
from .phase5_diagnostics import training_panels
from .ga7_ledger_bridge import replay
from .first_year_manifest import digest


def run():
    g, _, _, panels, _ = training_panels()
    from ga7.runner import passes
    from ga7.request_replay import replay_requests
    checks = []
    for n in (2, 8, 16, 32):
        native, ledger = replay_requests(g, panels[:n], passes, cash_yield=0., record_pass=True)
        bridge = replay(g, panels[:n], ledger.requests)
        residual = bridge['final_nav']-native['final_nav']
        checks.append(dict(sessions=n, native_nav=native['final_nav'], bridge_nav=bridge['final_nav'],
                           residual=residual, cashflow_residual=bridge['max_cashflow_residual'],
                           terminal_cashflow_residual=bridge['terminal_cashflow_residual']))
        if abs(residual) > 1e-7:
            raise ArithmeticError('native/bridge terminal parity failed')
    steps = []
    options = {}
    previous = bridge['final_nav']
    for label, option in [('fractional_shares', 'fractional'), ('remove_capacity_and_sector_limits', 'capacity_limits'),
                          ('include_receivables_in_sizing_equity', 'receivables_in_equity'),
                          ('retain_terminal_holdings', 'terminal_liquidation')]:
        options[option] = option not in ('capacity_limits', 'terminal_liquidation')
        result = replay(g, panels, ledger.requests, **options)
        steps.append(dict(change=label, nav=result['final_nav'], delta=result['final_nav']-previous,
                          fills=len(result['fills']), max_cashflow_residual=result['max_cashflow_residual']))
        previous = result['final_nav']
    phase5_path = Path('PHASE5_DIAGNOSTICS.json')
    prior = json.loads(phase5_path.read_text())
    if abs(prior['native_final_nav']-native['final_nav']) > 1e-7:
        raise ArithmeticError('phase5 baseline changed')
    source_hashes = {str(phase5_path):digest(phase5_path)}
    for path, expected in prior['sources'].items():
        actual = digest(Path(path))
        if actual != expected:
            raise ValueError('phase5 source identity changed: '+path)
        source_hashes[path] = actual
    isolated = {}
    for label, option, value in [('fractional_shares', 'fractional', True),
                                  ('remove_capacity_and_sector_limits', 'capacity_limits', False),
                                  ('include_receivables_in_sizing_equity', 'receivables_in_equity', True),
                                  ('retain_terminal_holdings', 'terminal_liquidation', False)]:
        alternative = replay(g, panels, ledger.requests, **{option:value})
        isolated[label] = alternative['final_nav']-native['final_nav']
    return dict(status='FIXED_TAPE_ACCOUNTING_RECONCILED_NOT_POLICY_EQUIVALENCE', proof_opened=False,
                sealed_sessions=867, first=panels[0][0], last=panels[-1][0], sessions=len(panels),
                opening_contract='100000 settled cash; no holdings/receivables; fee .001; T+1; zero yield',
                corporate_action_contract='adjusted prices; no raw split events; dividend credited ex-date; no pay-date certification',
                native_terminal_checks=checks, native_terminal_fee=bridge['terminal_fee'],
                native_fills=len(bridge['fills']), fixed_tape_waterfall=steps,
                isolated_fixed_tape_deltas=isolated,
                original_shadow_minus_native_both_marked=prior['funded_shadow_nav']-(native['final_nav']+bridge['terminal_fee']),
                waterfall_total=previous-native['final_nav'],
                original_shadow_minus_native=prior['nav_difference'],
                original_shadow_minus_changed_fixed_tape=prior['funded_shadow_nav']-previous,
                remaining_scope='Unallocated: endogenous held-state/action divergence, alphabetical versus native priority, target versus incremental sizing, and interactions. Ordered waterfall is path dependent; not attribution of original shadow gap.',
                sources=source_hashes,
                missing_inputs=['certified corporate actions/pay dates', 'synthetic risk/gap/group publications',
                                'GA4 approved exit archive linkage', 'joint synthetic Horizons stress source',
                                'verified family training lineage'])


if __name__ == '__main__':
    result = run()
    Path('PHASE6_DIAGNOSTICS.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
