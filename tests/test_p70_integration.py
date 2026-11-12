"""Full new product P70 synthetic country->KIC canonical->B/C/A->PDF audit.

Needs the copied proofinvest modules in GitHub develop, not a standalone demo.
"""
import json
from pathlib import Path
from copy import deepcopy
from datetime import date,timedelta
import socket
import tempfile
import unittest
from unittest.mock import patch
from kuodra.cli import analyze_bytes,main
from kuodra.report import render_html

BASE=Path(__file__).resolve().parents[1]/'fixtures/synthetic'
US=(BASE/'us_companyfacts.json').read_bytes()
KR=(BASE/'kr_dart.json').read_bytes()

class P70FullIntegration(unittest.TestCase):
    @staticmethod
    def amended_us():
        d=json.loads(US)
        val=deepcopy(d['facts']['us-gaap']['Revenues']['units']['USD'][1])
        val['form']='10-K/A';val['filed']='2025-04-01';val['accn']='0009999888-25-000009';val['val']=1300
        d['facts']['us-gaap']['Revenues']['units']['USD'].append(val)
        return json.dumps(d).encode()

    def test_amended_us_after_asof_with_canonical(self):
        raw=self.amended_us()
        a=analyze_bytes(raw,country='US',issuer_id='0009999888',as_of='2025-03-01')
        b=analyze_bytes(raw,country='US',issuer_id='0009999888',as_of='2025-05-01')
        self.assertTrue(any(x['metric']=='revenue' and x['amount']=='1200' for x in a['evidence']))
        self.assertTrue(any(x['metric']=='revenue' and x['amount']=='1300' for x in b['evidence']))
        self.assertEqual(b['fiscal_reconciliation']['revisions_changing_values'],1)
        self.assertTrue(any(x['revised_amount'] for x in b['revision_audit']))
        self.assertEqual(b['canonical_audit']['validated_rows'],14)
        self.assertEqual(b['guard'],'HOLD')
        self.assertFalse(b['source_verified'])
        self.assertFalse(b['rights_verified'])
        self.assertFalse(b['trade_executed'])
        self.assertIn('Historical filing revisions',render_html(b))

    def test_amended_kr_after_asof_and_canonical(self):
        d=json.loads(KR)
        row=deepcopy(d['list'][1]);row['rcept_no']='20250401000001';row['thstrm_amount']='1,300'
        d['list'].append(row)
        b=analyze_bytes(json.dumps(d).encode(),country='KR',issuer_id='99998888',as_of='2025-05-01')
        self.assertTrue(any(x['metric']=='revenue' and x['amount']=='1300' for x in b['evidence']))
        self.assertEqual(b['canonical_audit']['validated_rows'],14)
        self.assertEqual(b['fiscal_reconciliation']['revisions_changing_values'],1)
        self.assertEqual(b['guard'],'HOLD')

    def test_peer_case_with_sector_still_hold(self):
        d=json.loads(US);d['cik']=9999777
        b=analyze_bytes(US,country='US',issuer_id='0009999888',as_of='2025-03-01',
            peer_inputs=((json.dumps(d).encode(),'0009999777'),),synthetic_sector_code='TECH')
        self.assertEqual(b['engine_c'],'SYNTHETIC_SECTOR_COHORT_HOLD')
        self.assertEqual(b['peer_comparison']['comparison_count'],1)
        self.assertFalse(b['peer_comparison']['sector_policy']['authenticated'])
        self.assertEqual(b['guard'],'HOLD')
        self.assertIn('Peer comparison',render_html(b))

    def test_synthetic_market_case_does_not_unlock_real_market(self):
        s=[{'date':(date(2025,1,1)+timedelta(days=i)).isoformat(),'close':str(100+i)} for i in range(8)]
        m=[{'date':x['date'],'close':str(100+i*2)} for i,x in enumerate(s)]
        raw=json.dumps({'mode':'SYNTHETIC_TEST_ONLY','stock':s,'benchmark':m}).encode()
        r=analyze_bytes(US,country='US',issuer_id='0009999888',as_of='2025-03-01',synthetic_market_raw=raw)
        self.assertEqual(r['engine_a'],'SYNTHETIC_DESCRIPTIVE_ONLY')
        self.assertEqual(r['synthetic_market_a']['guard'],'HOLD')
        self.assertFalse(r['synthetic_market_a']['licensed_market_data_used'])
        self.assertIn('Synthetic A only',render_html(r))

    def test_unlicensed_market_file_rejected(self):
        with self.assertRaisesRegex(ValueError,'MARKET_SYNTHETIC_MODE_REQUIRED'):
            analyze_bytes(US,country='US',issuer_id='0009999888',as_of='2025-03-01',
                synthetic_market_raw=b'{"mode":"LICENSED","stock":[],"benchmark":[]}')

    def test_us_no_verified_consolidation_claim(self):
        with self.assertRaisesRegex(ValueError,'OFS_NOT_VERIFIABLE'):
            analyze_bytes(US,country='US',issuer_id='0009999888',as_of='2025-03-01',statement='OFS')

    def test_cli_pdf_three_artifacts_no_trade(self):
        with tempfile.TemporaryDirectory() as t:
            exit_code=main(['--country','KR','--issuer-id','99998888',
                            '--as-of','2025-03-01','--source',str(BASE/'kr_dart.json'),
                            '--output-dir',t,'--name','p70','--pdf'])
            self.assertEqual(exit_code,0)
            self.assertEqual({x.suffix for x in Path(t).iterdir()},{'.pdf','.html','.json'})
            pdf=(Path(t)/'p70.pdf').read_bytes()
            self.assertTrue(pdf.startswith(b'%PDF-'))
            report=json.loads((Path(t)/'p70.json').read_text())
            self.assertEqual(report['guard'],'HOLD')
            self.assertFalse(report['trade_executed'])

    def test_no_external_network_during_reconciliation(self):
        with patch.object(socket.socket,'connect',side_effect=AssertionError('NETWORK_DENIED')):
            r=analyze_bytes(self.amended_us(),country='US',issuer_id='0009999888',as_of='2025-05-01')
            self.assertEqual(r['guard'],'HOLD')

if __name__=='__main__':unittest.main()
