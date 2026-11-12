"""Offline executable entrypoint CLI dispatch must never imply buyer release."""
from __future__ import annotations
import contextlib
from io import StringIO
import json
import unittest
from unittest.mock import patch, Mock
from desktop.entry import main


class DesktopEntrypointTests(unittest.TestCase):
    def test_selftest_zero_network(self):
        o=StringIO()
        with contextlib.redirect_stdout(o):
            self.assertEqual(main(['--self-test']),0)
        r=json.loads(o.getvalue());self.assertEqual(r['status'],'STAGED_OFFLINE_ONLY')
        self.assertFalse(r['consumer_release_ready'])
    def test_no_unknown_args(self):
        with self.assertRaises(SystemExit): main(['--server'])
    def test_dispatch_offline_only(self):
        mock_module=Mock()
        mock_module.main.return_value=0
        with patch.dict('sys.modules', {'kuodra.cli': mock_module}):
            self.assertEqual(main(['--offline-review','--country','KR']),0)
            mock_module.main.assert_called_once_with(['--country','KR'])

if __name__=='__main__':unittest.main()

class EntrypointVerifierTests(unittest.TestCase):
    def test_verify_export_dispatch(self):
        with patch('kuodra.release_gate.verify_evidence_bundle', return_value={'status':'FILES_INTACT_NOT_AUTHENTICATED'}) as fn:
            o=StringIO()
            with contextlib.redirect_stdout(o):
                self.assertEqual(main(['--verify-export','/tmp/owned','new']),0)
            fn.assert_called_once_with('/tmp/owned','new',require_pdf=False)
            self.assertEqual(json.loads(o.getvalue())['status'],'FILES_INTACT_NOT_AUTHENTICATED')
