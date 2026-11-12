"""Synthetic-only KR/US offline positive, negative, cross-source and report checks."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import socket
from kuodra.cli import analyze_bytes,main
from kuodra.contracts import bounded_json,observation,parse_amount,parse_date
from kuodra.markets.kr.dart_local import parse_dart_annual
from kuodra.markets.us.sec_local import parse_sec_companyfacts
from kuodra.report import export_local,render_html
from kuodra.review import build_review

BASE=Path(__file__).resolve().parent.parent/'fixtures'/'synthetic'
US=BASE/'us_companyfacts.json';KR=BASE/'kr_dart.json'
US_ID='0009999888'; KR_ID='99998888'

class ContractTests(unittest.TestCase):
    def test_dates(self):
        with self.assertRaisesRegex(ValueError,'INVALID_DATE'):parse_date('2025-02-30')
        with self.assertRaisesRegex(ValueError,'INVALID_DATE'):parse_date('2025-2-01')
    def test_amount_rejects_nan_float_bool(self):
        for val in (True,1.5,'NaN','+3','-0','1e10','01'):
            with self.subTest(val=val),self.assertRaises(ValueError):parse_amount(val)
    def test_json_duplicate_rejected(self):
        with self.assertRaises(ValueError):bounded_json(b'{"status":"000","status":"001"}')
    def test_json_size_rejected(self):
        with self.assertRaises(ValueError):bounded_json(b'x'*1000001)
    def test_invalid_currency_rejected(self):
        with self.assertRaisesRegex(ValueError,'CURRENCY_MISMATCH'):
            observation(country='US',issuer_id=US_ID,metric='revenue',fiscal_end='2024-12-31',
                        available_at='2025-02-10',value=2,unit='KRW',statement='CFS',source_ref='SEC:abc',source_sha256='a'*64)

class USAdapter(unittest.TestCase):
    def test_us_two_years(self):
        x=parse_sec_companyfacts(US.read_bytes(),issuer_id=US_ID,as_of='2025-11-12')
        self.assertEqual(len(x),14)
        self.assertEqual(set(o.fiscal_end for o in x),{'2024-12-31','2023-12-31'})
    def test_us_mismatched_cik(self):
        with self.assertRaisesRegex(ValueError,'SEC_CIK_MISMATCH'):
            parse_sec_companyfacts(US.read_bytes(),issuer_id='0009999999',as_of='2025-11-12')
    def test_us_future_not_used(self):
        x=parse_sec_companyfacts(US.read_bytes(),issuer_id=US_ID,as_of='2024-12-01')
        self.assertEqual({y.fiscal_end for y in x},{'2023-12-31'})
    def test_us_conflicting_10ka_rejected(self):
        data=json.loads(US.read_text())
        rows=data['facts']['us-gaap']['NetIncomeLoss']['units']['USD']
        bad=dict(rows[-1]);bad['form']='10-K/A';bad['val']+=1;bad['accn']='0000000-25-999998';rows.append(bad)
        with self.assertRaisesRegex(ValueError,'SEC_CONFLICTING'):
            parse_sec_companyfacts(json.dumps(data).encode(),issuer_id=US_ID,as_of='2025-11-12')
    def test_us_filing_without_dates_fails(self):
        data=json.loads(US.read_text());data['facts']['us-gaap']['Revenues']['units']['USD'][0]['filed']='2025-99-99'
        with self.assertRaises(ValueError):parse_sec_companyfacts(json.dumps(data).encode(),issuer_id=US_ID,as_of='2025-11-12')

class KRAdapter(unittest.TestCase):
    def test_kr_two_years(self):
        x=parse_dart_annual(KR.read_bytes(),issuer_id=KR_ID,as_of='2025-11-12')
        self.assertEqual(len(x),14)
        self.assertEqual({o.fiscal_end for o in x},{'2023-12-31','2024-12-31'})
    def test_kr_wrong_company(self):
        with self.assertRaisesRegex(ValueError,'DART_CORP_MISMATCH'):
            parse_dart_annual(KR.read_bytes(),issuer_id='99999999',as_of='2025-11-12')
    def test_kr_future_hidden(self):
        x=parse_dart_annual(KR.read_bytes(),issuer_id=KR_ID,as_of='2024-11-12')
        self.assertEqual({o.fiscal_end for o in x},{'2023-12-31'})
    def test_kr_cfs_vs_ofs(self):
        with self.assertRaisesRegex(ValueError,'NO_ELIGIBLE'):
            parse_dart_annual(KR.read_bytes(),issuer_id=KR_ID,as_of='2025-11-12',statement='OFS')
    def test_kr_bad_account_section(self):
        data=json.loads(KR.read_text());data['list'][0]['sj_div']='BS'
        with self.assertRaisesRegex(ValueError,'DART_STATEMENT_SECTION'):
            parse_dart_annual(json.dumps(data).encode(),issuer_id=KR_ID,as_of='2025-11-12')
    def test_kr_duplicate_conflict(self):
        data=json.loads(KR.read_text());bad=dict(data['list'][0]);bad['thstrm_amount']='33';data['list'].append(bad)
        with self.assertRaisesRegex(ValueError,'DART_CONFLICTING'):
            parse_dart_annual(json.dumps(data).encode(),issuer_id=KR_ID,as_of='2025-11-12')

class Integration(unittest.TestCase):
    def test_both_countries_guard_hold(self):
        for country,issuer,p in [('US',US_ID,US),('KR',KR_ID,KR)]:
            with self.subTest(country=country):
                r=analyze_bytes(p.read_bytes(),country=country,issuer_id=issuer,as_of='2025-11-12')
                self.assertEqual(r['guard'],'HOLD')
                self.assertFalse(r['rights_verified'])
                self.assertFalse(r['source_verified'])
                self.assertEqual(r['engine_a'],'UNAVAILABLE_NO_LICENSED_MARKET_DATA')
                self.assertEqual(r['ml'],'NO_TRAIN_NO_VALIDATED_FINANCIAL_SAMPLES')
                self.assertFalse(r['trade_executed'])
                self.assertGreaterEqual(len(r['findings']),5)
                self.assertEqual(len(r['evidence']),14)
                self.assertTrue(any(f['name']=='cash_conversion' for f in r['findings']))
    def test_no_online_requests(self):
        with patch.object(socket.socket,'connect',side_effect=AssertionError('NETWORK_CALL')):
            self.test_both_countries_guard_hold()
    def test_historical_asof_no_future(self):
        for country,issuer,p in [('US',US_ID,US),('KR',KR_ID,KR)]:
            r=analyze_bytes(p.read_bytes(),country=country,issuer_id=issuer,as_of='2024-11-12')
            self.assertEqual(r['periods'],['2023-12-31'])
            self.assertFalse(any(f['name'].startswith('growth') for f in r['findings']))
    def test_scope_mismatch(self):
        a=parse_dart_annual(KR.read_bytes(),issuer_id=KR_ID,as_of='2025-11-12')
        b=parse_sec_companyfacts(US.read_bytes(),issuer_id=US_ID,as_of='2025-11-12')
        with self.assertRaisesRegex(ValueError,'REVIEW_SCOPE_MISMATCH'):
            build_review(a+b,as_of='2025-11-12')
    def test_html_not_injected(self):
        r=analyze_bytes(KR.read_bytes(),country='KR',issuer_id=KR_ID,as_of='2025-11-12')
        r['warnings'].append('<script>alert(1)</script>')
        html=render_html(r)
        self.assertNotIn('<script>alert(1)</script>',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('<table>',html)
        self.assertIn('cash_conversion',html)
        self.assertIn('class="bar"',html)
    def test_export_no_overwrite(self):
        r=analyze_bytes(US.read_bytes(),country='US',issuer_id=US_ID,as_of='2025-11-12')
        with tempfile.TemporaryDirectory() as t:
            out=export_local(r,Path(t),'fresh')
            self.assertEqual(set(out),{'json','html'})
            snap=(Path(t)/'fresh.json').read_bytes()
            with self.assertRaises(FileExistsError):export_local(r,Path(t),'fresh')
            self.assertEqual((Path(t)/'fresh.json').read_bytes(),snap)
            self.assertTrue((Path(t)/'fresh.html').exists())
    def test_existing_html_preserved_if_json_absent(self):
        r=analyze_bytes(US.read_bytes(),country='US',issuer_id=US_ID,as_of='2025-11-12')
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'review.html';p.write_text('user owned')
            with self.assertRaises(FileExistsError):export_local(r,Path(t))
            self.assertEqual(p.read_text(),'user owned')
            self.assertFalse((Path(t)/'report.json').exists())
    def test_path_traversal_name_denied(self):
        r=analyze_bytes(US.read_bytes(),country='US',issuer_id=US_ID,as_of='2025-11-12')
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError,'OUTPUT_STEM_INVALID'):export_local(r,Path(t),'../x')
    def test_cli_real_offline_path(self):
        with tempfile.TemporaryDirectory() as t:
            n=main(['--country','KR','--issuer-id',KR_ID,'--as-of','2025-11-12','--source',str(KR),'--output-dir',t,'--name','case1'])
            self.assertEqual(n,0)
            r=json.loads((Path(t)/'case1.json').read_text())
            self.assertEqual(r['country'],'KR')
            self.assertEqual(r['guard'],'HOLD')

if __name__=='__main__':unittest.main()

class GUINonInteractive(unittest.TestCase):
    def test_gui_workflow_without_window(self):
        from kuodra.gui import run_selected
        with tempfile.TemporaryDirectory() as t:
            r,art=run_selected(country='US',issuer_id=US_ID,as_of='2025-11-12',source=str(US),output_dir=t,name='gui_test')
            self.assertEqual(r['guard'],'HOLD')
            self.assertTrue(Path(art['html']['path']).exists())
    def test_gui_refuses_bad_local_path(self):
        from kuodra.gui import run_selected
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                run_selected(country='KR',issuer_id=KR_ID,as_of='2025-11-12',source=str(Path(t)/'missing.json'),output_dir=t)

class PeerTests(unittest.TestCase):
    def test_same_country_peer_calculations_are_hold(self):
        from kuodra.peers import compare_peers
        a=analyze_bytes(US.read_bytes(),country='US',issuer_id=US_ID,as_of='2025-11-12')
        d=json.loads(US.read_text());d['cik']=9999777
        for fact in d['facts']['us-gaap'].values():
            for row in fact['units']['USD']:row['val']*=2
        b=analyze_bytes(json.dumps(d).encode(),country='US',issuer_id='0009999777',as_of='2025-11-12')
        c=compare_peers(a,[b])
        self.assertEqual(c['status'],'DESCRIPTIVE_PEER_ONLY_UNVERIFIED')
        self.assertEqual(c['guard'],'HOLD')
        self.assertFalse(c['source_rights_verified'])
    def test_cross_country_peer_refused(self):
        from kuodra.peers import compare_peers
        a=analyze_bytes(US.read_bytes(),country='US',issuer_id=US_ID,as_of='2025-11-12')
        b=analyze_bytes(KR.read_bytes(),country='KR',issuer_id=KR_ID,as_of='2025-11-12')
        with self.assertRaisesRegex(ValueError,'PEER_INCOMPARABLE'):
            compare_peers(a,[b])
    def test_self_comparison_refused(self):
        from kuodra.peers import compare_peers
        a=analyze_bytes(US.read_bytes(),country='US',issuer_id=US_ID,as_of='2025-11-12')
        with self.assertRaisesRegex(ValueError,'DUPLICATE_PEER'):
            compare_peers(a,[a])

class FinancialBoundaryTests(unittest.TestCase):
    def test_us_annual_flow_requires_start(self):
        d=json.loads(US.read_text())
        del d['facts']['us-gaap']['Revenues']['units']['USD'][0]['start']
        with self.assertRaisesRegex(ValueError,'SEC_ANNUAL_FLOW_START_MISSING'):
            parse_sec_companyfacts(json.dumps(d).encode(),issuer_id=US_ID,as_of='2025-11-12')
    def test_kr_receipt_must_follow_fiscal_period(self):
        d=json.loads(KR.read_text());d['list'][0]['rcept_no']='20230101000001'
        with self.assertRaisesRegex(ValueError,'RELEASE_BEFORE_PERIOD'):
            parse_dart_annual(json.dumps(d).encode(),issuer_id=KR_ID,as_of='2025-11-12')
    def test_us_unreleased_no_data_holds(self):
        with self.assertRaises(ValueError):
            analyze_bytes(US.read_bytes(),country='US',issuer_id=US_ID,as_of='2023-01-01')
    def test_guard_is_never_a_trade_authorization(self):
        for c,i,p in [('US',US_ID,US),('KR',KR_ID,KR)]:
            report=analyze_bytes(p.read_bytes(),country=c,issuer_id=i,as_of='2025-11-12')
            self.assertFalse(report['trade_executed'])
            self.assertNotIn('BUY',str(report))
            self.assertNotIn('SELL',str(report))
