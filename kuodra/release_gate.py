"""Read-only independent verifier for local KUODRA evidence exports.

This is not a signature, publisher authentication or regulatory clearance.
Do not treat SHA-256 equality as proof of original document authority.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re

_STEM = re.compile(r'[A-Za-z0-9_-]{1,48}\Z')


def verify_evidence_bundle(directory: str | Path, stem: str = 'review', *, require_pdf: bool = False) -> dict:
    if type(stem) is not str or _STEM.fullmatch(stem) is None:
        raise ValueError('VERIFY_STEM_INVALID')
    root = Path(directory)
    if not root.is_dir() or root.is_symlink():
        raise ValueError('VERIFY_DIRECTORY_INVALID')
    files = {ext: root / (stem + '.' + ext) for ext in ('json', 'html')}
    if require_pdf:
        files['pdf'] = root / (stem + '.pdf')
    data = {}
    for ext, path in files.items():
        if path.is_symlink() or not path.is_file():
            raise ValueError('VERIFY_FILE_MISSING_OR_LINK')
        before = path.stat()
        if before.st_nlink != 1 or not 0 < before.st_size <= 3_000_000:
            raise ValueError('VERIFY_FILE_SCOPE_DENIED')
        with path.open('rb') as reader:
            content = reader.read(3_000_001)
        after = path.stat()
        if (len(content) != before.st_size or before.st_ino != after.st_ino
                or before.st_mtime_ns != after.st_mtime_ns):
            raise ValueError('VERIFY_CONCURRENT_MUTATION')
        data[ext] = content
    try:
        r = json.loads(data['json'].decode('utf-8', 'strict'))
    except (UnicodeError, ValueError) as exc:
        raise ValueError('VERIFY_REPORT_JSON_INVALID') from exc
    if (type(r) is not dict or r.get('schema') != 'kuodra.offline-review.v1'
            or r.get('guard') != 'HOLD' or r.get('trade_executed') is not False
            or r.get('rights_verified') is not False or r.get('source_verified') is not False
            or not isinstance(r.get('evidence'), list) or not r['evidence']):
        raise ValueError('VERIFY_RELEASE_HOLD_REQUIRED')
    html = data['html'].decode('utf-8', 'strict')
    if ('<html' not in html or '</html>' not in html
            or 'HOLD' not in html or r.get('issuer_id', '') not in html
            or '<script' in html.lower()):
        raise ValueError('VERIFY_HTML_CONTENT_INVALID')
    if require_pdf:
        pdf = data['pdf']
        if not pdf.startswith(b'%PDF-') or b'%%EOF' not in pdf[-256:]:
            raise ValueError('VERIFY_PDF_HEADER_INVALID')
    return {'schema': 'kuodra.export-verification.v1', 'status': 'FILES_INTACT_NOT_AUTHENTICATED',
            'guard': 'HOLD', 'publisher_authenticated': False,
            'commercial_rights_verified': False, 'market_predictions_verified': False,
            'file_hashes': {ext: hashlib.sha256(blob).hexdigest() for ext, blob in data.items()},
            'evidence_count': len(r['evidence']), 'report_schema': r['schema']}
