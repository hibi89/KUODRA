"""Official OpenDART annual income facts may appear in IS or CIS.

Source: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020
No genuine provider API key/data is used. The old synthetic annual fixture is
altered into official-field-compatible shapes and remains marked synthetic.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from kuodra.cli import analyze_bytes
from kuodra.markets.kr.dart_local import parse_dart_annual

BASE=Path(__file__).resolve().parents[1]/'fixtures'/'synthetic'/'kr_dart.json'


def fixture():
    return json.loads(BASE.read_text(encoding='utf-8'))


def encode(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf-8')


def documented_shape(obj):
    """Drop fields absent from the official fnlttSinglAcntAll response."""
    obj=deepcopy(obj)
    for row in obj['list']:
        row.pop('fs_div',None)
        row.pop('thstrm_dt',None)
    return obj


class DartIsCisContractTests(unittest.TestCase):
    def test_cis_only_income_accepted_without_forging_period_fields(self):
        obj=documented_shape(fixture())
        for r in obj['list']:
            if r['account_id'] in ('ifrs-full_Revenue','ifrs-full_ProfitLoss'):
                r['sj_div']='CIS'
        # Need a single owner-verified ending date, so take only one report year.
        obj['list']=[r for r in obj['list'] if r['bsns_year']=='2024']
        r=analyze_bytes(encode(obj),country='KR',issuer_id='99998888',
            as_of='2025-11-12',dart_fiscal_end='2024-12-31',
            dart_request_fs_div_bound=True)
        self.assertEqual(r['guard'],'HOLD')
        self.assertFalse(r['source_verified'])
        self.assertFalse(r['rights_verified'])
        self.assertEqual(len(r['evidence']),7)
        self.assertEqual(r['periods'],['2024-12-31'])
        metrics={x['metric'] for x in r['evidence']}
        self.assertIn('revenue',metrics)
        self.assertIn('net_income',metrics)

    def test_both_is_and_cis_equal_amounts_are_not_conflicts(self):
        obj=fixture()
        extra=[deepcopy(r) for r in obj['list']
               if r['account_id'] in ('ifrs-full_Revenue','ifrs-full_ProfitLoss')
               and r['bsns_year']=='2024']
        for r in extra:r['sj_div']='CIS'
        obj['list'].extend(extra)
        selected,audit=parse_dart_annual(encode(obj),issuer_id='99998888',
            as_of='2025-11-12',with_audit=True)
        self.assertEqual(len(selected),14)
        self.assertTrue(any(a['metric']=='revenue' and
                            a['candidate_count']==2 for a in audit))

    def test_same_filing_is_cis_disagree_must_reject_not_choose_one(self):
        obj=fixture()
        extra=deepcopy(next(r for r in obj['list']
                            if r['account_id']=='ifrs-full_ProfitLoss'
                            and r['bsns_year']=='2024'))
        extra['sj_div']='CIS'
        extra['thstrm_amount']='999'
        obj['list'].append(extra)
        with self.assertRaisesRegex(ValueError,'RECONCILIATION_SAME_DAY_CONFLICT'):
            parse_dart_annual(encode(obj),issuer_id='99998888',
                as_of='2025-11-12')

    def test_mismatched_cf_in_cis_is_still_denied(self):
        obj=fixture()
        x=next(r for r in obj['list']
               if r['account_id']=='ifrs-full_CashFlowsFromUsedInOperatingActivities')
        x['sj_div']='CIS'
        with self.assertRaisesRegex(ValueError,'DART_STATEMENT_SECTION_MISMATCH'):
            parse_dart_annual(encode(obj),issuer_id='99998888',
                as_of='2025-11-12')

    def test_mismatched_balance_sheet_in_cis_still_denied(self):
        obj=fixture()
        x=next(r for r in obj['list']
               if r['account_id']=='ifrs-full_Inventories')
        x['sj_div']='CIS'
        with self.assertRaisesRegex(ValueError,'DART_STATEMENT_SECTION_MISMATCH'):
            parse_dart_annual(encode(obj),issuer_id='99998888',
                as_of='2025-11-12')

    def test_prior_is_synthetic_case_unchanged(self):
        rows=parse_dart_annual(BASE.read_bytes(),issuer_id='99998888',
            as_of='2025-11-12')
        self.assertEqual(len(rows),14)


if __name__=='__main__':
    unittest.main()
