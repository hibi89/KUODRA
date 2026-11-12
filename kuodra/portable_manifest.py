"""Deterministic unsigned portable staging inventory.

An integrity manifest is NOT a publisher signature or customer release GO.
Reject missing, extra, symlinked, linked or modified files after relocation.
No network, no deletion, no registry edits and no file contents printed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import stat


_FORBIDDEN_SEGMENTS = {'.env', 'customer-data', 'private-data', 'secrets'}
_MAX_FILES = 10000
_MAX_SINGLE_BYTES = 500_000_000


def _file_sha(path: Path) -> tuple[str,int]:
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError('PORTABLE_LINK_OR_NONFILE_DENIED')
    if before.st_size < 1 or before.st_size > _MAX_SINGLE_BYTES:
        raise ValueError('PORTABLE_FILE_SIZE_DENIED')
    flags = os.O_RDONLY | getattr(os,'O_BINARY',0) | getattr(os,'O_NOFOLLOW',0)
    fd = os.open(path,flags)
    try:
        opened=os.fstat(fd)
        if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or opened.st_ino != before.st_ino
                or opened.st_dev != before.st_dev):
            raise ValueError('PORTABLE_FILE_REPLACED')
        digest=sha256()
        n=0
        while True:
            part=os.read(fd,1048576)
            if not part:
                break
            digest.update(part)
            n+=len(part)
            if n>_MAX_SINGLE_BYTES:
                raise ValueError('PORTABLE_FILE_SIZE_DENIED')
        after=os.fstat(fd)
        again=path.lstat()
        if (n != before.st_size or after.st_size != before.st_size
                or after.st_mtime_ns != before.st_mtime_ns
                or again.st_ino != before.st_ino or again.st_dev != before.st_dev):
            raise ValueError('PORTABLE_FILE_MUTATED_DURING_HASH')
        return digest.hexdigest(),n
    finally:
        os.close(fd)


def inventory(folder: str | Path) -> dict:
    root=Path(folder)
    if not root.is_dir() or root.is_symlink():
        raise ValueError('PORTABLE_DIRECTORY_INVALID')
    entries=[]
    for p in root.rglob('*'):
        if p.is_symlink():
            raise ValueError('PORTABLE_SYMLINK_DENIED')
        rel=p.relative_to(root).as_posix()
        if any(seg.lower() in _FORBIDDEN_SEGMENTS or seg.lower().startswith('.env.')
               for seg in p.relative_to(root).parts):
            raise ValueError('PORTABLE_PRIVATE_PATH_DENIED')
        if p.is_dir():
            continue
        if not p.is_file():
            raise ValueError('PORTABLE_SPECIAL_FILE_DENIED')
        digest,n=_file_sha(p)
        entries.append({'path':rel,'sha256':digest,'bytes':n})
        if len(entries)>_MAX_FILES:
            raise ValueError('PORTABLE_TOO_MANY_FILES')
    if not entries:
        raise ValueError('PORTABLE_EMPTY')
    entries.sort(key=lambda item:item['path'])
    names=[x['path'] for x in entries]
    if len({x.casefold() for x in names}) != len(names):
        raise ValueError('PORTABLE_CASE_INSENSITIVE_COLLISION')
    base={'schema':'kuodra.unsigned-portable-inventory.v1','files':entries}
    serialized=json.dumps(base,sort_keys=True,separators=(',',':')).encode('utf-8')
    return {**base,'inventory_sha256':sha256(serialized).hexdigest(),
            'signature_verified':False,'consumer_release_approved':False}


def create_manifest(folder: str | Path, output: str | Path) -> dict:
    result=inventory(folder)
    path=Path(output)
    if path.exists() or path.is_symlink():
        raise FileExistsError('PORTABLE_MANIFEST_NO_OVERWRITE')
    if path.parent.resolve() == Path(folder).resolve():
        raise ValueError('PORTABLE_MANIFEST_MUST_BE_OUTSIDE_FOLDER')
    blob=json.dumps(result,indent=2,sort_keys=True).encode('utf-8')
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'wb') as file:
        file.write(blob)
        file.flush()
        os.fsync(file.fileno())
    return result


def verify_manifest(folder: str | Path, manifest: str | Path) -> dict:
    manifest_path=Path(manifest)
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError('PORTABLE_MANIFEST_UNAVAILABLE')
    raw=manifest_path.read_bytes()
    if not 0<len(raw)<=3_000_000:
        raise ValueError('PORTABLE_MANIFEST_SIZE_DENIED')
    try:
        def pairs_unique(items):
            d={}
            for k,v in items:
                if k in d:
                    raise ValueError('PORTABLE_MANIFEST_DUPLICATE_JSON_KEY')
                d[k]=v
            return d
        expected=json.loads(raw.decode('utf-8','strict'),object_pairs_hook=pairs_unique)
    except (UnicodeError,ValueError) as exc:
        raise ValueError('PORTABLE_MANIFEST_JSON_INVALID') from exc
    if type(expected) is not dict or set(expected)!={'schema','files',
            'inventory_sha256','signature_verified','consumer_release_approved'}:
        raise ValueError('PORTABLE_MANIFEST_SCHEMA_INVALID')
    if expected['signature_verified'] is not False or expected['consumer_release_approved'] is not False:
        raise ValueError('PORTABLE_FAKE_RELEASE_APPROVAL_DENIED')
    measured=inventory(folder)
    if expected != measured:
        raise ValueError('PORTABLE_MANIFEST_CONTENT_MISMATCH')
    return {
        'status':'UNSIGNED_PORTABLE_BYTES_MATCH_NO_AUTHENTICATION',
        'file_count':len(measured['files']),
        'total_bytes':sum(x['bytes'] for x in measured['files']),
        'inventory_sha256':measured['inventory_sha256'],
        'consumer_release_approved':False,
        'signature_verified':False,
    }


def main(argv=None):
    p=argparse.ArgumentParser(description='KUODRA staging-only unsigned ZIP manifest')
    p.add_argument('action',choices=('create','verify'))
    p.add_argument('folder',type=Path)
    p.add_argument('manifest',type=Path)
    args=p.parse_args(argv)
    try:
        result=(create_manifest(args.folder,args.manifest) if args.action=='create'
                else verify_manifest(args.folder,args.manifest))
    except (ValueError,OSError) as exc:
        p.error(str(exc))
    summary={'status':'UNSIGNED_MANIFEST_CREATED' if args.action=='create' else result['status'],
        'inventory_sha256':result['inventory_sha256'],
        'file_count':len(result['files']) if args.action=='create' else result['file_count'],
        'signature_verified':False,'consumer_release_approved':False}
    print(json.dumps(summary,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
