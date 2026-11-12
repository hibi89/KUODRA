"""Opt-in CLI contract: no network without explicit consent, no key in output."""
from __future__ import annotations
from contextlib import redirect_stdout,redirect_stderr
from io import StringIO
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from kuodra.official_cli import main
from kuodra.cli import analyze_bytes

ROOT=Path(__file__).resolve().parents[1]
KR=ROOT/'fixtures'/'synthetic'/'kr_dart.json'

def fake_report(*args,**kwargs):
    r=analyze_bytes(KR.read_bytes(),country='KR',issuer_id='99998888',
                    as_of='2025-11-12')
    r['official_source_request']={
        'provider':'DART','fixed_url_no_credential':
        'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json',
        'input_sha256':'a'*64,
        'source_publisher_authenticated':False,
        'commercial_rights_verified':False}
    return r

class OfficialCliTests(unittest.TestCase):
    def test_no_consent_never_reads_creds_or_network(self):
        with tempfile.TemporaryDirectory() as td:
            with patch('kuodra.official_cli.analyze_opted_in_once',
                       side_effect=AssertionError('NETWORK_FORBIDDEN')) as transport:
                with redirect_stderr(StringIO()):
                    with self.assertRaises(SystemExit) as raised:
                        main(['--country','KR','--issuer-id','99998888',
                              '--as-of','2025-11-12','--business-year','2024',
                              '--output-dir',td])
            self.assertEqual(raised.exception.code,2)
            transport.assert_not_called()
    def test_explicit_consent_returns_hold_without_leaking_key(self):
        key='a'*40
        with tempfile.TemporaryDirectory() as td:
            with patch.dict('os.environ', {'KUODRA_DART_API_KEY':key}):
                with patch('kuodra.official_cli.analyze_opted_in_once',
                           side_effect=fake_report) as gateway:
                    output=StringIO()
                    with redirect_stdout(output):
                        self.assertEqual(main([
                            '--country','KR','--issuer-id','99998888',
                            '--as-of','2025-11-12','--business-year','2024',
                            '--output-dir',td,'--name','test','--consent']),0)
            report=json.loads(output.getvalue())
            self.assertEqual(report['guard'],'HOLD')
            self.assertEqual(report['network_requests'],1)
            self.assertFalse(report['commercial_rights_verified'])
            self.assertNotIn(key,output.getvalue())
            self.assertNotIn(key,(Path(td)/'test.json').read_text(encoding='utf-8'))
            self.assertNotIn(key,(Path(td)/'test.receipt.json').read_text(encoding='utf-8'))
            self.assertEqual(gateway.call_args.kwargs['dart_api_key'],key)
    def test_kr_no_year_fails_before_transport(self):
        with tempfile.TemporaryDirectory() as td:
            with patch('kuodra.official_cli.analyze_opted_in_once') as gateway:
                with redirect_stderr(StringIO()):
                    with self.assertRaises(SystemExit):
                        main(['--country','KR','--issuer-id','99998888',
                              '--as-of','2025-11-12','--consent',
                              '--output-dir',td])
                gateway.assert_not_called()
    def test_us_disallows_business_year_and_official_input_key(self):
        with tempfile.TemporaryDirectory() as td:
            with patch('kuodra.official_cli.analyze_opted_in_once') as gateway:
                with redirect_stderr(StringIO()):
                    with self.assertRaises(SystemExit):
                        main(['--country','US','--issuer-id','0009999888',
                              '--as-of','2025-11-12','--business-year','2024',
                              '--consent','--output-dir',td])
                gateway.assert_not_called()
    def test_cli_does_not_log_an_env_key_when_missing(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.dict('os.environ', {'KUODRA_DART_API_KEY':'missing'},
                            clear=False):
                captured=StringIO()
                with redirect_stderr(captured):
                    with self.assertRaises(SystemExit):
                        main(['--country','KR','--issuer-id','99998888',
                              '--as-of','2025-11-12','--business-year','2024',
                              '--consent','--output-dir',td])
                self.assertNotIn('crtfc_key=',captured.getvalue())


if __name__=='__main__':
    unittest.main()
