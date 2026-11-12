"""Output failure must never delete a replaced user-owned file.

Synthetic local I/O scenario. This does not prove OS-level race security,
but demonstrates no recursive/user-file cleanup after a partial export.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import kuodra.report as reports
from kuodra.cli import analyze_bytes

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic" / "kr_dart.json"


class OutputFailurePreservationTests(TestCase):
    def test_failed_second_write_never_deletes_replaced_first_path(self):
        review = analyze_bytes(
            _FIXTURE.read_bytes(), country="KR", issuer_id="99998888",
            as_of="2025-11-12",
        )
        with TemporaryDirectory() as td:
            root = Path(td)
            sentinel = root / "customer-important.txt"
            sentinel.write_text("DO_NOT_DELETE", encoding="utf-8")
            real_open = reports.os.open
            attempts = []

            def simulated_race_open(filename, flags, mode=0o777):
                attempts.append(str(filename))
                if len(attempts) == 2:
                    # Simulates an unrelated owner replacing the path created
                    # for the first export after the first file was closed.
                    (root / "bundle.json").write_text("CUSTOMER_REPLACEMENT", encoding="utf-8")
                    raise OSError("SIMULATED_SECOND_FILE_FAILURE")
                return real_open(filename, flags, mode)

            with patch.object(reports.os, "open", side_effect=simulated_race_open):
                with self.assertRaisesRegex(OSError, "SIMULATED_SECOND_FILE_FAILURE"):
                    reports.export_local(review, root, "bundle")
            self.assertEqual((root / "bundle.json").read_text(encoding="utf-8"),
                             "CUSTOMER_REPLACEMENT")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "DO_NOT_DELETE")
            self.assertFalse((root / "bundle.receipt.json").exists())
            # A partial bundle cannot be silently overwritten on retry.
            with self.assertRaises(FileExistsError):
                reports.export_local(review, root, "bundle")

    def test_new_output_refuses_preexisting_receipt_even_without_report_files(self):
        review = analyze_bytes(
            _FIXTURE.read_bytes(), country="KR", issuer_id="99998888",
            as_of="2025-11-12",
        )
        with TemporaryDirectory() as td:
            root = Path(td)
            receipt = root / "bundle.receipt.json"
            receipt.write_bytes(b"CUSTOMER_RECEIPT")
            with self.assertRaises(FileExistsError):
                reports.export_local(review, root, "bundle")
            self.assertEqual(receipt.read_bytes(), b"CUSTOMER_RECEIPT")
