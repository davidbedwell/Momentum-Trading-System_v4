# 8B calibration validation

Candidate **FAIL**. Completed 480 paired portfolios on 24 untouched holdout seeds in 71.1s. No further tuning.

Only the two CUSUM alarm thresholds change. Frozen corrected engine, drift constants, training mean baseline, date clock, classifier, execution and latch are shared verbatim. Original 8B-D retains its archived thresholds. All arms use original400/200 history.

Threshold rule: each channel is max(0.018, 1.1 × maximum unlatched statistic over all dates of 32 calibration seeds × learnable/outer_noise/null). No reversal calibration. Exact seeds and rule were committed before calibration; threshold lock precedes holdout generation.

Criteria: {"stable_zero_alarms": false, "reversal_three_session": true, "adverse_mdd": true, "outer_noise_return": true, "false_great": false}
Audit checks: {"complete": true, "cash": true, "pnl": true, "cost": true, "net": true, "horizon": true, "no_funding_after_alarm": true, "source_hashes": true, "threshold_lock": true}

| Arm | Learnable FA | Outer noise FA | Null FA | Reversal 3-session /24 | Random reversal 3-session /24 | Outer noise mean return | Reversal max adverse MDD | Random max adverse MDD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|6|0|0|0|0|0|87.63%|3.90%|4.20%|
|7B|0|0|0|0|0|87.63%|3.90%|5.17%|
|8B-D|0|3|9|22|23|80.01%|2.61%|2.38%|
|8B-Cal|0|0|1|22|23|87.63%|2.95%|2.38%|

Original thresholds: [0.018, 0.02735626675064957]; calibrated thresholds: [0.027659290213926383, 0.055015578352069085].

| Seed | Scenario | 6 delay | 7B delay | 8B-D delay | 8B-Cal delay |
|---|---|---:|---:|---:|---:|
|4537256206270286119|reversal|4|6|3|3|
|4537256206270286119|random_reversal|4|6|3|3|
|694382096743991061|reversal|4|5|3|3|
|694382096743991061|random_reversal|4|6|3|3|
|1150718378971727077|reversal|4|6|3|3|
|1150718378971727077|random_reversal|5|8|3|3|
|1167515651896656629|reversal|4|6|3|3|
|1167515651896656629|random_reversal|5|8|3|3|
|4831300176840824932|reversal|5|6|3|3|
|4831300176840824932|random_reversal|6|10|3|3|
|440151416451439808|reversal|4|6|3|3|
|440151416451439808|random_reversal|6|6|3|3|
|3126421887925349304|reversal|7|7|3|3|
|3126421887925349304|random_reversal|4|7|3|3|
|3783921666502362447|reversal|7|7|4|4|
|3783921666502362447|random_reversal|5|8|3|3|
|4776512205175634938|reversal|4|6|3|3|
|4776512205175634938|random_reversal|4|9|3|3|
|5049199660434344524|reversal|7|7|3|3|
|5049199660434344524|random_reversal|5|7|3|3|
|4282214295412051068|reversal|4|6|3|3|
|4282214295412051068|random_reversal|6|8|3|3|
|3657275775949343587|reversal|4|6|3|3|
|3657275775949343587|random_reversal|5|8|3|3|
|6969106638913461576|reversal|6|7|3|3|
|6969106638913461576|random_reversal|5|9|3|3|
|4001078017255128230|reversal|4|5|3|3|
|4001078017255128230|random_reversal|4|7|3|3|
|1396858669394021498|reversal|4|5|3|3|
|1396858669394021498|random_reversal|4|7|3|3|
|2859988942320173670|reversal|4|6|3|3|
|2859988942320173670|random_reversal|7|8|4|4|
|331215616702748929|reversal|9|8|4|6|
|331215616702748929|random_reversal|9|10|3|3|
|1419532715697785908|reversal|4|6|3|3|
|1419532715697785908|random_reversal|6|9|3|3|
|662918785606057485|reversal|6|6|3|3|
|662918785606057485|random_reversal|5|7|3|3|
|4019347600276602974|reversal|4|5|3|3|
|4019347600276602974|random_reversal|5|7|3|3|
|8035674003159893401|reversal|6|6|3|3|
|8035674003159893401|random_reversal|6|9|3|3|
|5228269056551364461|reversal|6|6|3|3|
|5228269056551364461|random_reversal|4|6|3|3|
|1691388399593399844|reversal|4|5|3|3|
|1691388399593399844|random_reversal|4|6|3|3|
|5958543661589150472|reversal|7|7|3|3|
|5958543661589150472|random_reversal|4|7|3|3|

False GREAT is latent AWFUL classified GREAT after executed gating; first3/post3 splits, all scenario means and every paired per-seed return/MDD/false-GREAT contrast are in report.json. Reversal false alarms are prechange alarms; nonreversal false alarms are any latch. Misses count in the 3-session denominator. No post-alarm entries are funded; existing positions finish normally.

## Confidence limitations

- 24 independent holdout seeds; paired scenarios within seed are dependent. No multiplicity correction.
- With zero alarms in 24 seeds, one-sided95 binomial upper is 0.11734615615494881. Nonzero observed rates do not establish population control.
- Calibration is empirical on 32 seeds, three stable scenarios; no anytime-valid or real-market guarantee.
- Threshold maxima across scenarios may sacrifice reversal speed; calibration never used reversal tapes.
- Paired t intervals are descriptive with n24 and possibly non-normal bounded outcomes. Misses and prealarms stay explicit; no complete-case mean-delay claim.
- Seed exclusion scans accessible uncompressed repository evidence; compressed artifacts rely on companion seed manifests. No guarantee about inaccessible external experiments.
- Local hashes/timestamps are auditable but lack trusted external timestamp. No prior results used to select thresholds.
- Single fixed original400/200 history; no extended-history confirmation. Synthetic generator and criteria are inherited or prespecified; no deployment inference.

## Audit artifacts

preregister.json and seeds.json: exact rule, criteria, seeds and scan inventory. commitment.json: pre-calibration source hashes. threshold_lock.json: pre-holdout calibration hash. calibration.json: all calibration date traces and maxima. event_ledger.json and per_seed_reversal_delays.json: alarms, timing and censoring. per_seed.jsonl/results.json: every endpoint and execution audit. replays.jsonl.gz: all fills, NAV and detector traces. opportunities.jsonl.gz: every asset/date label and funding status. tests.log: unit tests. Reproduce only in a separate folder; run.py refuses existing commitment.
