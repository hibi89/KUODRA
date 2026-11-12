"""P95 OSS dependency evidence inventory, NOT a license clearance.

Collects installed distribution versions and license metadata without
transferring source code, keys, customer records or package binaries.
A manifest is only a checklist for owner review of the *actual* Windows
PyInstaller bundled DLLs, fonts, assets and redistributables.
"""
from __future__ import annotations
import argparse
from importlib import metadata
import json
import re
import sys

_CORE=('numpy','scipy','scikit-learn','reportlab')
_OPTIONAL=('pyinstaller','pillow')
_SAFE=re.compile(r'[A-Za-z0-9_. +:/()\-]{1,120}\Z')


def _short(value: str | None) -> str:
    if not value:
        return 'NOT_DECLARED_REVIEW_REQUIRED'
    value=' '.join(value.split())[:120]
    return value if _SAFE.fullmatch(value) else 'NONTRIVIAL_LICENSE_TEXT_MANUAL_REVIEW'


def inventory(*, require_core: bool=False) -> dict:
    entries=[]
    for name in _CORE+_OPTIONAL:
        try:
            dist=metadata.distribution(name)
        except metadata.PackageNotFoundError:
            if require_core and name in _CORE:
                raise ValueError('REQUIRED_DISTRIBUTION_MISSING:'+name) from None
            entries.append({'distribution':name,'status':'NOT_INSTALLED',
                'license_review_approved':False})
            continue
        meta=dist.metadata
        label=_short(meta.get('License-Expression') or meta.get('License'))
        if label=='NOT_DECLARED_REVIEW_REQUIRED':
            tags=[str(x) for x in meta.get_all('Classifier',[]) if 'License ::' in str(x)]
            if tags:
                label=_short('; '.join(tags))
        entries.append({'distribution':name,'version':str(dist.version),
            'metadata_license_hint':label,
            'status':'MANUAL_LICENSE_AND_BUNDLED_NOTICE_REVIEW_REQUIRED',
            'license_review_approved':False})
    return {'schema':'kuodra.oss-dependency-ledger.v1',
            'runtime_python':f'{sys.version_info.major}.{sys.version_info.minor}',
            'distributions':entries,
            'completeness':'SELECTED_RUNTIME_PACKAGES_ONLY_NOT_ALL_TRANSITIVE_DLLS',
            'windows_bundle_audited':False,'commercial_distribution_approved':False}


def main(argv=None) -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--require-core',action='store_true')
    args=p.parse_args(argv)
    try:
        report=inventory(require_core=args.require_core)
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps(report,sort_keys=True,ensure_ascii=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
