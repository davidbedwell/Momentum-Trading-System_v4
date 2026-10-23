from pathlib import Path
import shutil,subprocess
root=Path('/opt/mts/ga6/runs')
target=root/'ga6_production_200_v1'
assert subprocess.run(['systemctl','is-active','mts-ga6-production-200.service'],capture_output=True,text=True).stdout.strip()=='inactive'
assert target.is_dir() and target.resolve().parent==root.resolve()
files=sum(1 for p in target.rglob('*') if p.is_file())
size=sum(p.stat().st_size for p in target.rglob('*') if p.is_file())
shutil.rmtree(target)
assert not target.exists()
print(f'INVALID_PRODUCTION_OUTPUT_DELETED files={files} bytes={size}')
