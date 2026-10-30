# Data-source policy
Primary provider: Alpaca for historical OHLCV, market context, and supported corporate actions.
Earnings requirement: independently verify whether Alpaca supplies historical earnings announcement timestamps, actual EPS, consensus estimates, surprises, revenue and guidance for each research year. Do not equate trading calendars or corporate-action records with complete earnings fundamentals. Record missing fields and coverage gaps; do not fabricate or silently backfill with another provider.
Study years: four non-crash discovery and four different non-crash blind years, to be selected and frozen before inspecting outcomes.
Isolation: no protected MTS research/validation banks or DEV79 datasets.
