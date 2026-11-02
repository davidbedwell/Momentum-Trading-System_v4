Start with [RESULTS.md](RESULTS.md) for results, assumptions, deviations and limitations.

Reproduce with `bash experiments/dev79_four_policy_comparison_20261101/run.sh` from repository root. Uses `/opt/mts/.venv`, pins one available CPU and numerical threads to one. No network, GA or production writes. `build.py` creates the isolated harness from the completed manager; `comparison.py` is the actual executable snapshot.
