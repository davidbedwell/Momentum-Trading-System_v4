# MTS v4 Discovery — General Winner Capital Rule — Frozen Holdout Result — 2026-10-02

## Conclusion
**DISCOVERY HOLDOUT REPLICATION: PASS.** The broad causal **historical expectancy / p10 downside** capital-allocation relationship replicated on the once-opened Discovery Holdout and is the parsimonious surviving Discovery hypothesis.

The historical-win-rate modifier also passed every frozen gate, but did not demonstrate a meaningful incremental Holdout advantage over the simpler EV/p10 control. Under the pre-frozen selection rule, the modifier is therefore not preferred.

## Once-opened Holdout
Equal-sizing baseline:
- terminal wealth 2.744909x
- CAGR-equivalent 22.3820%
- max drawdown -15.9683%
- daily CVaR5 -2.11892%

### CONTROL_EV_P10_BROAD — 0.75x floor / 1.50x cap
- PASS: all frozen gates
- mean sizing contribution +0.0128805 return units
- ticker breadth 65/67 positive (97.0%)
- year breadth 6/6 positive (100%)
- family breadth 7/8 positive (87.5%)
- ticker-cluster 95% CI [0.0107441, 0.0152575]
- largest ticker share of positive contribution 4.40%
- largest genome share 2.21%
- terminal wealth 2.834956x: +3.2805% vs equal sizing
- CAGR-equivalent +0.7927 percentage points vs equal
- max drawdown improved by 0.4103 percentage points
- CVaR5 worsened by 0.0647 percentage points

### PROPOSED_EV_P10_X_WINRATE_BROAD — 0.75x floor / 1.50x cap
- PASS: all frozen gates
- mean sizing contribution +0.0129035
- ticker breadth 63/67 positive (94.0%)
- year breadth 6/6 positive
- family breadth 7/8 positive
- ticker-cluster 95% CI [0.0107689, 0.0152744]
- terminal wealth 2.829330x: +3.0756% vs equal sizing
- max drawdown improved by 0.4284 percentage points
- CVaR5 worsened by 0.0651 percentage points

## Modifier comparison
The win-rate modifier's mean trade contribution exceeded the simple EV/p10 control by only 0.0000230 return units, while terminal wealth was 0.1984% lower relative to the control and ticker breadth was 63/67 rather than 65/67. This does not establish incremental value sufficient to justify the added term.

## Scientific interpretation
The replicated relationship is broad rather than concentrated: positive across 65 of 67 Holdout tickers, every Holdout year, and 7 of 8 signal families, with low ticker/genome contribution concentration and a ticker-cluster confidence interval wholly above zero. This is substantially more consistent with a general MTS winner-capital relationship than the earlier A2 frozen rule result, which produced only 2/20 positive ticker contributions.

The working relationship is: allocate more capital when the causally available historical expectancy of the applicable genome/family is high relative to its historical p10 downside tail, using bounded sizing. Historical win rate is not currently justified as an additional term.

This remains Discovery evidence. It is not paper/live promotion and does not retroactively convert the failed A2 validation into a pass. A materially specified candidate must still follow governance before any new Verification evidence is consumed.

## Integrity
- Nominees frozen before Holdout: yes, commit 60ddcf1
- Holdout implementation frozen before replay: yes, commit 7c6f2ac
- Discovery Holdout replayed once: yes
- Verification A accessed by this experiment: no
- Sequestered A60 accessed: no
- Verification B accessed: no
