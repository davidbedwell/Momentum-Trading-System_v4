# A/B/C and R-1 exclusively govern crash-state boundaries

Status: USER APPROVED clarification 2026-10-09.

- A/B/C is the exclusive trigger for entering crash/Defensive state. The cash-first liquidation response occurs on that transition.
- R-1 is the exclusive condition for ending crash/Defensive state and restoring Normal eligibility. Do not infer recovery from elapsed sessions, trade results, quiet market conditions, or an arbitrary time limit.
- A/B/C remains dominant if crash and recovery evidence are simultaneously present; R-1 terminates Defensive only when crash detection is absent.
- During Defensive, independently evaluate short-duration LONG and SHORT trades after cash-transition confirmation. Repeated qualifying entries are possible, but no long-horizon exposure before R-1.
- A/B/C and R-1 control market STATE duration, not individual position holding duration. Short-term position exit and maximum duration require separate evidence-based rules; do not silently assign a fixed cutoff or assume a trade may remain open until R-1.
- The state controller is research-only until connected to verified PIT detector inputs, brokerage execution, and lifecycle tests.
