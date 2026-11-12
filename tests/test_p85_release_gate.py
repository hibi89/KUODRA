"""Evidence export cannot be promoted to authenticated/sale-ready status."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from kuodra.release_gate import verify_evidence_bundle


def fixture(root: Path, *, pdf=False) -> None:
    report={'schema':'kuodra.offline-review.v1','issuer_id':'99998888',
            'guard':'HOLD','trade_executed':False,
            'rights_verified':False,'source_verified':False,
            'evidence':[{'metric':'revenue'}]}
    (root/'review.json').write_text(json.dumps(report),encoding='utf8')
    (root/'review.html').write_text('<html>99998888 HOLD <table></table></html>',encoding='utf8')
    if pdf:(root/'review.pdf').write_bytes(b'%PDF-1.4\n1 0 obj << >> endobj\n%%EOF\n')


class EvidenceGateTests(unittest.TestCase):
    def test_offline_report_ok_never_publisher_ok(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fixture(root, pdf=True)
            r=verify_evidence_bundle(root,require_pdf=True)
            self.assertEqual(len(r['file_hashes']),3)
            self.assertEqual(r['guard'],'HOLD')
            self.assertFalse(r['publisher_authenticated'])
    def test_denies_wrong_guard(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fixture(root)
            x=json.loads((root/'review.json').read_text());x['guard']='APPROVE'
            (root/'review.json').write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,'RELEASE_HOLD'):verify_evidence_bundle(root)
    def test_denies_html_injection(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fixture(root)
            (root/'review.html').write_text('<html>99998888 HOLD<script>alert(1)</script></html>')
            with self.assertRaisesRegex(ValueError,'HTML_CONTENT'):verify_evidence_bundle(root)
    def test_denies_report_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fixture(root)
            raw=root/'out.txt';raw.write_text((root/'review.html').read_text())
            (root/'review.html').unlink()
            try:(root/'review.html').symlink_to(raw)
            except (OSError,NotImplementedError):self.skipTest('symlink privileges missing')
            with self.assertRaisesRegex(ValueError,'LINK'):verify_evidence_bundle(root)
    def test_denies_hardlink(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fixture(root)
            import os
            os.link(root/'review.json',root/'copy.json')
            with self.assertRaisesRegex(ValueError,'SCOPE_DENIED'):verify_evidence_bundle(root)
    def test_denies_missing_pdf(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fixture(root)
            with self.assertRaisesRegex(ValueError,'LINK'):verify_evidence_bundle(root,require_pdf=True)
    def test_denies_invalid_stem(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'STEM'):verify_evidence_bundle(td,'../evil')
    def test_denies_pdf_fake_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fixture(root, pdf=True)
            (root/'review.pdf').write_bytes(b'fake pdf')
            with self.assertRaisesRegex(ValueError,'PDF_HEADER'):verify_evidence_bundle(root,require_pdf=True)
    def test_denies_unsigned_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);fixture(root)
            x=json.loads((root/'review.json').read_text());x['evidence']=[]
            (root/'review.json').write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,'RELEASE_HOLD'):verify_evidence_bundle(root)

if __name__=='__main__':unittest.main()
