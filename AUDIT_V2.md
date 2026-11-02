# Controlling v2 audit

No additional outcome data inspected. No data run, download, blind release, or certification. Offline fixture suite: 16 passed.

| Requirement | Implementation / status |
|---|---|
| v2 replaces v1 immediately | manifest and RESEARCH_PROTOCOL replaced; README/source policy updated; historical brief explicitly superseded |
| Independent directory only | local path containment and private-directory exclusions retained; no outside writes |
| S&P500 at every month end including exits, PIT GICS | interval membership supported; full reconstruction/validation BLOCKED by missing source coverage |
| Jan 2006–Sep 2026 | manifest frozen; calculation excludes formations outside bounds; full monthly coverage unavailable |
| Every stock, stock return minus sector median | median implemented; any missing PIT member return withholds whole sector benchmark |
| Formation close / next-session open, no proxy | signal cutoffs and panel next-session open enforced; exchange-certified calendar BLOCKED |
| H1 months t-12 through t-2 positive | calendar month closes t-2 / t-13; missing endpoints missing |
| H2 adjusted close / 52-week high positive | 252-session maximum including formation |
| H3 surprise / SD prior eight positive | exactly eight prior EPS surprises, sample SD; no missing substitutions; same-day event excluded |
| H4 gross profit / assets positive | as-filed eligible annual GP and matching period assets; filing strictly before formation implements +1 day; missing tags missing |
| H5 12m volatility negative | 252 daily simple returns sample SD, annualized; raw negative gate direction documented |
| H6 equal weights H1,H3,H4,-H5 positive | exactly four complete sector percentile ranks, inverse H5 rank; composite re-ranked |
| Exactly six primaries | H1–H6; 1m/3m primary and 6m exploratory |
| Stage1 2006–2015 six once | frozen; execution BLOCKED pending coverage and persistent once-only ledger |
| Stage2 2016–Sep2026 sealed | all CLI paths fail closed before reading inputs; no override flag; release workflow deliberately unavailable |
| Only Stage1 passers Stage2 | cannot evaluate any Stage2; future release must bind protocol/input/result hashes and passing signal/horizon list |
| Stage2 exclude 2019/2020 separately | contaminated years fixed; separate evaluation/reporting BLOCKED with Stage2 execution; never pristine |
| Sector/month Spearman, monthly mean | implemented with equal sector weighting |
| NW lags 3/5 | implemented, t exposed; noncontiguous months suppress inference |
| Decile10 minus decile1 | implemented; H5 trade direction reversed; missing tails remain missing |
| Fraction positive monthly IC | direction-aware fraction in summary |
| Stage1 mean >.01, t>3, sign, >=3/4 blocks | pure predicate implemented; blocks frozen in protocol; callers must direction-orient H5; complete coverage required |
| Stage2 sign, t>2, net spread positive | pure predicate implemented; both-leg turnover costs .0015 per dollar traded |
| Later hypotheses and multiple tests | primary 12-test Holm implemented; registration/persistent expanded-family ledger BLOCKED; no variant execution exposed |
| 1000 sector/month shuffles, 99th percentile | seeded permutation utility implemented, H5 direction tested; full-period reporting BLOCKED |
| t+1 signal versus return t warning | warning meaning documented; automatic joined diagnostic NOT IMPLEMENTED, blocks release |
| 1/3/6 decay and turnover | horizon IC summaries and both-leg turnover available; complete decay report and gap-aware portfolio continuity NOT IMPLEMENTED, blocks release |
| Yahoo provisional | explicit in protocol and source policy; no certification |
| Wikipedia insufficient / pre-2006 | explicitly incomplete; reconstruction BLOCKED |
| EDGAR / Alpha sources | explicit existing adapters retained; no fetch performed; full as-filed provenance validation BLOCKED |
| No fake data / no subscriptions | no research data generated; offline fixtures only |
| Missing delisted terminal prices | incomplete sectors withheld; explicit per-security missingness ledger NOT IMPLEMENTED, blocks release |
| Smoke old/exploratory | reports/LEGACY_OUTPUT_NOTICE.md labels all historical outputs; README prohibits interpreting as v2 |
| Tests before Stage2 | offline suite passed; all Stage2 paths sealed |
| No 2006–2026 claim | manifest certified=false; all execution blocked |

Remaining engineering is explicit rather than bypassed: immutable once-only Stage1 ledger, source/calendar certification schema and verifier, atomic Stage1 result/gate logging, passer-only Stage2 release with contamination exclusions, variant registry, lookahead diagnostic, missingness ledger, full decay/turnover reporting and continuity tests. These require further implementation before any data evaluation. The seal is functional; this is not yet a complete v2 research executor.
