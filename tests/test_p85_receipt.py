"""Unsigned receipt is deterministic and detects accidental report changes.

No claim of issuer authenticity or resistance to a malicious attacker able to
rewrite both receipt and report. Tests use only synthetic local fixture.
"""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest

from kuodra.cli import analyze_bytes
from kuodra.report import export_local
from kuodra.release_gate import verify_evidence_bundle

ROOT=Path(__file__).resolve().parents[1]
KR=ROOT/'fixtures'/'synthetic'/'kr_dart.json'

def _review():
    return analyze_bytes(KR.read_bytes(),country='KR',issuer_id='99998888',as_of='2025-11-12')

class ReceiptTests(unittest.TestCase):
    def test_receipt_consistent_and_unsigned(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            out=export_local(_review(),root,'proof')
            self.assertEqual(set(out),{'json','html'})
            receipt=root/'proof.receipt.json'
            self.assertTrue(receipt.is_file())
            v=verify_evidence_bundle(root,'proof')
            self.assertEqual(v['status'],'UNSIGNED_RECEIPT_MATCHED_NOT_AUTHENTICATED')
            self.assertEqual(len(v['receipt_sha256']),64)
            self.assertFalse(v['signature_verified'])
            self.assertFalse(v['publisher_authenticated'])
    def test_receipt_catches_mutated_financial_number(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);export_local(_review(),root,'proof')
            target=root/'proof.json'
            doc=json.loads(target.read_text(encoding='utf8'))
            doc['evidence'][0]['amount']='999999'
            target.write_text(json.dumps(doc),encoding='utf8')
            with self.assertRaisesRegex(ValueError,'RECEIPT_HASH_MISMATCH'):
                verify_evidence_bundle(root,'proof')
    def test_receipt_catches_mutated_html_even_if_hold_visible(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);export_local(_review(),root,'proof')
            target=root/'proof.html'
            target.write_text(target.read_text(encoding='utf8').replace('cash_conversion','cash_conversion_CHANGE'))
            with self.assertRaisesRegex(ValueError,'RECEIPT_HASH_MISMATCH'):
                verify_evidence_bundle(root,'proof')
    def test_old_bundle_distinctly_unanchored(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);export_local(_review(),root,'proof')
            (root/'proof.receipt.json').unlink()
            v=verify_evidence_bundle(root,'proof')
            self.assertEqual(v['status'],'FORMAT_CHECKED_NO_SAVED_RECEIPT')
            self.assertIsNone(v['receipt_sha256'])
    def test_receipt_untrusted_modification_fails_scope(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);export_local(_review(),root,'proof')
            p=root/'proof.receipt.json'
            item=json.loads(p.read_text())
            item['commercial_rights_verified']=True
            p.write_text(json.dumps(item))
            with self.assertRaisesRegex(ValueError,'RECEIPT_SCOPE_INVALID'):
                verify_evidence_bundle(root,'proof')
    def test_receipt_itself_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);export_local(_review(),root,'proof')
            (root/'proof.html').unlink()
            (root/'proof.json').unlink()
            with self.assertRaises(FileExistsError):
                export_local(_review(),root,'proof')

if __name__=='__main__':unittest.main()
