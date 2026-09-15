# MTS v4 Scientific Control Campaign Configuration — 2026-09-14

The control runner is `scripts/run_sol_scientific_controls.py`. It executes all five blinded calibration controls through the ordinary governed universe Sol runner. The expected answer/rubric is **not** included in the RD prompt or evidence configuration.

The configuration file is a JSON object keyed by the five exact control IDs:

- `cross_sectional_medium_term_momentum`
- `medium_term_trend_persistence`
- `short_horizon_reversal`
- `post_earnings_behavior`
- `deterministic_negative_control`

Each value describes only the evidence/query surface available to that control:

```json
{
  "cross_sectional_medium_term_momentum": {
    "universe_id": "<point-in-time-universe-id>",
    "feature_set_id": "mts_market_predictors",
    "feature_set_version": "v1",
    "feature_columns": ["return_126__v1", "return_252__v1", "return_126_percentile__v1", "return_252_percentile__v1"],
    "outcome_feature_set_id": "mts_historical_outcomes",
    "outcome_feature_set_version": "v1",
    "outcome_feature_columns": ["forward_return_20__v1", "forward_return_63__v1"]
  },
  "medium_term_trend_persistence": {
    "universe_id": "<point-in-time-universe-id>",
    "feature_set_id": "mts_market_predictors",
    "feature_set_version": "v1",
    "feature_columns": ["close_to_sma_20__v1", "close_to_sma_50__v1", "close_to_sma_200__v1", "sma20_slope_5__v1", "return_63__v1", "return_126__v1"],
    "outcome_feature_set_id": "mts_historical_outcomes",
    "outcome_feature_set_version": "v1",
    "outcome_feature_columns": ["forward_return_20__v1", "forward_return_63__v1"]
  },
  "short_horizon_reversal": {
    "universe_id": "<point-in-time-universe-id>",
    "feature_set_id": "mts_market_predictors",
    "feature_set_version": "v1",
    "feature_columns": ["return_1__v1", "return_3__v1", "return_5__v1", "return_10__v1"],
    "outcome_feature_set_id": "mts_historical_outcomes",
    "outcome_feature_set_version": "v1",
    "outcome_feature_columns": ["forward_return_1__v1", "forward_return_3__v1", "forward_return_5__v1", "forward_return_10__v1"]
  },
  "post_earnings_behavior": {
    "universe_id": "<point-in-time-universe-id>",
    "feature_set_id": "<validated-point-in-time-earnings-feature-set>",
    "feature_set_version": "<version>",
    "feature_columns": ["<event-time/surprise/eligible-event columns>"],
    "outcome_feature_set_id": "mts_historical_outcomes",
    "outcome_feature_set_version": "v1",
    "outcome_feature_columns": ["forward_return_5__v1", "forward_return_20__v1", "forward_return_63__v1"]
  },
  "deterministic_negative_control": {
    "universe_id": "<point-in-time-universe-id>",
    "feature_set_id": "mts_acceptance_negative_control",
    "feature_set_version": "v1",
    "feature_columns": ["deterministic_null__v1"],
    "outcome_feature_set_id": "mts_historical_outcomes",
    "outcome_feature_set_version": "v1",
    "outcome_feature_columns": ["forward_return_5__v1", "forward_return_20__v1"]
  }
}
```

Before the control campaign, build/update the isolated negative-control feature set with `scripts/build_negative_control_feature_set.py`. It copies only `security_id`, `effective_date`, and eligibility from an existing derived-market row surface and computes a deterministic SHA-256 identity/date hash. No price, return, volume, volatility, event, sector, breadth, or other market measurement is copied into the negative-control predictor set. This prevents a genuine market feature from contaminating the negative control.

The PEAD entry intentionally remains a placeholder until the historical earnings source passes timestamp/coverage audit. Do not substitute current/revised earnings data or fabricate historical event timing merely to make the control runnable.

The runner requires an explicit per-control Sol spend ceiling and disables interactive spend extension inside each child run. A technical/spend failure stops the campaign by default rather than silently spending through the remaining controls. Every Sol universe run preserves `sol_replay_envelopes.jsonl` so successful control decisions become exact Qwen replay cases.

After execution, `scientific_control_campaign_report.json` automatically assembles the five run states, Analysis counts, findings, closure state, Sol spend and replay-capture paths. PASS/PARTIAL/FAIL grades are supplied only after the run by independent human/ChatGPT review under the previously agreed rubric; deterministic code never grades scientific adequacy from keywords or Finding count.
