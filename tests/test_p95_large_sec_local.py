"""P95 candidate: issuer-level SEC local CompanyFacts is not restricted to 1MB.

Official SEC payloads can contain many concepts and years. All tests use a
locally constructed synthetic CompanyFacts-shaped object; no network, secret,
stock quote, real issuer, or external data transmission.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import unittest

from kuodra.cli import main as cli_main
from kuodra.gui import run_selected
from kuodra.safe_io import source_limit_for, read_bounded_local

ROOT = Path(__file__).resolve().parents[1]
US = ROOT / 'fixtures' / 'synthetic' / 'us_companyfacts.json'
KR = ROOT / 'fixtures' / 'synthetic' / 'kr_dart.json'


class P95LargeOfficialShapeTests(unittest.TestCase):
    @staticmethod
    def oversized_us_bytes():
        obj = json.loads(US.read_text(encoding='utf-8'))
        # an unknown official us-gaap concept must not be interpreted as revenue
        obj['facts']['us-gaap']['UnknownSyntheticConcept'] = {
            'label':'Synthetic-only appendix',
            'description':'n' * 1_240_000,
            'units': {'USD': []}}
        return json.dumps(obj,ensure_ascii=False).encode('utf-8')

    def test_country_limits_are_explicit(self):
        self.assertEqual(source_limit_for('US'),10_000_000)
        self.assertEqual(source_limit_for('KR'),1_000_000)
        with self.assertRaisesRegex(ValueError,'COUNTRY_UNSUPPORTED'):
            source_limit_for('XY')

    def test_us_large_companyfacts_via_cli(self):
        raw = self.oversized_us_bytes()
        self.assertGreater(len(raw),1_000_000)
        self.assertLess(len(raw),10_000_000)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            source=root/'companyfacts.json';source.write_bytes(raw)
            dest=root/'output';dest.mkdir()
            output=StringIO()
            with redirect_stdout(output):
                self.assertEqual(cli_main([
                    '--country','US','--issuer-id','0009999888',
                    '--as-of','2025-11-12','--source',str(source),
                    '--output-dir',str(dest),'--name','large',
                ]),0)
            result=json.loads((dest/'large.json').read_text(encoding='utf-8'))
            self.assertEqual(result['guard'],'HOLD')
            self.assertEqual(result['engine_a'],'UNAVAILABLE_NO_LICENSED_MARKET_DATA')
            self.assertEqual(len(result['evidence']),14)
            self.assertFalse(result['rights_verified'])
            self.assertEqual(json.loads(output.getvalue())['guard'],'HOLD')

    def test_us_large_companyfacts_via_gui_function(self):
        raw=self.oversized_us_bytes()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'input.json';source.write_bytes(raw)
            output=root/'out';output.mkdir()
            report,paths=run_selected(country='US',issuer_id='0009999888',
                 as_of='2025-11-12',source=str(source),output_dir=str(output))
            self.assertEqual(report['guard'],'HOLD')
            self.assertEqual(len(report['evidence']),14)
            self.assertTrue(Path(paths['html']['path']).is_file())

    def test_kr_stays_one_megabyte_bound(self):
        data=json.loads(KR.read_text(encoding='utf-8'))
        data['synthetic_padding']='x'*1_100_000
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'dart.json'
            source.write_text(json.dumps(data),encoding='utf-8')
            output=root/'out';output.mkdir()
            with self.assertRaisesRegex(ValueError,'SOURCE_FILE_INVALID'):
                run_selected(country='KR',issuer_id='99998888',as_of='2025-11-12',
                     source=str(source),output_dir=str(output))

    def test_us_above_ten_megabytes_rejected_before_parse(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'big.json';source.write_bytes(b'x'*10_000_001)
            output=root/'out';output.mkdir()
            with self.assertRaisesRegex(ValueError,'SOURCE_FILE_INVALID'):
                run_selected(country='US',issuer_id='0009999888',as_of='2025-11-12',
                    source=str(source),output_dir=str(output))

    def test_symlink_input_stays_denied(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=root/'owned.json';src.write_bytes(self.oversized_us_bytes())
            link=root/'linked.json'
            try:
                link.symlink_to(src)
            except OSError:
                self.skipTest('Host policy disallows symlinks')
            output=root/'out';output.mkdir()
            with self.assertRaisesRegex(ValueError,'SOURCE_FILE_INVALID'):
                run_selected(country='US',issuer_id='0009999888',as_of='2025-11-12',
                    source=str(link),output_dir=str(output))

    def test_hardlink_large_input_stays_denied(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=root/'owned.json';src.write_bytes(self.oversized_us_bytes())
            linked=root/'linked.json'
            try:
                os.link(src,linked)
            except OSError:
                self.skipTest('Host policy disallows hardlinks')
            with self.assertRaisesRegex(ValueError,'LOCAL_SOURCE_FILE_POLICY_DENIED'):
                read_bounded_local(linked,limit=source_limit_for('US'))


if __name__=='__main__':
    unittest.main()
