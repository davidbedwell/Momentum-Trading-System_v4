# GA5 unified design — 2026-10-18

## Binding research design
- No fixed count of market niches, no market-niche-constrained breeding.
- Evolve complete chromosomes jointly: entry, hold, exit, increase, decrease, replacement, stop, trailing stop, sizing, risk budget and time exit.
- Market conditions are measured as continuous and overlapping, causal dimensions: direction/structure; volume, volatility, liquidity, breadth; momentum, rotation, reversal and recovery. Discover additional environments empirically without hard-coded counts.
- Evaluate each chromosome across all observable environments. Historical seven seed labels are provenance only, not eligibility filters or market truth.
- Pass 1: simulate and persist every qualifying shadow trade and all fill/adjustment/exit events, with prices, quantities, costs, MAE/MFE, corporate actions, missing-data flags and point-in-time context. Shadow returns are not investable portfolio CAGR.
- Pass 2: hide future outcomes, replay every day chronologically, learn rankings from completed past outcomes only, allocate under realistic cash/settlement/exposure constraints, compare against hindsight outcomes only after decision.
- Retain full GA4 bank and GA5 lineage; validate sources and reproducibility before use. No blind-data consumption.
- Efficient implementation: reusable features, batched/vectorized calculations, parallel processing, checkpoints, deterministic hashes. No reduced coverage or omitted scientific controls.

## Implementation status
- market_state.py: first backward-looking multidimensional research features, NOT certified PIT universe or liquidity model.
- unified_evolution.py: cross-label breeding adapter, NOT integrated into production runner.
- Existing runner_v4.py still uses seven isolated seed populations; do not launch it as the new design.
- Existing shadow_signals.py lacks scale-in/out event histories.
- Existing two_pass_replay.py is a seven-chromosome one-selection-per-day diagnostic, not final selector.
- Remaining: verified chromosome bank ingestion; unified evolutionary runner; joint scale-in/out grammar and fills; comprehensive event ledger; data-driven state discovery; leakage-safe learning; full portfolio validation and tests.
