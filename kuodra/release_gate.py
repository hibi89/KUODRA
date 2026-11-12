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
    pdf_path = root / (stem + '.pdf')
    if require_pdf or pdf_path.exists() or pdf_path.is_symlink():
        files['pdf'] = pdf_path
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
    hashes = {ext: hashlib.sha256(blob).hexdigest() for ext, blob in data.items()}
    receipt_path = root / (stem + '.receipt.json')
    receipt_digest = None
    status = 'FORMAT_CHECKED_NO_SAVED_RECEIPT'
    if receipt_path.exists() or receipt_path.is_symlink():
        if receipt_path.is_symlink() or not receipt_path.is_file():
            raise ValueError('VERIFY_RECEIPT_LINK_DENIED')
        if receipt_path.stat().st_nlink != 1 or not 0 < receipt_path.stat().st_size <= 10_000:
            raise ValueError('VERIFY_RECEIPT_SCOPE_DENIED')
        rb = receipt_path.read_bytes()
        receipt_digest = hashlib.sha256(rb).hexdigest()
        try:
            receipt = json.loads(rb.decode('utf-8','strict'))
        except (UnicodeError,ValueError) as exc:
            raise ValueError('VERIFY_RECEIPT_INVALID') from exc
        if (type(receipt) is not dict or
                set(receipt) != {'schema','issuer_id','guard','source_authenticated',
                                 'commercial_rights_verified','artifacts'} or
                receipt['schema'] != 'kuodra.unsigned-evidence-receipt.v1' or
                receipt['issuer_id'] != r['issuer_id'] or receipt['guard'] != 'HOLD' or
                receipt['source_authenticated'] is not False or
                receipt['commercial_rights_verified'] is not False or
                type(receipt['artifacts']) is not dict or
                set(receipt['artifacts']) != set(data)):
            raise ValueError('VERIFY_RECEIPT_SCOPE_INVALID')
        for ext, content in data.items():
            item = receipt['artifacts'][ext]
            if (type(item) is not dict or set(item) != {'sha256','bytes'}
                    or item['sha256'] != hashes[ext] or item['bytes'] != len(content)):
                raise ValueError('VERIFY_RECEIPT_HASH_MISMATCH')
        status = 'UNSIGNED_RECEIPT_MATCHED_NOT_AUTHENTICATED'
    return {'schema': 'kuodra.export-verification.v1', 'status': status,
            'guard': 'HOLD', 'publisher_authenticated': False,
            'commercial_rights_verified': False, 'market_predictions_verified': False,
            'receipt_sha256':receipt_digest, 'signature_verified':False,
            'file_hashes': hashes, 'evidence_count': len(r['evidence']),
            'report_schema': r['schema']}
