"""Source bytes must not be taken from links, changing or oversized evidence."""
from pathlib import Path
import os
import tempfile
import unittest
from kuodra.safe_io import read_bounded_local

class SafeSourceTests(unittest.TestCase):
    def test_allowed_bytes_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data';p.write_bytes(b'1234567')
            self.assertEqual(read_bounded_local(p),b'1234567')
            self.assertEqual(p.read_bytes(),b'1234567')
    def test_reject_oversized(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data';p.write_bytes(b'a'*11)
            with self.assertRaisesRegex(ValueError,'FILE_POLICY'):read_bounded_local(p,limit=10)
    def test_reject_zero_byte(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data';p.write_bytes(b'')
            with self.assertRaisesRegex(ValueError,'FILE_POLICY'):read_bounded_local(p)
    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'real';p.write_bytes(b'x');link=Path(d)/'link'
            try:link.symlink_to(p)
            except (OSError,NotImplementedError):self.skipTest('no symlink privilege')
            with self.assertRaisesRegex(ValueError,'FILE_POLICY'):read_bounded_local(link)
    def test_reject_hardlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'real';p.write_bytes(b'x');link=Path(d)/'link';os.link(p,link)
            with self.assertRaisesRegex(ValueError,'FILE_POLICY'):read_bounded_local(link)
    def test_missing(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'UNAVAILABLE'):read_bounded_local(Path(d)/'missing')
    def test_bad_limit(self):
        with self.assertRaisesRegex(ValueError,'LIMIT_INVALID'):read_bounded_local('no',limit=-1)
    def test_reject_directory(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'FILE_POLICY'):read_bounded_local(d)

if __name__=='__main__':unittest.main()
