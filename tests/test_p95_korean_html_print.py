"""Korean browser-printable HTML does not bundle font binaries.

The programmatic ReportLab PDF remains ASCII until separate embedded-font
license review; users may print localized HTML to PDF using their own browser.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from kuodra.cli import analyze_bytes
from kuodra.gui import run_selected
from kuodra.report import render_html, export_local
from kuodra.release_gate import verify_evidence_bundle

KR=Path(__file__).resolve().parents[1]/'fixtures'/'synthetic'/'kr_dart.json'


class KoreanPrintReportTests(unittest.TestCase):
    def report(self):
        return analyze_bytes(KR.read_bytes(),country='KR',
                             issuer_id='99998888',as_of='2025-11-12')

    def test_html_korean_headings_preserve_guard_and_evidence(self):
        report=self.report()
        html=render_html(report,language='ko')
        self.assertIn('lang="ko"',html)
        self.assertIn('기업 재무 근거 검증',html)
        self.assertIn('검토 보류(HOLD)',html)
        self.assertIn('공시 원문 수치 근거',html)
        self.assertIn('@media print',html)
        self.assertIn('Malgun Gothic',html)
        self.assertIn('cash_conversion',html)
        self.assertIn('2024-12-31',html)
        self.assertNotIn('<script',html)
        self.assertNotIn('@font-face',html)
        self.assertNotIn('https://fonts.',html)
        self.assertEqual(report['guard'],'HOLD')
        self.assertFalse(report['rights_verified'])

    def test_korean_untrusted_text_is_html_escaped(self):
        report=self.report()
        report['warnings'].append('<script>alert("미검증")</script>')
        html=render_html(report,language='ko')
        self.assertNotIn('<script>alert(',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('미검증',html)

    def test_html_language_is_restricted(self):
        with self.assertRaisesRegex(ValueError,'REPORT_LANGUAGE_UNSUPPORTED'):
            render_html(self.report(),language='xx')

    def test_gui_controller_korean_export_and_receipt(self):
        with TemporaryDirectory() as td:
            report,paths=run_selected(country='KR',issuer_id='99998888',
                as_of='2025-11-12',source=str(KR),output_dir=td,
                name='korean',language='ko')
            html=Path(paths['html']['path']).read_text(encoding='utf8')
            self.assertIn('lang="ko"',html)
            self.assertIn('재무 분석 및 계산 근거',html)
            checked=verify_evidence_bundle(td,'korean')
            self.assertEqual(checked['status'],'UNSIGNED_RECEIPT_MATCHED_NOT_AUTHENTICATED')
            self.assertEqual(report['guard'],'HOLD')

    def test_default_english_report_is_backwards_compatible(self):
        english=render_html(self.report())
        self.assertIn('lang="en"',english)
        self.assertIn('Corporate evidence',english)
        self.assertNotIn('lang="ko"',english)


if __name__=='__main__':
    unittest.main()
