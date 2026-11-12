"""P95 portable integrity is staging-only, unsigned, network-free."""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
import unittest
from kuodra.portable_manifest import (
    inventory,create_manifest,verify_manifest,
)

class PortableManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)/'package'
        self.folder.mkdir()
        (self.folder/'KUODRA.exe').write_bytes(b'synthetic executable bytes')
        inside=self.folder/'_internal'
        inside.mkdir()
        (inside/'core.pyd').write_bytes(b'dependencies')
        self.manifest=Path(self.temp.name)/'manifest.json'
    def create(self):
        return create_manifest(self.folder,self.manifest)
    def test_create_and_verify_exact_bytes(self):
        r=self.create()
        self.assertEqual(r['schema'],'kuodra.unsigned-portable-inventory.v1')
        self.assertFalse(r['signature_verified'])
        v=verify_manifest(self.folder,self.manifest)
        self.assertEqual(v['file_count'],2)
        self.assertFalse(v['consumer_release_approved'])
        self.assertEqual(v['inventory_sha256'],r['inventory_sha256'])
    def test_manifest_no_overwrite(self):
        self.create()
        with self.assertRaises(FileExistsError):self.create()
    def test_modified_binary_rejected(self):
        self.create()
        (self.folder/'KUODRA.exe').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'CONTENT_MISMATCH'):
            verify_manifest(self.folder,self.manifest)
    def test_extra_file_rejected(self):
        self.create()
        (self.folder/'addon.dll').write_bytes(b'new')
        with self.assertRaisesRegex(ValueError,'CONTENT_MISMATCH'):
            verify_manifest(self.folder,self.manifest)
    def test_missing_file_rejected(self):
        self.create()
        (self.folder/'_internal'/'core.pyd').unlink()
        with self.assertRaisesRegex(ValueError,'CONTENT_MISMATCH'):
            verify_manifest(self.folder,self.manifest)
    def test_fake_release_approval_rejected(self):
        self.create()
        doc=json.loads(self.manifest.read_text(encoding='utf-8'))
        doc['consumer_release_approved']=True
        self.manifest.write_text(json.dumps(doc),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'FAKE_RELEASE_APPROVAL'):
            verify_manifest(self.folder,self.manifest)
    def test_duplicate_json_key_rejected(self):
        self.create()
        self.manifest.write_text('{"schema":"a","schema":"b"}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'MANIFEST_JSON_INVALID'):
            verify_manifest(self.folder,self.manifest)
    def test_symlink_in_package_denied(self):
        target=self.folder/'KUODRA.exe'
        link=self.folder/'link.exe'
        try:link.symlink_to(target)
        except OSError:self.skipTest('Host disallows symlinks')
        with self.assertRaisesRegex(ValueError,'PORTABLE_SYMLINK_DENIED'):
            inventory(self.folder)
    def test_hardlink_denied(self):
        link=self.folder/'hardlink.exe'
        try:os.link(self.folder/'KUODRA.exe',link)
        except OSError:self.skipTest('Host disallows hardlinks')
        with self.assertRaisesRegex(ValueError,'LINK_OR_NONFILE_DENIED'):
            inventory(self.folder)
    def test_private_env_path_denied(self):
        (self.folder/'.env').write_bytes(b'private')
        with self.assertRaisesRegex(ValueError,'PRIVATE_PATH_DENIED'):
            inventory(self.folder)
    def test_case_insensitive_duplicate_denied(self):
        first=self.folder/'readme'
        second=self.folder/'README'
        first.write_bytes(b'a')
        try:second.write_bytes(b'b')
        except OSError:self.skipTest('Case-insensitive filesystem')
        if first.read_bytes()==second.read_bytes():
            self.skipTest('Host filesystem aliases uppercase filename')
        with self.assertRaisesRegex(ValueError,'CASE_INSENSITIVE_COLLISION'):
            inventory(self.folder)
    def test_cannot_save_manifest_inside_package(self):
        with self.assertRaisesRegex(ValueError,'MUST_BE_OUTSIDE_FOLDER'):
            create_manifest(self.folder,self.folder/'manifest.json')
    def test_manifest_record_cannot_claim_signature(self):
        self.create()
        doc=json.loads(self.manifest.read_text(encoding='utf-8'))
        doc['signature_verified']=True
        self.manifest.write_text(json.dumps(doc),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'FAKE_RELEASE_APPROVAL'):
            verify_manifest(self.folder,self.manifest)


if __name__=='__main__':unittest.main()
