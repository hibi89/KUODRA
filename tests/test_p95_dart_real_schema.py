"""Official OpenDART full-statement contract tests (synthetic, no real key).

The official fnlttSinglAcntAll response list has NO guaranteed per-row
'fs_div' or 'thstrm_dt'. These are supplied by validated request scope and
explicit owner-verified fiscal-end, NEVER invented from a December year-end.
Official schema: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from kuodra.markets.kr.dart_local import parse_dart_annual
from kuodra.official_review import analyze_opted_in_once
from kuodra.cli import analyze_bytes

ROOT=Path(__file__).resolve().parents[1]
SYNTHETIC=ROOT/'fixtures'/'synthetic'/'kr_dart.json'
KEY='1'*40


def synthetic_documented_all_rows():
    o=json.loads(SYNTHETIC.read_text(encoding='utf-8'))
    o['list']=[r.copy() for r in o['list'] if r['bsns_year']=='2024']
    for r in o['list']:
        del r['thstrm_dt']
        del r['fs_div']
        r['thstrm_nm']='제 24 기'
        r['account_nm']=r['account_id']
        r['account_detail']='-'
    o['message']='SYNTHETIC DART FULL ACCOUNT ALL SHAPE, NOT REAL API'
    return json.dumps(o,ensure_ascii=False).encode('utf-8')


class OfficialDartShapeAcceptance(TestCase):
    def test_official_shape_requires_bound_requested_statement(self):
        with self.assertRaisesRegex(ValueError,'DART_FS_DIV_REQUEST_SCOPE_NOT_BOUND'):
            parse_dart_annual(synthetic_documented_all_rows(),
                issuer_id='99998888',as_of='2025-11-12',
                fiscal_end_override='2024-12-31')

    def test_official_shape_requires_explicit_fiscal_end(self):
        with self.assertRaisesRegex(ValueError,'DART_FISCAL_PERIOD_MISSING'):
            parse_dart_annual(synthetic_documented_all_rows(),
                issuer_id='99998888',as_of='2025-11-12',
                request_fs_div_bound=True)

    def test_documented_shape_owner_end_reconciles_and_guard_holds(self):
        raw=synthetic_documented_all_rows()
        observations=parse_dart_annual(raw,issuer_id='99998888',
            as_of='2025-11-12',fiscal_end_override='2024-12-31',
            request_fs_div_bound=True)
        self.assertEqual(len(observations),7)
        self.assertEqual({r.fiscal_end for r in observations},{'2024-12-31'})
        report=analyze_bytes(raw,country='KR',issuer_id='99998888',
            as_of='2025-11-12',dart_fiscal_end='2024-12-31',
            dart_request_fs_div_bound=True)
        self.assertEqual(report['guard'],'HOLD')
        self.assertFalse(report['source_verified'])
        self.assertEqual(report['periods'],['2024-12-31'])
        self.assertEqual(len(report['evidence']),7)
        self.assertFalse(report['trade_executed'])

    def test_wrong_business_year_no_silent_calendar_rollover(self):
        with self.assertRaisesRegex(ValueError,'DART_FISCAL_YEAR_MISMATCH'):
            parse_dart_annual(synthetic_documented_all_rows(),
                issuer_id='99998888',as_of='2025-11-12',
                fiscal_end_override='2025-03-31',request_fs_div_bound=True)

    def test_missing_fiscal_end_override_does_not_assume_december(self):
        o=json.loads(synthetic_documented_all_rows())
        for r in o['list']: r['bsns_year']='2024'
        with self.assertRaisesRegex(ValueError,'DART_FISCAL_PERIOD_MISSING'):
            parse_dart_annual(json.dumps(o).encode(),issuer_id='99998888',
                as_of='2025-11-12',request_fs_div_bound=True)

    def test_conflicting_fiscal_end_in_supplied_row_rejected(self):
        o=json.loads(SYNTHETIC.read_text(encoding='utf8'))
        o['list']=[r for r in o['list'] if r['bsns_year']=='2024']
        with self.assertRaisesRegex(ValueError,'DART_FISCAL_END_SOURCE_CONFLICT'):
            parse_dart_annual(json.dumps(o).encode(),issuer_id='99998888',
                as_of='2025-11-12',fiscal_end_override='2024-09-30')

    def test_request_response_fs_div_conflict_rejected(self):
        o=json.loads(synthetic_documented_all_rows())
        o['list'][0]['fs_div']='OFS'
        with self.assertRaisesRegex(ValueError,'DART_FS_DIV_REQUEST_RESPONSE_MISMATCH'):
            parse_dart_annual(json.dumps(o).encode(),issuer_id='99998888',
                as_of='2025-11-12',fiscal_end_override='2024-12-31',
                request_fs_div_bound=True)

    def test_blank_official_amount_is_missing_not_zero(self):
        o=json.loads(synthetic_documented_all_rows())
        o['list'][0]['thstrm_amount']=''
        rows=parse_dart_annual(json.dumps(o).encode(),issuer_id='99998888',
            as_of='2025-11-12',fiscal_end_override='2024-12-31',
            request_fs_div_bound=True)
        self.assertEqual(len(rows),6)
        self.assertNotIn('0',[str(r.value) for r in rows if r.metric=='revenue'])

    def test_owner_opt_in_gateway_binds_request_scope(self):
        raw=synthetic_documented_all_rows()
        reqs=[]
        def transport(req,timeout):
            reqs.append(req.full_url)
            return raw,'application/json'
        report=analyze_opted_in_once(country='KR',issuer_id='99998888',
            as_of='2025-11-12',owner_consent=True,dart_api_key=KEY,
            dart_business_year='2024',dart_fiscal_end='2024-12-31',
            transport=transport)
        self.assertEqual(len(reqs),1)
        self.assertIn('fs_div=CFS',reqs[0])
        self.assertEqual(report['guard'],'HOLD')
        self.assertFalse(report['rights_verified'])
        self.assertEqual(
            report['official_source_request']['financial_period_origin'],
            'OWNER_EXPLICIT_FISCAL_END_NOT_IN_DART_ALL_RESPONSE')
        self.assertNotIn(KEY,json.dumps(report))

    def test_future_dart_receipt_filtered_without_false_asof(self):
        raw=synthetic_documented_all_rows()
        with self.assertRaisesRegex(ValueError,'DART_NO_ELIGIBLE_ANNUAL_FACTS'):
            parse_dart_annual(raw,issuer_id='99998888',as_of='2024-12-31',
                fiscal_end_override='2024-12-31',request_fs_div_bound=True)

    def test_official_response_without_period_must_fail_closed(self):
        raw=synthetic_documented_all_rows()
        with self.assertRaisesRegex(ValueError,'DART_FISCAL_PERIOD_MISSING'):
            analyze_opted_in_once(country='KR',issuer_id='99998888',
                as_of='2025-11-12',owner_consent=True,dart_api_key=KEY,
                dart_business_year='2024',
                transport=lambda req,t:(raw,'application/json'))


    def test_owner_local_documented_json_via_gui_korean(self):
        from kuodra.gui import run_selected
        with TemporaryDirectory() as td:
            root=Path(td)
            src=root/'local_dart_2024.json'
            src.write_bytes(synthetic_documented_all_rows())
            report,art=run_selected(
                country='KR',issuer_id='99998888',as_of='2025-11-12',
                source=str(src),output_dir=td,name='dart_owner_local',
                dart_fiscal_end='2024-12-31',dart_scope_attested=True,
                language='ko')
            self.assertEqual(report['guard'],'HOLD')
            self.assertFalse(report['source_verified'])
            html=Path(art['html']['path']).read_text(encoding='utf8')
            self.assertIn('lang="ko"',html)
            self.assertIn('공시 원문 수치 근거',html)
            self.assertFalse(report['rights_verified'])

    def test_owner_local_documented_json_via_cli(self):
        from kuodra.cli import main as offline_cli
        with TemporaryDirectory() as td:
            root=Path(td)
            src=root/'dart.json'
            src.write_bytes(synthetic_documented_all_rows())
            out=StringIO()
            with redirect_stdout(out):
                rc=offline_cli([
                    '--country','KR','--issuer-id','99998888',
                    '--as-of','2025-11-12','--statement','CFS',
                    '--source',str(src),'--output-dir',td,
                    '--name','dart_cli','--dart-fiscal-end','2024-12-31',
                    '--dart-request-scope-attested','--html-language','ko'
                ])
            self.assertEqual(rc,0)
            result=json.loads((root/'dart_cli.json').read_text(encoding='utf8'))
            self.assertEqual(result['guard'],'HOLD')
            self.assertEqual(result['periods'],['2024-12-31'])
            self.assertIn('공시 원문 수치 근거',
                (root/'dart_cli.html').read_text(encoding='utf8'))

    def test_local_gui_missing_owner_scope_refuses_without_faking(self):
        from kuodra.gui import run_selected
        with TemporaryDirectory() as td:
            root=Path(td); src=root/'dart.json'
            src.write_bytes(synthetic_documented_all_rows())
            with self.assertRaisesRegex(ValueError,'DART_FS_DIV_REQUEST_SCOPE_NOT_BOUND'):
                run_selected(country='KR',issuer_id='99998888',
                    as_of='2025-11-12',source=str(src),
                    output_dir=td,dart_fiscal_end='2024-12-31',
                    dart_scope_attested=False)

    def test_local_gui_owner_scope_still_requires_fiscal_end(self):
        from kuodra.gui import run_selected
        with TemporaryDirectory() as td:
            root=Path(td);src=root/'dart.json'
            src.write_bytes(synthetic_documented_all_rows())
            with self.assertRaisesRegex(ValueError,'DART_FISCAL_PERIOD_MISSING'):
                run_selected(country='KR',issuer_id='99998888',
                    as_of='2025-11-12',source=str(src),output_dir=td,
                    dart_scope_attested=True)

    def test_original_synthetic_period_scope_still_works(self):
        rows=parse_dart_annual(SYNTHETIC.read_bytes(),
            issuer_id='99998888',as_of='2025-11-12')
        self.assertEqual(len(rows),14)
