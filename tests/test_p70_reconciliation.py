"""P70: synthetic annual vintage, calendar, peer and market rights gates.

All values/issuer IDs are fictional. Source rights and publisher identity remain
unverified; no trading or external data calls are permitted.
"""
import json
from copy import deepcopy
from pathlib import Path
from datetime import datetime,timedelta,date
from decimal import Decimal
import unittest
from kuodra.markets.kr.dart_local import parse_dart_annual
from kuodra.markets.us.sec_local import parse_sec_companyfacts
from kuodra.market_a import evaluate_synthetic_market_a
from kuodra.peers import compare_peers
from kuodra.review import build_review
from kuodra.report import render_html

ROOT=Path(__file__).resolve().parents[1]/'fixtures'/'synthetic'
KR_RAW=(ROOT/'kr_dart.json').read_bytes()
US_RAW=(ROOT/'us_companyfacts.json').read_bytes()

def kr():return json.loads(KR_RAW)
def us():return json.loads(US_RAW)
def source(data):return json.dumps(data,separators=(',',':')).encode('utf8')

def us_amend(*,filed='2025-04-01',amount=1300):
    x=us();r=deepcopy(x['facts']['us-gaap']['Revenues']['units']['USD'][-1]);
    r['filed']=filed;r['form']='10-K/A';r['val']=amount;r['accn']='0009999888-25-000009'
    x['facts']['us-gaap']['Revenues']['units']['USD'].append(r)
    return source(x)

def kr_amend(*,date_no='20250401000001',amount='1300'):
    x=kr();r=deepcopy(x['list'][1]);r['rcept_no']=date_no;r['thstrm_amount']=amount
    x['list'].append(r)
    return source(x)

class AnnualVintageTests(unittest.TestCase):
    def test_us_later_amended_fact_selected_with_audit(self):
        raw=us_amend()
        old,_=parse_sec_companyfacts(raw,issuer_id='0009999888',as_of='2025-03-01',with_audit=True)
        now,audit=parse_sec_companyfacts(raw,issuer_id='0009999888',as_of='2025-05-01',with_audit=True)
        fetch=lambda rows:next(r for r in rows if r.metric=='revenue' and r.fiscal_end=='2024-12-31')
        self.assertEqual(fetch(old).value,Decimal(1200))
        self.assertEqual(fetch(now).value,Decimal(1300))
        a=next(r for r in audit if r['metric']=='revenue' and r['fiscal_end']=='2024-12-31')
        self.assertTrue(a['revised_amount']);self.assertEqual(a['chosen_filed_at'],'2025-04-01')
        self.assertEqual(a['candidate_count'],2)
        self.assertFalse(a['publisher_authenticated'])
    def test_us_same_day_conflict_denied(self):
        with self.assertRaisesRegex(ValueError,'SAME_DAY_CONFLICT'):
            parse_sec_companyfacts(us_amend(filed='2025-02-10'),issuer_id='0009999888',as_of='2025-03-01')
    def test_us_revised_after_cutoff_does_not_leak(self):
        raw=us_amend(filed='2027-01-01')
        facts=parse_sec_companyfacts(raw,issuer_id='0009999888',as_of='2025-03-01')
        self.assertEqual(next(r.value for r in facts if r.metric=='revenue' and r.fiscal_end=='2024-12-31'),Decimal(1200))
    def test_us_official_accession_format_required(self):
        x=us();x['facts']['us-gaap']['Revenues']['units']['USD'][0]['accn']='bogus'
        with self.assertRaisesRegex(ValueError,'SEC_ACCESSION_INVALID'):
            parse_sec_companyfacts(source(x),issuer_id='0009999888',as_of='2025-03-01')
    def test_us_ofs_not_falsely_classified_from_companyfacts(self):
        with self.assertRaisesRegex(ValueError,'SEC_OFS_NOT_VERIFIABLE'):
            parse_sec_companyfacts(US_RAW,issuer_id='0009999888',as_of='2025-03-01',statement='OFS')
    def test_us_stock_fact_duration_rejected(self):
        x=us();x['facts']['us-gaap']['InventoryNet']['units']['USD'][0]['start']='2023-01-01'
        with self.assertRaisesRegex(ValueError,'SEC_STOCK_FACT_HAS_DURATION'):
            parse_sec_companyfacts(source(x),issuer_id='0009999888',as_of='2025-03-01')
    def test_kr_later_corrected_fact_selected(self):
        raw=kr_amend()
        previous,_=parse_dart_annual(raw,issuer_id='99998888',as_of='2025-03-01',with_audit=True)
        latest,audit=parse_dart_annual(raw,issuer_id='99998888',as_of='2025-05-01',with_audit=True)
        get=lambda a:next(r.value for r in a if r.metric=='revenue' and r.fiscal_end=='2024-12-31')
        self.assertEqual(get(previous),Decimal(1200))
        self.assertEqual(get(latest),Decimal(1300))
        self.assertTrue(any(a['revised_amount'] for a in audit))
    def test_kr_conflict_same_day_rejected(self):
        with self.assertRaisesRegex(ValueError,'SAME_DAY_CONFLICT'):
            parse_dart_annual(kr_amend(date_no='20250210000002'),issuer_id='99998888',as_of='2025-03-01')
    def test_kr_fiscal_period_required(self):
        x=kr();del x['list'][0]['thstrm_dt']
        with self.assertRaisesRegex(ValueError,'DART_FISCAL_PERIOD_MISSING'):
            parse_dart_annual(source(x),issuer_id='99998888',as_of='2025-03-01')
    def test_kr_non_calendar_fiscal_end_read_not_inferred(self):
        x=kr();row=x['list'][1];row['thstrm_dt']='2023.07.01 ~ 2024.06.30'
        got=parse_dart_annual(source(x),issuer_id='99998888',as_of='2025-03-01')
        self.assertTrue(any(r.fiscal_end=='2024-06-30' for r in got))
    def test_kr_mismatched_fiscal_year_denied(self):
        x=kr();x['list'][0]['thstrm_dt']='2022.12.31'
        with self.assertRaisesRegex(ValueError,'DART_FISCAL_YEAR_MISMATCH'):
            parse_dart_annual(source(x),issuer_id='99998888',as_of='2025-03-01')
    def test_kr_missing_currency_denied(self):
        x=kr();del x['list'][0]['currency']
        with self.assertRaisesRegex(ValueError,'DART_CURRENCY_NOT_EXPLICIT_KRW'):
            parse_dart_annual(source(x),issuer_id='99998888',as_of='2025-03-01')
    def test_kr_invalid_duration_denied(self):
        x=kr();x['list'][0]['thstrm_dt']='2024.01.01 ~ 2024.12.31'
        with self.assertRaisesRegex(ValueError,'DART_FISCAL_YEAR_MISMATCH'):
            parse_dart_annual(source(x),issuer_id='99998888',as_of='2025-03-01')
    def test_same_day_same_amount_deduplicates(self):
        x=kr();x['list'].append(deepcopy(x['list'][1]))
        got,audit=parse_dart_annual(source(x),issuer_id='99998888',as_of='2025-03-01',with_audit=True)
        self.assertEqual(len(got),14)
        self.assertEqual(sum(a['candidate_count']-1 for a in audit),1)

class MarketAndPeerTests(unittest.TestCase):
    @staticmethod
    def market(n=8,constant=False):
        dates=[(date(2025,1,1)+timedelta(days=i)).isoformat() for i in range(n)]
        s=[{'date':d,'close':str(100+i*2)} for i,d in enumerate(dates)]
        m=[{'date':d,'close':str(100 if constant else 100+i)} for i,d in enumerate(dates)]
        return s,m
    def test_market_a_is_synthetic_and_hold(self):
        a,b=self.market();r=evaluate_synthetic_market_a(a,b)
        self.assertEqual(r['status'],'SYNTHETIC_DESCRIPTIVE_ONLY')
        self.assertEqual(r['guard'],'HOLD')
        self.assertFalse(r['licensed_market_data_used'])
        self.assertEqual(r['stock_total_return'],'0.140000')
        self.assertEqual(r['benchmark_total_return'],'0.070000')
        self.assertEqual(r['simple_relative_delta'],'0.070000')
    def test_market_a_rejects_real_data_and_labels(self):
        a,b=self.market()
        for kwargs in ({'use_mode':'LICENSED'},{'stock_label':'AAPL'}):
            with self.subTest(kwargs=kwargs),self.assertRaisesRegex(ValueError,'UNLICENSED'):
                evaluate_synthetic_market_a(a,b,**kwargs)
    def test_market_a_zero_index_variance_no_fake_beta(self):
        a,b=self.market(constant=True)
        self.assertIsNone(evaluate_synthetic_market_a(a,b)['beta'])
    def test_market_calendar_mismatch(self):
        a,b=self.market();b[2]['date']='2025-01-15'
        with self.assertRaises(ValueError):evaluate_synthetic_market_a(a,b)
    def test_market_duplicate_date_rejected(self):
        a,b=self.market();a[1]['date']=a[0]['date']
        with self.assertRaisesRegex(ValueError,'ASCENDING'):
            evaluate_synthetic_market_a(a,b)
    def test_peer_sectors_requires_issuer_exact(self):
        base=build_review(parse_sec_companyfacts(US_RAW,issuer_id='0009999888',as_of='2025-03-01'),as_of='2025-03-01')
        x=us();x['cik']=9999777
        peer=build_review(parse_sec_companyfacts(source(x),issuer_id='0009999777',as_of='2025-03-01'),as_of='2025-03-01')
        with self.assertRaisesRegex(ValueError,'SECTOR_EVIDENCE_INVALID'):
            compare_peers(base,[peer],synthetic_sector={'code':'TECH','origin':'SYNTHETIC_TEST_ONLY','issuers':['0009999888']})
        r=compare_peers(base,[peer],synthetic_sector={'code':'TECH','origin':'SYNTHETIC_TEST_ONLY','issuers':['0009999888','0009999777']})
        self.assertEqual(r['status'],'SYNTHETIC_SECTOR_COHORT_HOLD')
        self.assertFalse(r['sector_policy']['authenticated'])
        self.assertEqual(r['guard'],'HOLD')
    def test_revision_table_escaped(self):
        r=build_review(parse_dart_annual(KR_RAW,issuer_id='99998888',as_of='2025-03-01'),as_of='2025-03-01')
        r['revision_audit']=[{'fiscal_end':'2024-12-31','metric':'revenue','chosen_source':'DART:20250401000001',
                             'chosen_filed_at':'2025-04-01','revised_amount':True}]
        html=render_html(r)
        self.assertIn('Historical filing revisions',html)
        self.assertIn('DART:20250401000001',html)

if __name__=='__main__':unittest.main()
