"""P95 source gateway: explicit consent and issuer binding, synthetic transport.

Real SEC/DART access and commercial source rights are NOT tested by this suite.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

from kuodra.official_review import analyze_opted_in_once

ROOT=Path(__file__).resolve().parents[1]
US=ROOT/'fixtures'/'synthetic'/'us_companyfacts.json'
KR=ROOT/'fixtures'/'synthetic'/'kr_dart.json'
USER_AGENT='KUODRA/1.0 (synthetic-test@example.invalid)'
DART_KEY='a'*40


class OfficialGatewayE2ETests(unittest.TestCase):
    def test_us_explicit_request_enforces_ci_issuer_then_guard_hold(self):
        calls=[]
        def fake_transport(req,timeout):
            calls.append((req.get_method(),req.full_url,timeout))
            return US.read_bytes(),'application/json'
        r=analyze_opted_in_once(country='US',issuer_id='0009999888',
            as_of='2025-11-12',owner_consent=True,
            sec_user_agent=USER_AGENT,transport=fake_transport)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][0],'GET')
        self.assertEqual(calls[0][1],
            'https://data.sec.gov/api/xbrl/companyfacts/CIK0009999888.json')
        self.assertEqual(r['guard'],'HOLD')
        self.assertFalse(r['rights_verified'])
        self.assertFalse(r['source_verified'])
        self.assertFalse(r['trade_executed'])
        self.assertEqual(len(r['evidence']),14)
        self.assertEqual(r['official_source_request']['provider'],'SEC')
        self.assertEqual(r['official_source_request']['automatic_retry_count'],0)
        self.assertNotIn('test@example.invalid',json.dumps(r))

    def test_kr_provided_key_not_returned_or_saved(self):
        calls=[]
        def fake_transport(req,timeout):
            calls.append(req.full_url)
            return KR.read_bytes(),'application/json'
        r=analyze_opted_in_once(country='KR',issuer_id='99998888',
            as_of='2025-11-12',owner_consent=True,
            dart_api_key=DART_KEY,dart_business_year='2024',
            transport=fake_transport)
        self.assertEqual(len(calls),1)
        self.assertIn('crtfc_key='+DART_KEY,calls[0])
        report=json.dumps(r,ensure_ascii=False)
        self.assertNotIn(DART_KEY,report)
        self.assertNotIn('crtfc_key',report)
        self.assertEqual(r['guard'],'HOLD')
        self.assertFalse(r['official_source_request']['commercial_rights_verified'])
        self.assertEqual(r['official_source_request']['fixed_url_no_credential'],
            'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json')

    def test_no_owner_consent_causes_no_transport(self):
        def unexpected(*args):
            raise AssertionError('UNEXPECTED_NETWORK')
        with self.assertRaisesRegex(ValueError,'OWNER_CONSENT'):
            analyze_opted_in_once(country='US',issuer_id='0009999888',
                as_of='2025-11-12',owner_consent=False,
                sec_user_agent=USER_AGENT,transport=unexpected)

    def test_missing_dart_key_stops_before_transport(self):
        with self.assertRaisesRegex(ValueError,'DART_EXPLICIT_CONSENT'):
            analyze_opted_in_once(country='KR',issuer_id='99998888',
                as_of='2025-11-12',owner_consent=True,
                dart_business_year='2024',
                transport=lambda *a: self.fail('REQUEST_WITHOUT_KEY'))

    def test_us_response_wrong_cik_is_rejected(self):
        d=json.loads(US.read_text(encoding='utf8'));d['cik']=12345
        with self.assertRaisesRegex(ValueError,'SEC_COMPANYFACTS_SCOPE'):
            analyze_opted_in_once(country='US',issuer_id='0009999888',
                as_of='2025-11-12',owner_consent=True,
                sec_user_agent=USER_AGENT,
                transport=lambda req,t: (json.dumps(d).encode(),'application/json'))

    def test_dart_application_status_denied(self):
        with self.assertRaisesRegex(ValueError,'DART_APPLICATION_STATUS'):
            analyze_opted_in_once(country='KR',issuer_id='99998888',
                as_of='2025-11-12',owner_consent=True,
                dart_api_key=DART_KEY,dart_business_year='2024',
                transport=lambda req,t: (b'{"status":"013","message":"no data"}','application/json'))

    def test_provider_forbidden_no_retry(self):
        call=[0]
        def forbidden(req,timeout):
            call[0]+=1
            raise urllib.error.HTTPError(req.full_url,403,'Forbidden',{},None)
        with self.assertRaisesRegex(ValueError,'FORBIDDEN_NO_BYPASS'):
            analyze_opted_in_once(country='US',issuer_id='0009999888',
                as_of='2025-11-12',owner_consent=True,
                sec_user_agent=USER_AGENT,transport=forbidden)
        self.assertEqual(call[0],1)

    def test_dart_key_not_allowed_on_sec(self):
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_DART'):
            analyze_opted_in_once(country='US',issuer_id='0009999888',
                as_of='2025-11-12',owner_consent=True,
                sec_user_agent=USER_AGENT,dart_api_key=DART_KEY,
                transport=lambda *a:self.fail('MUST_NOT_REQUEST'))

    def test_dart_response_mixed_corp_code_denied(self):
        d=json.loads(KR.read_text(encoding='utf8'))
        d['list'][0]['corp_code']='00000000'
        with self.assertRaisesRegex(ValueError,'DART_CORP_MISMATCH'):
            analyze_opted_in_once(country='KR',issuer_id='99998888',
                as_of='2025-11-12',owner_consent=True,
                dart_api_key=DART_KEY,dart_business_year='2024',
                transport=lambda req,t:(json.dumps(d).encode(),'application/json'))

    def test_asof_future_filing_results_are_denied(self):
        # The signed response transport cannot silently backdate later filings.
        r=analyze_opted_in_once(country='US',issuer_id='0009999888',
            as_of='2024-11-12',owner_consent=True,
            sec_user_agent=USER_AGENT,
            transport=lambda req,t:(US.read_bytes(),'application/json'))
        self.assertEqual(r['periods'],['2023-12-31'])
        self.assertNotIn('2024-12-31',r['periods'])


if __name__=='__main__':
    unittest.main()
