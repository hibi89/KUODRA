"""P95 local GUI-controller regression without opening native windows.

These tests cannot prove that a real buyer's Win10/11 GUI renders correctly.
"""
from __future__ import annotations
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from kuodra.gui import run_selected
from kuodra.release_gate import verify_evidence_bundle

ROOT=Path(__file__).resolve().parents[1]
KR=ROOT/'fixtures'/'synthetic'/'kr_dart.json'
US=ROOT/'fixtures'/'synthetic'/'us_companyfacts.json'


class DeveloperGuiControllerTests(unittest.TestCase):
    def test_kr_pdf_and_receipt_stay_hold(self):
        with tempfile.TemporaryDirectory() as td:
            report,paths=run_selected(country='KR',issuer_id='99998888',
                as_of='2025-11-12',source=str(KR),output_dir=td,
                name='p95',pdf=True)
            self.assertEqual(set(paths),{'json','html','pdf'})
            verified=verify_evidence_bundle(td,'p95',require_pdf=True)
            self.assertEqual(verified['status'],'UNSIGNED_RECEIPT_MATCHED_NOT_AUTHENTICATED')
            self.assertEqual(verified['guard'],'HOLD')
            self.assertFalse(verified['publisher_authenticated'])
            self.assertFalse(verified['commercial_rights_verified'])
            self.assertTrue((Path(td)/'p95.pdf').read_bytes().startswith(b'%PDF-'))
            self.assertFalse(report['trade_executed'])

    def test_gui_selected_source_cannot_use_network(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(socket.socket,'connect',
                              side_effect=AssertionError('GUI_NETWORK_ACCESS_DENIED')):
                report,paths=run_selected(country='US',issuer_id='0009999888',
                    as_of='2025-11-12',source=str(US),output_dir=td,name='offline')
            self.assertFalse(report['source_verified'])
            self.assertEqual(report['guard'],'HOLD')
            self.assertTrue(Path(paths['html']['path']).exists())

    def test_unsupported_country_rejected_before_file_processing(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'COUNTRY_UNSUPPORTED'):
                run_selected(country='ZZ',issuer_id='99998888',
                     as_of='2025-11-12',source=str(KR),output_dir=td)

    def test_pdf_failed_export_does_not_destroy_user_file(self):
        with tempfile.TemporaryDirectory() as td:
            original=Path(td)/'trial.pdf'
            original.write_bytes(b'CUSTOMER_DO_NOT_DELETE')
            with self.assertRaises(FileExistsError):
                run_selected(country='KR',issuer_id='99998888',
                    as_of='2025-11-12',source=str(KR),
                    output_dir=td,name='trial',pdf=True)
            self.assertEqual(original.read_bytes(),b'CUSTOMER_DO_NOT_DELETE')

    def test_no_source_is_denied(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises((ValueError,FileNotFoundError)):
                run_selected(country='US',issuer_id='0009999888',
                    as_of='2025-11-12',source=str(Path(td)/'missing.json'),
                    output_dir=td)


if __name__=='__main__':
    unittest.main()
