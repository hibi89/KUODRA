"""The Windows staging entry must never fetch without owner consent.

The released-sounding --official-review route is NOT a publisher auth,
license grant, or a buyer-ready signed installer.
"""
from __future__ import annotations
import json
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout,redirect_stderr
from io import StringIO

from desktop.entry import main

class OptInDesktopRoutingTests(unittest.TestCase):
    def test_staged_selftest_includes_official_module_but_no_network(self):
        out=StringIO()
        with patch('kuodra.source_client._transport',
                   side_effect=AssertionError('UNEXPECTED_NETWORK')) as network:
            with redirect_stdout(out):
                self.assertEqual(main(['--self-test']),0)
        obj=json.loads(out.getvalue())
        self.assertFalse(obj['consumer_release_ready'])
        self.assertEqual(obj['status'],'STAGED_OFFLINE_ONLY')
        network.assert_not_called()

    def test_official_gateway_requires_consent_before_transport(self):
        with patch('kuodra.official_cli.analyze_opted_in_once',
                   side_effect=AssertionError('UNEXPECTED_NETWORK')) as gateway:
            with redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as exc:
                    main(['--official-review','--country','US',
                          '--issuer-id','0009999888','--as-of','2025-11-12',
                          '--output-dir','/tmp/not-supplied'])
        self.assertEqual(exc.exception.code,2)
        gateway.assert_not_called()

    def test_route_calls_exact_official_cli_arguments(self):
        args=['--country','US','--issuer-id','0009999888',
              '--as-of','2025-11-12','--consent']
        with patch('kuodra.official_cli.main',return_value=0) as official:
            self.assertEqual(main(['--official-review']+args),0)
        official.assert_called_once_with(args)


if __name__=='__main__':
    unittest.main()
