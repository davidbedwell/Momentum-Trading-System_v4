# Resume acquisition: STOP / BLOCKED_DATA

Checked from the normal host shell on 2026-10-31, starting 11:16:04 UTC. The claimed restored connectivity could not be reproduced in this executor.

- Python socket.getaddrinfo for stooq.com, query1.finance.yahoo.com and query2.finance.yahoo.com each raised gaierror, errno -3: Temporary failure in name resolution.
- Actual XLK Stooq daily CSV request via shell curl failed on all four attempts (initial plus three retries): exit 6, Could not resolve host: stooq.com. HTTP code 000, no remote IP, zero downloaded bytes.
- Alternative free Yahoo XLK daily chart requests to query1 and query2 each failed on all four attempts with curl exit 6, HTTP 000, no remote IP and zero bytes.
- A separate Stooq CSV request restricted to 1999–2025, initial plus two retries, also exited 6. See stooq_quick.log.
- No TLS connection or HTTP response was reached. These observations establish DNS failure in this host, not a finding about the remote services' health.
- Cloud environment status tool was not exposed; /etc/codex/network-policy.json was absent. No network-policy cause is asserted.

No data were admitted. No IC, spread, CAGR, MDD, Calmar, turnover, cost impact or inference was computed. Discovery and sealed validation remain unevaluated; no holdout evaluation occurred. Under the requested data-access stop condition, analysis implementation was not resumed.

Frozen preregistration verified unchanged: SHA256 23a49749f06cfc44c4c7f5a203e5f18cd04343d5763e7541100c4f977a2f756f. Only files in this experiment's resume_evidence directory were written. No paid sources, main MTS changes, commits or GitHub push.

Evidence: connectivity.txt records DNS checks, exact URLs, curl exits and stderr; stooq_quick.log records the separate CSV retry. The first connectivity probe requested through 2026-10-30 solely to test transport; it obtained zero bytes, and no 2026 data were admitted. The independent CSV probe used the preregistered end year 2025.
