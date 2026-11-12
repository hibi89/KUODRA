"""New product country adapters -> copied legacy KIC canonical end-to-end.

These tests must execute on the GitHub develop checkout that includes proofinvest.
"""
from pathlib import Path
import importlib.util
import unittest
from kuodra.kic_bridge import normalize_observations_via_kic
from kuodra.markets.kr.dart_local import parse_dart_annual
from kuodra.markets.us.sec_local import parse_sec_companyfacts

ROOT = Path(__file__).resolve().parents[1]

class KICBridgeTests(unittest.TestCase):
    def test_us_to_legacy_canonical(self):
        raw = (ROOT / 'fixtures/synthetic/us_companyfacts.json').read_bytes()
        data = parse_sec_companyfacts(raw, issuer_id='0009999888', as_of='2025-03-01')
        converted = normalize_observations_via_kic(data, as_of='2025-03-01')
        self.assertEqual(converted['canonical']['rows'], 14)
        self.assertEqual(converted['original_country'], 'US')
        self.assertFalse(converted['publisher_authenticated'])
        self.assertEqual(converted['guard'], 'HOLD')
        self.assertTrue(all(r['entity_id'] == 'US_0009999888' for r in converted['canonical']['records']))

    def test_kr_to_legacy_canonical(self):
        raw = (ROOT / 'fixtures/synthetic/kr_dart.json').read_bytes()
        data = parse_dart_annual(raw, issuer_id='99998888', as_of='2025-03-01')
        converted = normalize_observations_via_kic(data, as_of='2025-03-01')
        self.assertEqual(converted['canonical']['rows'], 14)
        self.assertEqual(converted['original_country'], 'KR')
        self.assertTrue(all(r['unit'] == 'KRW' for r in converted['canonical']['records']))

    def test_mixed_country_rejected(self):
        kr = parse_dart_annual((ROOT / 'fixtures/synthetic/kr_dart.json').read_bytes(),issuer_id='99998888',as_of='2025-03-01')
        us = parse_sec_companyfacts((ROOT / 'fixtures/synthetic/us_companyfacts.json').read_bytes(),issuer_id='0009999888',as_of='2025-03-01')
        with self.assertRaisesRegex(ValueError,'MIXED_SOURCE_SCOPE'):
            normalize_observations_via_kic(kr + us, as_of='2025-03-01')

    def test_future_release_rejected(self):
        kr = parse_dart_annual((ROOT / 'fixtures/synthetic/kr_dart.json').read_bytes(),issuer_id='99998888',as_of='2025-03-01')
        with self.assertRaisesRegex(ValueError,'FUTURE_RELEASE'):
            normalize_observations_via_kic(kr, as_of='2024-03-01')

if __name__=='__main__': unittest.main()
