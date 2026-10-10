# MTS controller integration — second-server launch readiness

Status: PREPARATION ONLY. No GA or historical replay launched.

## Authority and separation
- Production trade gating is exclusively the causal A/B/C DEFENSIVE declaration and R-1 NORMAL recovery declaration.
- The 2007–09, 2020, and 2022 calendar exclusion intervals are research-only masks. Never use them to trigger live liquidation, block live entries, or override R-1.
- A/B/C has priority if A/B/C and R-1 fire simultaneously.
- On DEFENSIVE designation at decision close T: cancel pending Normal entries and liquidate every open Normal position at the first executable opportunity, with realized transaction costs. Keep proceeds in cash. Track fills and incomplete liquidations.
- Resume Normal entries only on causal R-1 NORMAL designation; the actual execution/confirmation and portfolio exposure constraints still apply.
- No same-close execution based on an end-of-day signal; no future data in predictors.

## Available engineered components
- Core/layered_ga/defensive_state_controller.py (existing controller).
- Core/layered_ga/regime_liquidation.py (per-security horizon shortening).
- Core/layered_ga/regime_state_routing.py (state-based entry eligibility and transition extraction).
- scripts/test_regime_liquidation_20261010.py and scripts/test_regime_state_routing_20261010.py: 9 unit tests passed.

## Launch blockers to resolve BEFORE purchase
1. Validate the controller's actual A/B/C/R-1 signal-generation code and its causal, point-in-time inputs.
2. Locate or regenerate the state tape from reproducible inputs. The expected Research/State/MTS_ABC_DEFENSIVE_R1_STATE_TAPE_20261005.csv is NOT present on the current Nebius instance as of this audit; the generation script exists, but has not been executed.
3. Implement portfolio-level transition handling: multiple open positions, partial fills, order cancellations, cash balance, costs, and failed exits.
4. Confirm security trading calendars and missing sessions. Existing per-security horizon mapper deliberately fails closed when a transition date is absent.
5. Verify signal-close -> next executable open chronology and no lookahead.
6. Build an isolated replay runner with frozen input manifest and output checkpoints; use DEV80 only. DEV37 transport only under approved protocol. Do not access DEV50 or BLIND17.
7. Add integration tests for simultaneous A/B/C and R-1, repeated DEFENSIVE, recovery, missing prices, multiple positions, and date-mask disagreement.
8. Package exact Git commit, dependency lock, input checksums, environment preflight, run command, restart/resume instructions, and cloud-cost shutdown procedure.

## Deployment gate
Only recommend renting the additional server after all launch blockers are cleared and the preflight suite passes. No GA should be started during preparation. Existing Gen3 process is unchanged.