"""Financial B indicators are evidence-linked review questions, not fraud decisions."""
from __future__ import annotations
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import unittest
from kuodra.cli import analyze_bytes
from kuodra.contracts import observation
from kuodra.markets.kr.dart_local import parse_dart_annual
from kuodra.review import build_review
from kuodra.report import render_html
from kuodra.report_pdf import render_pdf_bytes

KR=Path(__file__).resolve().parents[1]/'fixtures'/'synthetic'/'kr_dart.json'

class FinancialFlagTests(unittest.TestCase):
    def test_growth_review_flags_source_bound(self):
        r=analyze_bytes(KR.read_bytes(),country='KR',issuer_id='99998888',as_of='2025-11-12')
        flags=r['financial_flags']
        codes={x['code'] for x in flags}
        self.assertIn('RECEIVABLES_OUTPACE_REVENUE',codes)
        self.assertIn('INVENTORY_OUTPACES_REVENUE',codes)
        self.assertTrue(all(f['status']=='REVIEW_ONLY_NOT_FRAUD' and f['source_refs'] for f in flags))
        self.assertEqual(r['guard'],'HOLD')
        self.assertFalse(r['trade_executed'])
    def test_html_pdf_label_flags_not_fraud(self):
        r=analyze_bytes(KR.read_bytes(),country='KR',issuer_id='99998888',as_of='2025-11-12')
        html=render_html(r)
        self.assertIn('not fraud findings',html)
        self.assertIn('RECEIVABLES_OUTPACE_REVENUE',html)
        pdf=render_pdf_bytes(r)
        self.assertTrue(pdf.startswith(b'%PDF-'))
    def test_no_comparison_no_growth_flag(self):
        r=analyze_bytes(KR.read_bytes(),country='KR',issuer_id='99998888',as_of='2024-11-12')
        self.assertFalse(any(x['code'].endswith('REVENUE') for x in r['financial_flags']))
    def test_positive_profit_negative_cashflow_context_only(self):
        records=parse_dart_annual(KR.read_bytes(),issuer_id='99998888',as_of='2025-11-12')
        adjusted=[replace(r,value=Decimal('-7')) if
                  r.metric=='operating_cashflow' and r.fiscal_end=='2024-12-31'
                  else r for r in records]
        result=build_review(adjusted,as_of='2025-11-12')
        self.assertIn('PROFIT_POSITIVE_CFO_NEGATIVE',
                      {f['code'] for f in result['financial_flags']})
        self.assertEqual(result['guard'],'HOLD')

if __name__=='__main__':unittest.main()
