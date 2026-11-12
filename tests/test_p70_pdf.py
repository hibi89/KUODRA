"""P70 reportlab PDF generation tests use synthetic source values only."""
from pathlib import Path
import tempfile,unittest
from kuodra.markets.us.sec_local import parse_sec_companyfacts
from kuodra.review import build_review
from kuodra.report import export_local
from kuodra.report_pdf import render_pdf_bytes

BASE=Path(__file__).resolve().parents[1]/'fixtures/synthetic/us_companyfacts.json'
class P70PDFTests(unittest.TestCase):
    def report(self):
        return build_review(parse_sec_companyfacts(BASE.read_bytes(),issuer_id='0009999888',as_of='2025-03-01'),as_of='2025-03-01')
    def test_pdf_generated_with_human_hold(self):
        pdf=render_pdf_bytes(self.report())
        self.assertTrue(pdf.startswith(b'%PDF-'))
        self.assertGreater(len(pdf),2000)
        try:
            import fitz
        except ImportError:
            return
        d=fitz.open(stream=pdf,filetype='pdf')
        self.assertLessEqual(len(d),3)
        txt=''.join(p.get_text() for p in d)
        self.assertIn('HOLD',txt)
        self.assertIn('CashFlow',txt)
        self.assertIn('Source evidence',txt)
    def test_pdf_export_is_opt_in_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            r=self.report();d=Path(temp)
            out=export_local(r,d,'trial',pdf=True)
            self.assertEqual(set(out),{'json','html','pdf'})
            self.assertTrue((d/'trial.pdf').read_bytes().startswith(b'%PDF-'))
            sha=(d/'trial.pdf').read_bytes()
            with self.assertRaises(FileExistsError):export_local(r,d,'trial',pdf=True)
            self.assertEqual((d/'trial.pdf').read_bytes(),sha)
    def test_unicode_refused_until_font_review(self):
        r=self.report();r['warnings'].append('미검증')
        with self.assertRaisesRegex(ValueError,'NON_ASCII'):
            render_pdf_bytes(r)
    def test_outsize_report_refused(self):
        r=self.report();r['evidence']=r['evidence']*8
        with self.assertRaisesRegex(ValueError,'TOO_LARGE'):
            render_pdf_bytes(r)

if __name__=='__main__':unittest.main()
