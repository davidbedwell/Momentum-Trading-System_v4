from scripts.thirteen_window_launch_guard_20261011 import require_launch_authorization
try:require_launch_authorization()
except (PermissionError,RuntimeError):pass
else:raise AssertionError('launch without certification/authorization')
print('LAUNCH_GUARD_FAIL_CLOSED_PASS')
