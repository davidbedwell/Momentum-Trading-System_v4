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
    "universe_id": "<authorized-universe-id>",
    "feature_set_id": "mts_market_predictors",
    "feature_set_version": "v1",
    "feature_columns": ["return_126__v1", "return_252__v1", "return_252_skip_20__v1", "return_126_percentile__v1", "return_252_percentile__v1", "return_252_skip_20_percentile__v1"],
    "outcome_feature_set_id": "mts_historical_outcomes",
    "outcome_feature_set_version": "v1",
    "outcome_feature_columns": ["forward_return_20__v1", "forward_return_63__v1"]
  },
  "medium_term_trend_persistence": {
    "universe_id": "<authorized-universe-id>",
    "feature_set_id": "mts_market_predictors",
    "feature_set_version": "v1",
    "feature_columns": ["close_to_sma_20__v1", "close_to_sma_50__v1", "close_to_sma_200__v1", "sma20_slope_5__v1", "return_63__v1", "return_126__v1"],
    "outcome_feature_set_id": "mts_historical_outcomes",
    "outcome_feature_set_version": "v1",
    "outcome_feature_columns": ["forward_return_20__v1", "forward_return_63__v1"]
  },
  "short_horizon_reversal": {
    "universe_id": "<authorized-universe-id>",
    "feature_set_id": "mts_market_predictors",
    "feature_set_version": "v1",
    "feature_columns": ["return_1__v1", "return_3__v1", "return_5__v1", "return_10__v1"],
    "outcome_feature_set_id": "mts_historical_outcomes",
    "outcome_feature_set_version": "v1",
    "outcome_feature_columns": ["forward_return_1__v1", "forward_return_3__v1", "forward_return_5__v1", "forward_return_10__v1"]
  },
  "post_earnings_behavior": {
    "universe_id": "<authorized-universe-id>",
    "feature_set_id": "<validated-point-in-time-earnings-feature-set>",
    "feature_set_version": "<version>",
    "feature_columns": ["<event-time/surprise/eligible-event columns>"],
    "outcome_feature_set_id": "mts_historical_outcomes",
    "outcome_feature_set_version": "v1",
    "outcome_feature_columns": ["forward_return_5__v1", "forward_return_20__v1", "forward_return_63__v1"]
  },
  "deterministic_negative_control": {
    "universe_id": "<authorized-universe-id>",
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


## Mandatory zero-Sol readiness gate

Before any paid control execution, run `scripts/preflight_scientific_controls.py`. Every control configuration must additionally supply human-authorized mechanical adequacy floors:

- `minimum_eligible_dates`;
- `minimum_eligible_securities`;
- `minimum_complete_rows_per_column`.

Every control must also declare `historical_membership_classification` as either `AUTHORITATIVE_HISTORICAL_POINT_IN_TIME` or `CURRENT_MEMBER_CONDITIONED`. This records provenance and scope; it is not a readiness preference.

No default thresholds are invented by deterministic code. Placeholder values, an unidentified membership source, an absent or invalid membership classification, unknown feature sets, unavailable columns, duplicate security/date identities, or inadequate coverage cause `NOT_READY`.

Historical point-in-time index membership is not a prerequisite for this control campaign. A current-member universe may be used when its membership semantics and scope are recorded. Former constituents are absent, so results describe the histories of the current-member population; they must not be described as an authoritative reconstruction of the historical index or generalized to securities outside that population. This scope boundary does not make the present-day research objective invalid and does not relax prediction-time integrity for features, earnings, outcomes, or any other information used at historical time `T`.

The preflight also requires a separate RD-hidden answer-key JSON containing exactly the five control IDs. Each control answer contains:

- `formulation`;
- `expected_direction`;
- `expected_horizons`;
- `robustness_conditions`;
- `independent_benchmark_artifact_sha256`;
- `dataset_fingerprint_sha256`;
- `assessor`.

The answer key is never included in Research Director context. The dataset fingerprint binds the independently established answer to the exact queried predictor/outcome surface. The benchmark artifact hash binds it to the independent calculation used to establish that the expected control is demonstrably present in the supplied data.

Example preflight:

```bash
.venv/bin/python scripts/preflight_scientific_controls.py \
  --control-config-json /path/to/control_config.json \
  --hidden-answer-key-json /path/to/hidden_answer_key.json \
  --derived-market-root /path/to/derived_market_store \
  --output-json /path/to/control_readiness_report.json
```

The paid control runner now requires `--control-readiness-report`. Direct paid open-ended universe discovery requires a complete independently assessed `CALIBRATION_PASS` report through `--control-campaign-report`. Dry runs remain zero-cost and are not blocked.
