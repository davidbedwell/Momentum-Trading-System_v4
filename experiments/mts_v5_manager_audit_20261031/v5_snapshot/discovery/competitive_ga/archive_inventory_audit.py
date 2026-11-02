"""Read-only inventory of discoverable strategy archives, not an execution claim."""
import json,sqlite3
from pathlib import Path
import pandas as pd
ROOT=Path('/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518')
DB=Path('/opt/mts/ga6/runs/frozen_four_run_20261024/catalogue.sqlite')
OUT=Path('/opt/mts/synthetic-market-lab/reports/manager_archive_inventory.json')
def audit():
 db=sqlite3.connect(DB)
 count=db.execute('select count(*) from chromosomes').fetchone()[0]
 ga7=pd.read_csv(ROOT/'dev79_all_ranked.csv')
 ga6=pd.read_csv(ROOT/'ga6v3_400_dev79_2009_2018.csv')
 result={'status':'ARCHIVE_DISCOVERY_ONLY','ga6_catalogue_records':count,'ga6_prior_replay_rows':len(ga6),'ga7_prior_replay_rows':len(ga7),'ga7_unique_ids_in_prior_replay':int(ga7.chromosome_id.nunique()),'cautions':['GA6 catalogue provenance and uniqueness require verification','GA7 archive grammar requires separate native adapter','GA4 and HORIZONS executable banks not yet located','No shared 2020 cross-family replay','Do not compare GA6 fractional EV against GA7 R multiple']}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2)+'\n')
 return result
if __name__=='__main__':print(json.dumps(audit(),indent=2))
