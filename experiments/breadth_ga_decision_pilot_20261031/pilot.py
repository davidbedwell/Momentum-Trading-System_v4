"""Deterministic eligibility audit. Intentionally contains no optimizer or live imports."""
from pathlib import Path
import hashlib
import json
import gzip
import time
import numpy as np
import pandas as pd

R = Path(__file__).resolve().parent
SOURCE = R.parent / 'top_chromosome_spy_breadth_replay_20261031'
MIN_EVENTS = 20
MIN_ACTIVE_FOLDS = 2


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def separated_events(frame, gap=63):
    """Conservative support proxy: disjoint holding intervals plus 63 business days.

    Shared chromosome/ticker dates merge. Counts are NOT proven independent events.
    """
    end = None
    count = 0
    for row in frame.sort_values(['entry_date', 'exit_date']).itertuples():
        if end is None or row.entry_date > end + pd.offsets.BDay(gap):
            count += 1
        end = row.exit_date if end is None else max(end, row.exit_date)
    return count


def summarize(g, keep):
    keep = pd.Series(np.asarray(keep, dtype=bool), index=g.index)
    base = float(g.pnl.sum())
    retained = float(g.loc[keep, 'pnl'].sum())
    days = (g.exit_date - g.entry_date).dt.days + 1
    proxy = g.acquisition_cost * days
    return dict(n=len(g), kept=int(keep.sum()), skipped=int((~keep).sum()),
                base_pnl=base, retained_pnl=retained,
                uplift_pnl=retained-base, skipped_net_pnl=base-retained,
                skipped_winner_pnl=float(g.loc[~keep & (g.pnl > 0), 'pnl'].sum()),
                avoided_loss_pnl=float(-g.loc[~keep & (g.pnl < 0), 'pnl'].sum()),
                acquisition_retention=float(g.loc[keep, 'acquisition_cost'].sum()/g.acquisition_cost.sum()) if len(g) else np.nan,
                capital_days_retention=float(proxy[keep].sum()/proxy.sum()) if len(g) else np.nan,
                entry_dates=g.entry_date.nunique(), separated_event_proxy=separated_events(g),
                cagr=np.nan, mdd=np.nan, calmar=np.nan)


def eligibility(portfolio_valid, events, active_folds, positive_later_folds, lower_bound_positive):
    checks = dict(cash_constrained_counterfactual_valid=bool(portfolio_valid),
                  minimum_separated_events=events >= MIN_EVENTS,
                  multiple_active_folds=active_folds >= MIN_ACTIVE_FOLDS,
                  repeatable_later_net_benefit=positive_later_folds >= MIN_ACTIVE_FOLDS,
                  uncertainty_supports_net_benefit=bool(lower_bound_positive))
    return checks, all(checks.values())


def main():
    start = time.monotonic()
    files = ['GA_RESEARCH_OBJECTIVE.md', 'trades.csv.gz', 'entry_features.csv',
             'selection.csv', 'fold_audit.csv', 'fold_correlations.csv',
             'decision_value.csv', 'decision_summary.csv', 'block_bootstrap.csv',
             'metadata.json', 'report.py', 'study.py']
    hashes = {str(SOURCE / name): sha(SOURCE / name) for name in files}
    prior_report = R.parent/'breadth_chromosome_entry_20261031/REPORT.md'
    hashes[str(prior_report)] = sha(prior_report)
    t = pd.read_csv(SOURCE/'trades.csv.gz', parse_dates=['entry_date', 'exit_date', 'feature_date'])
    assert (t.feature_date < t.entry_date).all()
    assert np.allclose(t.pnl/t.acquisition_cost, t.net_return)
    assert not t.duplicated(['system','chromosome_id','fold','ticker','entry_date','exit_date']).any()
    selection = pd.read_csv(SOURCE/'selection.csv')
    audit = pd.read_csv(SOURCE/'fold_audit.csv')
    # Verify immutable source closed-cycle amounts; no price/exit/cost substitution.
    ledger_checks = []
    for path, group in selection.groupby('path'):
        d = json.load(gzip.open(path, 'rt'))
        hashes[path] = sha(path)
        archived = {(z['ticker'],z['entry_date'],z['exit_date']): z for z in d['trades']}
        sub = t[(t.system == d['system']) & (t.chromosome_id == d['chromosome_id'])]
        for z in sub.itertuples():
            original = archived[z.ticker, str(z.entry_date.date()), str(z.exit_date.date())]
            assert abs(original['pnl']-z.pnl) < .01
            assert original['entry_session'] == z.entry_session
            assert original['exit_session'] == z.exit_session
        ledger_checks.append(dict(path=path, checked_trades=len(sub), fills=len(d['fills']),
                                  nav_sessions=len(d['nav']), pnl_reconciled=True))
    pd.DataFrame(ledger_checks).to_csv(R/'ledger_checks.csv',index=False)
    choices = pd.read_csv(SOURCE/'decision_value.csv')
    rows = []
    for (system, cid, fold), g in t.groupby(['system','chromosome_id','fold']):
        masks = [('baseline', np.ones(len(g),dtype=bool)),
                 ('fixed_b50_le_0.5', (g.b50 <= .5).fillna(False))]
        prior = choices[(choices.system==system)&(choices.chromosome_id==cid)&(choices.fold==fold)]
        if len(prior):
            z = prior.iloc[0]
            masks.append(('prior_training_selected_median', z.direction*(g[f'b{int(z.ma)}']-z.threshold)>=0))
        for model, mask in masks:
            rows.append(dict(system=system,chromosome_id=cid,fold=fold,year='all',model=model,**summarize(g,mask)))
            for year, sub in g.groupby(g.entry_date.dt.year):
                indexed = pd.Series(np.asarray(mask),index=g.index)
                rows.append(dict(system=system,chromosome_id=cid,fold=fold,year=str(year),model=model,**summarize(sub,indexed.loc[sub.index])))
    results = pd.DataFrame(rows)
    results.to_csv(R/'trade_comparisons.csv',index=False)
    # Include dormant selected slots explicitly, rather than replacing them with later winners.
    audit.to_csv(R/'fold_support.csv',index=False)
    support=[]
    for (system,fold),g in t.groupby(['system','fold']):
        support.append(dict(system=system,fold=fold,trades=len(g),dates=g.entry_date.nunique(),
                            separated_event_proxy=separated_events(g)))
    pd.DataFrame(support).to_csv(R/'event_support.csv',index=False)
    # Existing evidence already fails the economic gate. New fixed diagnostic is never used
    # to tune/reopen this stop; previously inspected periods are not pristine OOS.
    active_folds = max(sum(z['trades'] >= 30 and z['dates'] >= 20
                               for z in support if z['system'] == family)
                           for family in ['GA6', 'GA7'])
    economic = choices.assign(uplift=choices.kept_pnl-choices.base_pnl).groupby(['system','fold']).uplift.sum()
    positive_folds = max(int((economic.loc[family] > 0).sum()) for family in ['GA6','GA7'])
    checks, launch = eligibility(False, max(z['separated_event_proxy'] for z in support),
                                 active_folds, positive_folds, False)
    assert not launch
    decision = dict(decision='NO-GA warranted', optimizer_launched=False,
                    hypotheses_evolved=0, portfolio_metrics='unavailable', checks=checks,
                    minimum_events=MIN_EVENTS, minimum_active_folds=MIN_ACTIVE_FOLDS,
                    runtime_seconds=time.monotonic()-start, seed=None,
                    seed_reason='No random operations; no evolution authorized by evidence.',
                    hashes=hashes)
    for p in [Path(__file__),R/'test_pilot.py',R/'PROTOCOL.md']:
        decision['hashes'][str(p)] = sha(p)
    (R/'decision.json').write_text(json.dumps(decision,indent=2)+'\n')
    # These sums are bookkeeping across separate accounts, never portfolio returns.
    a=results[(results.year=='all') & (results.system.isin(['GA6','GA7']))]
    summary=a.groupby(['system','model'])[['base_pnl','retained_pnl','uplift_pnl','skipped_winner_pnl','avoided_loss_pnl']].sum()
    summary.to_csv(R/'accounting_summary.csv')
    (R/'REPORT.md').write_text('''# Breadth GA decision pilot\n\n**NO-GA warranted.** No evolutionary optimization was launched; zero genomes were evaluated. Available evidence does not establish an economically useful, repeatable breadth gate. This is a null eligibility result, not proof that every breadth function has zero edge.\n\nThe user objective, original archival report, replay report source, trade ledger, selection, fold splits, correlations, bootstrap and previous decision results were reviewed. The replay directory has no generated REPORT.md; its report.py contains the intended report text and was read without executing it or changing prior artifacts.\n\nThe strongest prior economic warning is GA6: the earlier training-selected median filter raises average trade return from 2.514% to 2.850%, yet retains only 104,670.83 of 135,843.93 in closed-trade net PnL, for an arithmetic opportunity cost of 31,173.09. GA7 retains 349.86 versus -1,150.40, but evidence is dominated by F2: F1 has no trades and F3 has four. These are sums of separate hypothetical chromosome accounts, **not investable combined portfolios**. Prior kept-versus-skipped return intervals include zero for both families; those intervals are not uncertainty intervals for portfolio uplift. GA6 MA50 Pearson correlation changes from -0.055 to -0.312 to +0.070 across F1/F2/F3. GA8 winners differ each year and have no corresponding multi-year chromosome training sample.\n\n## Objective stop and independent support\n\nPROTOCOL.md defines a conjunctive stop: require validated cash-constrained counterfactual accounting, at least 20 separated market events, at least two materially active chronological evaluation folds, repeatable net benefit on those folds, and uncertainty supporting incremental net benefit before any search. These are conservative research screening choices made after reviewing the existing evidence, not preregistration or calibrated significance tests. The economic and accounting failures independently stop this phase. No threshold search, MA search, slope interaction, nonlinear fit, population or random seed was run. No automated future launch path is included.\n\nEvent support merges overlapping holding intervals across chromosomes and requires a 63-business-day gap to start another cluster. event_support.csv reports this deliberately conservative support proxy, not a claim of statistical independence. Trade counts and entry dates are also shown. Changing genomes or duplicated holdings does not create independent market episodes. Sparse GA7 slots remain in fold_support.csv.\n\n## Comparisons and opportunity cost\n\ntrade_comparisons.csv compares each original chromosome/fold and entry year with (1) unchanged baseline, (2) fixed MA50 breadth <=50% gate, and (3) the **previous study's** earlier-training-selected median rule, with its original frozen MA/direction/threshold. The third comparator is not evolved and is unavailable for GA8. The fixed rule is a descriptive comparator chosen in this phase, informed by prior weak-breadth findings; it is not a newly validated holdout result. Evolved-model results are **not run**, rather than invented or replaced by the earlier rule. No test-period threshold was optimized.\n\nEach gate keeps or skips whole original episodes, including their original adds, partial reductions, costs and exits in original net PnL. Missing breadth fails closed. Positive skipped PnL is opportunity cost; negative skipped PnL is avoided loss. Net uplift equals avoided loss minus skipped winners. Acquisition retention and acquisition-cost times inclusive calendar holding-day retention are turnover/capital-duration proxies, **not daily marked portfolio exposure**; partial exits/adds prevent interpreting them as actual exposure. GA6/7 closed-trade PnL and entry/exit sessions reconcile to all ten selected original ledgers (ledger_checks.csv). GA8 uses the already reconstructed original-cost episode records; its fills are not independently rebuilt here.\n\nAggregate separate-account bookkeeping (currency units; no allocation or compounding implied):\n\n'''+'```text\n'+summary.to_string()+'\n```'+'''\n\n## Portfolio metrics and chronology\n\nCAGR, MDD and Calmar are **unavailable for this counterfactual comparison** and blank in output. Original full-account NAV exists, but filtered completed trades do not supply a validated cash-constrained marked portfolio. Reusing original baseline NAV as filtered NAV would be wrong. Fills contain partial sizing, dividends and settlement effects; freeing cash changes order competition and strategy state. This pilot does not simulate new replacement trades or leverage. It does not concatenate chromosomes, reset fold cash, compound per-trade returns or turn realized-only PnL into equity. Original NAV could describe its own original account, but cannot provide the requested comparable filtered-account metrics. A portfolio objective cannot be satisfied by optimizing these trade-level sums; this is an independent reason to stop.\n\nOriginal folds are training from 2009 to strictly before 2012/2014/2016, with evaluations [2012,2014), [2014,2016), [2016,2018). All model choices in the inherited median-rule comparator used earlier completed trades. Selected chromosome identities vary by fold. Current diagnostics perform no fitting. Both entry and exit must lie within each evaluation window; 71 boundary trades are excluded in the inherited ledger, and carried-in positions are absent. This completed-trade censoring limits all results; no independent cash-reset portfolio is claimed. GA8 covers completed 2023/2024/2025 episodes, excluding 11 open positions.\n\nAll periods have already been inspected. They are chronological retrospective evaluation, **not pristine OOS**. Chromosomes and DEV79 universe were discovered retrospectively; survivor, universe and prior-search bias persist. DEV79 breadth is a market proxy, not validated point-in-time S&P 500 membership breadth. Entry features precede entries; MA horizons 10/20/50/100/200 and slopes are available but no evidence-based permission to evolve them arose. Earlier correlation significance, isolated year effects and untested nonlinear possibilities do not establish tradable incremental value.\n\n## Reproduction and checks\n\nFrom repository root:\n\n```sh\n/opt/mts/.venv/bin/python experiments/breadth_ga_decision_pilot_20261031/pilot.py\n/opt/mts/.venv/bin/python -m unittest discover -s experiments/breadth_ga_decision_pilot_20261031 -p 'test_*.py' -v\n```\n\nThe deterministic audit takes seconds and hashes all consumed inputs and selected ledgers in decision.json. Tests cover economic opportunity-cost identity, whole-episode gate accounting, shared-event support, future-evidence inability to bypass the portfolio stop, causal feature timing and inherited fold cutoff constraints. No live GA/MTS source, database or configuration was changed. Any future search requires new economic support and validated portfolio accounting; no deployment is recommended.\n''')
    print(summary.to_string())
    print(json.dumps({k:v for k,v in decision.items() if k!='hashes'},indent=2))

if __name__ == '__main__':
    main()
