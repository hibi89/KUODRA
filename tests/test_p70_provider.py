"""Opt-in sources tested with transport fakes: no actual credentials/requests."""
import unittest
from urllib.request import Request
from urllib.error import HTTPError
from kuodra.source_client import build_sec_request,build_dart_request,fetch_once

class P70ProviderTests(unittest.TestCase):
    def test_off_by_default(self):
        with self.assertRaisesRegex(ValueError,'CONSENT'):
            build_sec_request('0000320193',user_agent='KUODRA/1.0 (product@example.com)',opt_in=False)
        with self.assertRaisesRegex(ValueError,'CONSENT'):
            build_dart_request('00126380',year='2025',api_key='a'*40,opt_in=False)
    def test_sec_user_agent_and_fixed_endpoint(self):
        req=build_sec_request('0000320193',user_agent='KUODRA/1.0 (product@example.com)',opt_in=True)
        self.assertEqual(req.full_url,'https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json')
        self.assertEqual(req.get_method(),'GET')
        self.assertIn('product@example.com',req.get_header('User-agent'))
    def test_dart_key_not_in_receipt(self):
        req=build_dart_request('00126380',year='2025',api_key='a'*40,opt_in=True)
        r=fetch_once(req,provider='DART',opt_in=True,transport=lambda q,t:(b'{"status":"000","list":[]}','application/json'))
        self.assertNotIn('aaaa',r.source_url)
        self.assertFalse(r.publisher_authenticated)
        self.assertFalse(r.commercial_rights_verified)
    def test_wrong_host_denied(self):
        req=Request('https://evil.example/api/xbrl/companyfacts/CIK0000320193.json',method='GET')
        with self.assertRaisesRegex(ValueError,'HOST_DENIED'):
            fetch_once(req,provider='SEC',opt_in=True,transport=lambda q,t:(b'{}','application/json'))
    def test_forged_route_denied(self):
        req=Request('https://data.sec.gov/path',method='GET')
        with self.assertRaisesRegex(ValueError,'ROUTE_OR_AGENT_DENIED'):
            fetch_once(req,provider='SEC',opt_in=True,transport=lambda q,t:(b'{}','application/json'))
    def test_rate_limit_never_retry(self):
        req=build_sec_request('0000320193',user_agent='KUODRA/1.0 (product@example.com)',opt_in=True)
        calls=[]
        def fake(q,t):
            calls.append(q)
            raise HTTPError(q.full_url,429,'rate limited',{},None)
        with self.assertRaisesRegex(ValueError,'RATE_LIMIT_NO_RETRY'):
            fetch_once(req,provider='SEC',opt_in=True,transport=fake)
        self.assertEqual(len(calls),1)
    def test_error_hides_credential(self):
        req=build_dart_request('00126380',year='2025',api_key='a'*40,opt_in=True)
        def fake(q,t): raise HTTPError(q.full_url,403,'Forbidden',{},None)
        with self.assertRaises(ValueError) as ctx:
            fetch_once(req,provider='DART',opt_in=True,transport=fake)
        self.assertNotIn('aaaa',str(ctx.exception))
    def test_provider_rejects_missing_sec_agent(self):
        req=Request('https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json',method='GET')
        with self.assertRaisesRegex(ValueError,'AGENT_DENIED'):
            fetch_once(req,provider='SEC',opt_in=True,transport=lambda q,t:(b'{}','application/json'))
    def test_provider_rejects_extra_dart_query(self):
        req=build_dart_request('00126380',year='2025',api_key='a'*40,opt_in=True)
        bad=Request(req.full_url+'&redirect=https://evil.example',method='GET')
        with self.assertRaisesRegex(ValueError,'REQUEST_SCOPE_DENIED'):
            fetch_once(bad,provider='DART',opt_in=True,transport=lambda q,t:(b'{}','application/json'))
    def test_response_size_and_mimetype_rejected(self):
        req=build_sec_request('0000320193',user_agent='KUODRA/1.0 (product@example.com)',opt_in=True)
        for payload,ctype in ((b'x'*10_000_001,'application/json'),(b'hello','text/html')):
            with self.subTest(length=len(payload)):
                with self.assertRaisesRegex(ValueError,'RESPONSE_INVALID'):
                    fetch_once(req,provider='SEC',opt_in=True,transport=lambda q,t:(payload,ctype))
    def test_dart_http_200_application_error_is_not_accepted(self):
        req=build_dart_request('00126380',year='2025',api_key='a'*40,opt_in=True)
        with self.assertRaisesRegex(ValueError,'DART_APPLICATION_STATUS_NOT_SUCCESS'):
            fetch_once(req,provider='DART',opt_in=True,
                       transport=lambda q,t:(b'{"status":"013","message":"key invalid"}','application/json'))

    def test_sec_payload_scope_never_assumed_from_url(self):
        req=build_sec_request('0000320193',user_agent='KUODRA/1.0 (product@example.com)',opt_in=True)
        for fake in (b'{}', b'{"cik":123,"facts":{}}',b'{"cik":320193,"facts":[]}',b'[]'):
            with self.subTest(payload=fake):
                with self.assertRaises(ValueError):
                    fetch_once(req,provider='SEC',opt_in=True,
                               transport=lambda q,t:(fake,'application/json'))
        ok=fetch_once(req,provider='SEC',opt_in=True,
                      transport=lambda q,t:(b'{"cik":320193,"facts":{}}','application/json'))
        self.assertFalse(ok.publisher_authenticated)
        self.assertFalse(ok.commercial_rights_verified)

    def test_invalid_json_and_non_object_denied(self):
        req=build_dart_request('00126380',year='2025',api_key='a'*40,opt_in=True)
        with self.assertRaisesRegex(ValueError,'PROVIDER_JSON_INVALID'):
            fetch_once(req,provider='DART',opt_in=True,
                       transport=lambda q,t:(b'not-json','application/json'))
        with self.assertRaisesRegex(ValueError,'PROVIDER_JSON_OBJECT_REQUIRED'):
            fetch_once(req,provider='DART',opt_in=True,
                       transport=lambda q,t:(b'[]','application/json'))

    def test_sec_parser_accepts_bounded_over_one_megabyte(self):
        from kuodra.contracts import bounded_json
        raw=b'{"x":"'+b'A'*1_200_000+b'"}'
        with self.assertRaisesRegex(ValueError,'SOURCE_SIZE_INVALID'):
            bounded_json(raw)
        self.assertIn('x',bounded_json(raw,max_bytes=10_000_000))

if __name__=='__main__':unittest.main()
