"""Selected-runtime dependency listing is evidence, not license acceptance."""
from __future__ import annotations
import json
import unittest
from unittest.mock import patch
from io import StringIO
from contextlib import redirect_stdout

from kuodra.dependency_ledger import inventory,main

class DependencyLedgerTests(unittest.TestCase):
    def test_never_marks_license_clear_or_bundle_approved(self):
        report=inventory()
        self.assertEqual(report['schema'],'kuodra.oss-dependency-ledger.v1')
        self.assertFalse(report['commercial_distribution_approved'])
        self.assertFalse(report['windows_bundle_audited'])
        self.assertEqual(report['completeness'],
                         'SELECTED_RUNTIME_PACKAGES_ONLY_NOT_ALL_TRANSITIVE_DLLS')
        self.assertGreaterEqual(len(report['distributions']),4)
        self.assertTrue(all(item['license_review_approved'] is False
                            for item in report['distributions']))
        serialized=json.dumps(report)
        self.assertNotIn('KUODRA_DART_API_KEY',serialized)
    def test_required_core_installed_on_ci(self):
        report=inventory(require_core=True)
        self.assertEqual(len([item for item in report['distributions']
             if item['distribution'] in ('numpy','scipy','scikit-learn','reportlab')
             and item['status']=='MANUAL_LICENSE_AND_BUNDLED_NOTICE_REVIEW_REQUIRED']),4)
    def test_cli_json_reports_no_sale_go(self):
        out=StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(['--require-core']),0)
        report=json.loads(out.getvalue())
        self.assertFalse(report['commercial_distribution_approved'])
    def test_unknown_license_is_not_cleared(self):
        class Metadata(dict):
            def get_all(self,k,default=None):return []
        class Dist:
            version='1.0'
            metadata=Metadata({})
        with patch('kuodra.dependency_ledger.metadata.distribution',return_value=Dist()):
            report=inventory()
        self.assertTrue(all(item['license_review_approved'] is False
                            for item in report['distributions']))
        self.assertTrue(all(item['metadata_license_hint']=='NOT_DECLARED_REVIEW_REQUIRED'
                            for item in report['distributions']))
    def test_missing_core_is_not_silently_approved(self):
        from importlib import metadata
        with patch('kuodra.dependency_ledger.metadata.distribution',
            side_effect=metadata.PackageNotFoundError('numpy')):
            with self.assertRaisesRegex(ValueError,'REQUIRED_DISTRIBUTION_MISSING'):
                inventory(require_core=True)


if __name__=='__main__':
    unittest.main()
