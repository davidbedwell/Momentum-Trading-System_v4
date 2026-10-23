"""GA4 archived predictor registry; all inputs remain research-only until PIT audits."""
import pyarrow.parquet as pq
from pathlib import Path
SOURCE=Path('/opt/mts/thunder-migration/mts-layered-run-20261007/Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet')
GA4_COLUMNS=tuple(c for c in pq.read_schema(SOURCE).names if c.endswith('__v1'))
GA4_FEATURES=tuple('ga4_'+c for c in GA4_COLUMNS)
