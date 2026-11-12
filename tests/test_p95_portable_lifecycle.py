"""Staging-only portable lifecycle tests with strict customer file preservation."""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from kuodra.portable_manifest import create_manifest
from kuodra.portable_lifecycle import install, verify, remove, main


class PortableLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.source=self.base/'built-program'
        self.source.mkdir()
        (self.source/'KUODRA.exe').write_bytes(b'SYNTHETIC NOT EXECUTABLE')
        libs=self.source/'_internal'
        libs.mkdir()
        (libs/'lib.dll').write_bytes(b'DEPENDENCY')
        self.manifest=self.base/'manifest.json'
        create_manifest(self.source,self.manifest)
        self.workspace=self.base/'한글_고객_검수'
        self.workspace.mkdir()
        self.sentinel=self.workspace/'CUSTOMER_ORIGINAL.txt'
        self.sentinel.write_text('DO_NOT_DELETE',encoding='utf8')

    def test_install_verify_and_confirmed_remove_keep_unrelated_data(self):
        r=install(self.source,self.manifest,self.workspace,'kuodra-v1')
        self.assertEqual(r['status'],'UNSIGNED_OWNER_STAGING_INSTALLED')
        self.assertFalse(r['consumer_release_approved'])
        dest=self.workspace/'kuodra-v1'
        self.assertEqual((dest/'KUODRA.exe').read_bytes(),b'SYNTHETIC NOT EXECUTABLE')
        self.assertEqual(verify(self.workspace,'kuodra-v1',self.manifest)['status'],
                         'STAGING_BYTES_MATCH_NOT_SIGNED')
        with self.assertRaisesRegex(ValueError,'EXPLICIT_OWNER_CONFIRMATION'):
            remove(self.workspace,'kuodra-v1',self.manifest)
        self.assertTrue(dest.exists())
        result=remove(self.workspace,'kuodra-v1',self.manifest,confirm=True)
        self.assertFalse(dest.exists())
        self.assertEqual(result['status'],'STAGING_VERIFIED_PACKAGE_REMOVED')
        self.assertFalse(result['customer_data_removed'])
        self.assertEqual(self.sentinel.read_text(encoding='utf8'),'DO_NOT_DELETE')
        self.assertTrue(self.source.exists())

    def test_user_owned_destination_is_never_overwritten(self):
        dest=self.workspace/'customer'
        dest.mkdir()
        important=dest/'work.csv'
        important.write_text('KEEP',encoding='utf8')
        with self.assertRaisesRegex(FileExistsError,'TARGET_EXISTS_NO_OVERWRITE'):
            install(self.source,self.manifest,self.workspace,'customer')
        self.assertEqual(important.read_text(encoding='utf8'),'KEEP')

    def test_modified_installed_file_blocks_remove(self):
        install(self.source,self.manifest,self.workspace,'kuodra')
        (self.workspace/'kuodra'/'KUODRA.exe').write_bytes(b'ALTERED')
        with self.assertRaisesRegex(ValueError,'PORTABLE_MANIFEST_CONTENT_MISMATCH'):
            remove(self.workspace,'kuodra',self.manifest,confirm=True)
        self.assertTrue((self.workspace/'kuodra'/'KUODRA.exe').exists())
        self.assertEqual(self.sentinel.read_text(encoding='utf8'),'DO_NOT_DELETE')

    def test_user_extra_file_in_package_blocks_remove(self):
        install(self.source,self.manifest,self.workspace,'kuodra')
        added=self.workspace/'kuodra'/'USER_FINANCIAL.xlsx'
        added.write_bytes(b'OWNED_DATA')
        with self.assertRaisesRegex(ValueError,'PORTABLE_MANIFEST_CONTENT_MISMATCH'):
            remove(self.workspace,'kuodra',self.manifest,confirm=True)
        self.assertEqual(added.read_bytes(),b'OWNED_DATA')

    def test_side_by_side_upgrade_keeps_old_version(self):
        install(self.source,self.manifest,self.workspace,'version-one')
        second=self.base/'second'
        second.mkdir()
        (second/'KUODRA.exe').write_bytes(b'NEW_RELEASE_SOURCE')
        libs=second/'_internal';libs.mkdir()
        (libs/'lib.dll').write_bytes(b'DEPENDENCY')
        manifest2=self.base/'manifest2.json'
        create_manifest(second,manifest2)
        install(second,manifest2,self.workspace,'version-two')
        self.assertTrue((self.workspace/'version-one'/'KUODRA.exe').exists())
        self.assertEqual((self.workspace/'version-two'/'KUODRA.exe').read_bytes(),
                         b'NEW_RELEASE_SOURCE')
        remove(self.workspace,'version-one',self.manifest,confirm=True)
        self.assertTrue((self.workspace/'version-two'/'KUODRA.exe').exists())
        self.assertEqual(self.sentinel.read_text(encoding='utf8'),'DO_NOT_DELETE')

    def test_slot_traversal_is_rejected(self):
        for slot in ('../outside','.', 'C:/Users','', 'name with spaces'):
            with self.subTest(slot=slot):
                with self.assertRaisesRegex(ValueError,'STAGING_SLOT_INVALID'):
                    install(self.source,self.manifest,self.workspace,slot)

    def test_symlink_install_path_denied(self):
        dest=self.workspace/'kuodra'
        try:
            dest.symlink_to(self.source,target_is_directory=True)
        except OSError:
            self.skipTest('Host disallows directory symlinks')
        with self.assertRaisesRegex(ValueError,'STAGING_TARGET_SYMLINK_DENIED'):
            install(self.source,self.manifest,self.workspace,'kuodra')
        self.assertTrue(self.source.exists())

    def test_wrong_manifest_denies_install(self):
        (self.source/'KUODRA.exe').write_bytes(b'CHANGED')
        with self.assertRaisesRegex(ValueError,'PORTABLE_MANIFEST_CONTENT_MISMATCH'):
            install(self.source,self.manifest,self.workspace,'kuodra')
        self.assertFalse((self.workspace/'kuodra').exists())

    def test_cli_lifecycle_with_explicit_confirm(self):
        with redirect_stdout(StringIO()) as buf:
            self.assertEqual(main(['install',str(self.source),str(self.manifest),
                                   str(self.workspace),'test-slot']),0)
        self.assertEqual(json.loads(buf.getvalue())['status'],
                         'UNSIGNED_OWNER_STAGING_INSTALLED')
        with redirect_stdout(StringIO()) as buf:
            self.assertEqual(main(['verify',str(self.workspace),str(self.manifest),'test-slot']),0)
        self.assertEqual(json.loads(buf.getvalue())['status'],'STAGING_BYTES_MATCH_NOT_SIGNED')
        with redirect_stdout(StringIO()) as buf:
            self.assertEqual(main(['remove',str(self.workspace),str(self.manifest),
                                   'test-slot','--confirm-remove']),0)
        self.assertEqual(json.loads(buf.getvalue())['status'],
                         'STAGING_VERIFIED_PACKAGE_REMOVED')
        self.assertEqual(self.sentinel.read_text(encoding='utf8'),'DO_NOT_DELETE')


if __name__=='__main__':
    unittest.main()
