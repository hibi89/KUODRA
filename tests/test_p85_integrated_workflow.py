"""Integrated P85 CLI/report/heldout/Guard on lawfully local synthetic fixtures only."""
from __future__ import annotations
from contextlib import redirect_stdout
from datetime import date, timedelta
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from kuodra.cli import analyze_bytes, main
from kuodra.report import render_html, export_local
from kuodra.release_gate import verify_evidence_bundle

ROOT=Path(__file__).resolve().parents[1]
KR=ROOT/'fixtures'/'synthetic'/'kr_dart.json'

def _heldout_bytes():
    d=date(2021,1,1)
    rows=[]
    for i in range(30):
        day=d+timedelta(days=i)
        rows.append({'issuer_id':'TRAIN_A','observed_at':day.isoformat(),
                     'released_at':(day+timedelta(days=1)).isoformat(),
                     'split':'train','feature':str(i),'target':str(2*i+3)})
    for i in range(12):
        day=d+timedelta(days=40+i)
        rows.append({'issuer_id':'TEST_B','observed_at':day.isoformat(),
                     'released_at':(day+timedelta(days=1)).isoformat(),
                     'split':'test','feature':str(i+40),'target':str((i+40)*2+3)})
    return json.dumps({'schema':'kuodra.synthetic-heldout.v1',
                       'mode':'SYNTHETIC_TEST_ONLY','rows':rows}).encode()

class P85FullPipelineTests(unittest.TestCase):
    def _review(self):
        return analyze_bytes(KR.read_bytes(),country='KR',issuer_id='99998888',
                             as_of='2025-11-12',synthetic_heldout_raw=_heldout_bytes(),
                             heldout_owner_consent=True)
    def test_model_baseline_never_approves(self):
        result=self._review()
        self.assertEqual(result['synthetic_heldout']['status'],'EVALUATED_SYNTHETIC_ONLY')
        self.assertEqual(result['guard'],'HOLD')
        self.assertFalse(result['trade_executed'])
        self.assertFalse(result['synthetic_heldout']['prediction_claim'])
        self.assertFalse(result['canonical_audit']['private_data_exported'])
    def test_html_contains_dummy_and_limits(self):
        html=render_html(self._review())
        self.assertIn('Dummy baseline',html)
        self.assertIn('Grouped/time-heldout',html)
        self.assertNotIn('TRAIN_A',html)
        self.assertNotIn('TEST_B',html)
    def test_local_pdf_html_json_and_independent_hashes(self):
        r=self._review()
        with tempfile.TemporaryDirectory() as td:
            paths=export_local(r,Path(td),'p85',pdf=True)
            checked=verify_evidence_bundle(td,'p85',require_pdf=True)
            self.assertEqual(set(paths),{'json','html','pdf'})
            for ext in paths:
                self.assertEqual(paths[ext]['sha256'],checked['file_hashes'][ext])
            self.assertEqual(checked['guard'],'HOLD')
            self.assertFalse(checked['publisher_authenticated'])
    def test_no_overwrite_existing_bundle(self):
        r=self._review()
        with tempfile.TemporaryDirectory() as td:
            export_local(r,Path(td),'same')
            with self.assertRaises(FileExistsError):export_local(r,Path(td),'same')
    def test_owner_consent_enforced(self):
        with self.assertRaisesRegex(ValueError,'CONSENT'):
            analyze_bytes(KR.read_bytes(),country='KR',issuer_id='99998888',
                          as_of='2025-11-12',synthetic_heldout_raw=_heldout_bytes())
    def test_cli_optional_e2e(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);heldout=p/'synthetic-heldout.json';heldout.write_bytes(_heldout_bytes())
            output=p/'out';output.mkdir()
            capture=StringIO()
            with redirect_stdout(capture):
                code=main(['--country','KR','--issuer-id','99998888',
                           '--as-of','2025-11-12','--source',str(KR),
                           '--output-dir',str(output),'--name','cli',
                           '--synthetic-heldout-source',str(heldout),
                           '--heldout-consent'])
            self.assertEqual(code,0)
            result=json.loads(capture.getvalue())
            self.assertEqual(result['guard'],'HOLD')
            self.assertEqual(verify_evidence_bundle(output,'cli')['guard'],'HOLD')

if __name__=='__main__':unittest.main()
