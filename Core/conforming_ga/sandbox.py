"""Unprivileged Linux Landlock read sandbox for fold isolation."""
from __future__ import annotations
import ctypes,os
from pathlib import Path
libc=ctypes.CDLL(None,use_errno=True)
SYS_CREATE=444;SYS_ADD=445;SYS_RESTRICT=446
LANDLOCK_CREATE_RULESET_VERSION=1
LANDLOCK_RULE_PATH_BENEATH=1
PR_SET_NO_NEW_PRIVS=38
ACCESS_EXECUTE=1<<0
ACCESS_READ_FILE=1<<2
ACCESS_READ_DIR=1<<3
HANDLED=ACCESS_EXECUTE|ACCESS_READ_FILE|ACCESS_READ_DIR
class RulesetAttr(ctypes.Structure): _fields_=[("handled_access_fs",ctypes.c_uint64)]
class PathBeneathAttr(ctypes.Structure): _fields_=[("allowed_access",ctypes.c_uint64),("parent_fd",ctypes.c_int)]
def abi_version():
    r=libc.syscall(SYS_CREATE,0,0,LANDLOCK_CREATE_RULESET_VERSION)
    return int(r)
def restrict_reads(allowed_paths):
    if abi_version()<1:raise RuntimeError("Landlock unavailable")
    attr=RulesetAttr(HANDLED)
    fd=libc.syscall(SYS_CREATE,ctypes.byref(attr),ctypes.sizeof(attr),0)
    if fd<0:raise OSError(ctypes.get_errno(),"landlock_create_ruleset")
    try:
        for raw in allowed_paths:
            p=Path(raw).resolve()
            flags=getattr(os,"O_PATH",0)|os.O_CLOEXEC
            pfd=os.open(str(p),flags)
            try:
                rule=PathBeneathAttr(HANDLED,pfd)
                rc=libc.syscall(SYS_ADD,fd,LANDLOCK_RULE_PATH_BENEATH,ctypes.byref(rule),0)
                if rc<0:raise OSError(ctypes.get_errno(),f"landlock_add_rule {p}")
            finally:os.close(pfd)
        if libc.prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0)!=0:raise OSError(ctypes.get_errno(),"prctl")
        if libc.syscall(SYS_RESTRICT,fd,0)!=0:raise OSError(ctypes.get_errno(),"landlock_restrict_self")
    finally:os.close(fd)
