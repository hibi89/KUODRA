"""Synthetic-only holdout: no market performance claims, no group/time leakage."""
from __future__ import annotations
from datetime import date, timedelta
import json
import unittest
from kuodra.heldout import evaluate_synthetic_heldout


def fake_rows():
    arr=[]
    start=date(2021,1,1)
    for i in range(30):
        d=start+timedelta(days=i)
        arr.append({'issuer_id':'TRAIN_A','observed_at':d.isoformat(),
                    'released_at':(d+timedelta(days=1)).isoformat(),
                    'split':'train','feature':str(i),'target':str(i*2+3)})
    for i in range(12):
        d=start+timedelta(days=40+i)
        arr.append({'issuer_id':'TEST_B','observed_at':d.isoformat(),
                    'released_at':(d+timedelta(days=1)).isoformat(),
                    'split':'test','feature':str(i+40),'target':str((i+40)*2+3)})
    return arr


def raw(rows=None):
    return json.dumps({'schema':'kuodra.synthetic-heldout.v1',
                       'mode':'SYNTHETIC_TEST_ONLY','rows':rows or fake_rows()},
                      separators=(',',':')).encode()


class HoldoutTests(unittest.TestCase):
    def evaluate(self,b,**kw):
        return evaluate_synthetic_heldout(b,as_of=kw.get('as_of','2021-04-30'),
                                          owner_consent=kw.get('consent',True))
    def test_disjoint_time_issuer_and_dummy(self):
        r=self.evaluate(raw())
        self.assertEqual(r['status'],'EVALUATED_SYNTHETIC_ONLY')
        self.assertEqual(r['guard'],'HOLD')
        self.assertLess(float(r['model_mae']),float(r['dummy_mae']))
        self.assertFalse(r['prediction_claim'])
        self.assertFalse(r['raw_rows_exported'])
        self.assertNotIn('TEST_B',str(r))
    def test_no_consent(self):
        with self.assertRaisesRegex(ValueError,'CONSENT'):self.evaluate(raw(),consent=False)
    def test_future_release(self):
        v=fake_rows();v[-1]['released_at']='2027-02-02'
        with self.assertRaisesRegex(ValueError,'LEAKAGE'):self.evaluate(raw(v))
    def test_group_leakage(self):
        v=fake_rows();v[-1]['issuer_id']='TRAIN_A'
        with self.assertRaisesRegex(ValueError,'ISSUER_LEAKAGE'):self.evaluate(raw(v))
    def test_time_leakage(self):
        v=fake_rows();v[0]['released_at']='2021-02-15'
        with self.assertRaisesRegex(ValueError,'TIME_LEAKAGE'):self.evaluate(raw(v))
    def test_duplicate_observation(self):
        v=fake_rows();v.append(dict(v[-1]))
        with self.assertRaisesRegex(ValueError,'DUPLICATE_OBSERVATION'):self.evaluate(raw(v))
    def test_no_sample(self):
        r=self.evaluate(raw(fake_rows()[:21]))
        self.assertEqual(r['status'],'NO_TRAIN_INSUFFICIENT_SAMPLES')
    def test_constant_feature(self):
        v=fake_rows()
        for r in v:r['feature']='1'
        r=self.evaluate(raw(v))
        self.assertEqual(r['status'],'NO_TRAIN_CONSTANT_FEATURE')
    def test_reject_market_mode(self):
        b=raw().replace(b'SYNTHETIC_TEST_ONLY',b'REAL_MARKET')
        with self.assertRaisesRegex(ValueError,'SYNTHETIC_CONTRACT'):self.evaluate(b)
    def test_reject_nonfinite_number(self):
        v=fake_rows();v[0]['target']='NaN'
        with self.assertRaisesRegex(ValueError,'NUMBER'):self.evaluate(raw(v))
    def test_reject_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError,'JSON_INVALID'):
            self.evaluate(b'{"schema":"x","schema":"y"}')
    def test_reject_cross_year_source(self):
        v=fake_rows();v[-1]['observed_at']='2021-01-02'
        with self.assertRaisesRegex(ValueError,'TIME_LEAKAGE'):self.evaluate(raw(v))

if __name__=='__main__':unittest.main()
