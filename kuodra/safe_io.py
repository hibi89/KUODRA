"""Read-only bounded evidence-file open with fd/path identity rechecks.

Best effort cross-platform hardlink/symlink/race defense; not a sandbox,
not a host-level ACL and not a guarantee against malicious filesystem drivers.
"""
from __future__ import annotations
import os
from pathlib import Path
import stat


def read_bounded_local(path: str | Path, *, limit: int=1_000_000) -> bytes:
    if type(limit) is not int or not 0 < limit <= 10_000_000:
        raise ValueError('LOCAL_SOURCE_LIMIT_INVALID')
    p=Path(path)
    try:
        before=os.lstat(p)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or not 0 < before.st_size <= limit:
            raise ValueError('LOCAL_SOURCE_FILE_POLICY_DENIED')
        flags=os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_CLOEXEC', 0) | getattr(os, 'O_NOFOLLOW', 0)
        fd=os.open(p,flags)
        try:
            opened=os.fstat(fd)
            if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                    or opened.st_ino != before.st_ino or opened.st_dev != before.st_dev
                    or not 0 < opened.st_size <= limit):
                raise ValueError('LOCAL_SOURCE_RACE_OR_LINK')
            chunks=[];total=0
            while True:
                chunk=os.read(fd,min(65536,limit+1-total))
                if not chunk:break
                chunks.append(chunk);total+=len(chunk)
                if total>limit:raise ValueError('LOCAL_SOURCE_TOO_LARGE')
            after=os.fstat(fd)
            current=os.lstat(p)
            if (current.st_ino != opened.st_ino or current.st_dev != opened.st_dev
                    or after.st_size != opened.st_size or after.st_mtime_ns != opened.st_mtime_ns
                    or total != opened.st_size):
                raise ValueError('LOCAL_SOURCE_MUTATED_DURING_READ')
            return b''.join(chunks)
        finally:os.close(fd)
    except (FileNotFoundError, IsADirectoryError, PermissionError) as exc:
        raise ValueError('LOCAL_SOURCE_UNAVAILABLE') from exc
