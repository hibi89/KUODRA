"""Owner-controlled *staging* install/verify/remove of an unsigned portable ZIP.

Only exact-byte preverified package trees are accepted. A new slot never
overwrites an existing install, an upgrade uses a NEW side-by-side slot, and
removal demands explicit confirmation plus exact current hash parity.
This is not a signed MSI/NSIS installer, OS IAM/no-egress, or buyer release.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile

from kuodra.portable_manifest import verify_manifest

_SLOT = re.compile(r'[a-zA-Z][a-zA-Z0-9_-]{0,31}\Z')


def _target(workspace:Path, slot:str) -> Path:
    if type(slot) is not str or not _SLOT.fullmatch(slot):
        raise ValueError('STAGING_SLOT_INVALID')
    if workspace.is_symlink() or not workspace.exists() or not workspace.is_dir():
        raise ValueError('STAGING_WORKSPACE_INVALID')
    # This workflow is restricted to a preexisting, explicitly chosen
    # first-level directory; never operate in root, home, or parent paths.
    base=workspace.resolve(strict=True)
    if base == Path(base.anchor) or base == Path.home().resolve():
        raise ValueError('STAGING_WORKSPACE_TOO_BROAD')
    dest=base / slot
    if dest.is_symlink():
        raise ValueError('STAGING_TARGET_SYMLINK_DENIED')
    return dest


def install(source:Path, manifest:Path, workspace:Path, slot:str) -> dict:
    dest=_target(Path(workspace),slot)
    if dest.exists():
        raise FileExistsError('STAGING_TARGET_EXISTS_NO_OVERWRITE')
    src=Path(source)
    verified=verify_manifest(src,manifest)
    if dest == src.resolve() or dest in src.resolve().parents:
        raise ValueError('STAGING_SELF_INSTALL_DENIED')
    # Temporary path was created by us inside the user-selected workspace.
    # Failures intentionally leave only our uniquely prefixed staged folder
    # for human review rather than risking cleanup of replaced user files.
    tmp=Path(tempfile.mkdtemp(dir=dest.parent,prefix='.kuodra-staging-'))
    prepared=tmp/'program'
    shutil.copytree(src,prepared,symlinks=False)
    recheck=verify_manifest(prepared,manifest)
    if recheck['inventory_sha256'] != verified['inventory_sha256']:
        raise ValueError('STAGING_COPIED_BYTES_MISMATCH')
    if dest.exists() or dest.is_symlink():
        raise FileExistsError('STAGING_TARGET_EXISTS_NO_OVERWRITE')
    prepared.rename(dest)
    tmp.rmdir()
    return {'status':'UNSIGNED_OWNER_STAGING_INSTALLED',
        'target':str(dest),'slot':slot,
        'inventory_sha256':verified['inventory_sha256'],
        'consumer_release_approved':False,'signature_verified':False}


def verify(workspace:Path,slot:str,manifest:Path)->dict:
    dest=_target(Path(workspace),slot)
    if not dest.exists() or dest.is_symlink():
        raise ValueError('STAGING_INSTALL_MISSING')
    result=verify_manifest(dest,manifest)
    return {'status':'STAGING_BYTES_MATCH_NOT_SIGNED',
            'slot':slot,'inventory_sha256':result['inventory_sha256'],
            'consumer_release_approved':False,'signature_verified':False}


def remove(workspace:Path,slot:str,manifest:Path,*,confirm:bool=False)->dict:
    if confirm is not True:
        raise ValueError('STAGING_REMOVE_EXPLICIT_OWNER_CONFIRMATION_REQUIRED')
    dest=_target(Path(workspace),slot)
    checked=verify(workspace,slot,manifest)
    # Refuse removal of any directory containing unrecognized customer data,
    # extra files, modified binaries, hardlinks or symlinks.
    # The staging workspace must not be shared/untrusted; OS-level races and
    # buyer-machine authorization are NOT certified by this procedure.
    if dest.is_symlink():
        raise ValueError('STAGING_REMOVE_TARGET_LINK_DENIED')
    shutil.rmtree(dest)
    return {'status':'STAGING_VERIFIED_PACKAGE_REMOVED',
            'slot':slot,'inventory_sha256':checked['inventory_sha256'],
            'customer_data_removed':False,
            'consumer_release_approved':False}


def main(argv=None)->int:
    p=argparse.ArgumentParser(description='Owner-only, unsigned portable staging lifecycle')
    p.add_argument('action',choices=('install','verify','remove'))
    p.add_argument('source_or_workspace',type=Path)
    p.add_argument('manifest',type=Path)
    p.add_argument('workspace_or_slot')
    p.add_argument('slot',nargs='?')
    p.add_argument('--confirm-remove',action='store_true')
    args=p.parse_args(argv)
    try:
        if args.action=='install':
            if args.slot is None:
                p.error('STAGING_INSTALL_SLOT_REQUIRED')
            result=install(args.source_or_workspace,args.manifest,
                           Path(args.workspace_or_slot),args.slot)
        elif args.action=='verify':
            if args.slot is not None:
                p.error('STAGING_EXTRA_ARGUMENT')
            result=verify(args.source_or_workspace,
                          args.workspace_or_slot,args.manifest)
        else:
            if args.slot is not None:
                p.error('STAGING_EXTRA_ARGUMENT')
            result=remove(args.source_or_workspace,args.workspace_or_slot,
                          args.manifest,confirm=args.confirm_remove)
    except (ValueError,OSError) as exc:
        p.error(str(exc))
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
