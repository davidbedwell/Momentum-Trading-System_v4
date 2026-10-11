"""Hard fail-closed launch boundary: only preflight and dry-run without explicit authorization.
The evolutionary launcher must call require_launch_authorization immediately before compute.
"""
import json,os,pathlib
from scripts.preflight_horizon_evolution_20261010 import check

def require_launch_authorization(*,authorization_path=None):
    readiness=check()
    if readiness['status']!='READY':raise RuntimeError('13_WINDOW_NOT_CERTIFIED: '+','.join(readiness['reasons']))
    if authorization_path is None:raise PermissionError('NEW_STUDY_SERVER_NOT_AUTHORIZED')
    p=pathlib.Path(authorization_path)
    if not p.is_file():raise PermissionError('NEW_STUDY_SERVER_NOT_AUTHORIZED')
    obj=json.loads(p.read_text())
    if obj.get('study')!='THIRTEEN_WINDOW_2_TO_65' or obj.get('authorized') is not True or obj.get('server_id')!=os.uname().nodename:
        raise PermissionError('NEW_STUDY_SERVER_NOT_AUTHORIZED')
    return readiness
