"""P70: strong local consent, no raw export, statistical claims guarded."""
import csv
from io import StringIO
from datetime import date,timedelta
import unittest
from kuodra.exploration import explore_local_cross_section


def stats_fixture(*,n=36,future=False):
    out=StringIO(newline='');writer=csv.writer(out,lineterminator='\n')
    writer.writerow(('entity_id','metric_id','observation_at','available_at','value','unit'))
    for i in range(n):
        for metric,v in [('revenue',str(i+1)),('cashflow',str(3*(i+1)+7))]:
            writer.writerow((f'firm{i:03d}',metric,'2024-12-31T00:00:00Z',
                             '2026-01-01T00:00:00Z' if future else '2025-02-01T00:00:00Z',v,'USD'))
    return out.getvalue().encode('utf8')

class LocalStatsTests(unittest.TestCase):
    def test_without_consent_blocked(self):
        with self.assertRaisesRegex(ValueError,'CONSENT_REQUIRED'):
            explore_local_cross_section(stats_fixture(),metrics=('revenue','cashflow'),
                observation_at='2024-12-31',as_of='2025-12-31')
    def test_synthetic_thirty_six_issuers_fdr_no_prediction(self):
        r=explore_local_cross_section(stats_fixture(),metrics=('revenue','cashflow'),
            observation_at='2024-12-31',as_of='2025-12-31',owner_consent=True)
        self.assertEqual(r['status'],'EXPLORATORY_INDEPENDENCE_UNVERIFIED')
        self.assertEqual(r['eligible_entities'],36)
        self.assertEqual(r['hypotheses_planned'],1)
        self.assertEqual(r['multiple_testing_method'],'BENJAMINI_HOCHBERG')
        self.assertFalse(r['model_trained'])
        self.assertFalse(r['prediction_claim'])
        self.assertEqual(r['guard'],'HOLD')
        self.assertTrue(r['insights'])
        self.assertNotIn('records',str(r))
    def test_not_enough_issuers_stays_insufficient(self):
        r=explore_local_cross_section(stats_fixture(n=10),metrics=('revenue','cashflow'),
            observation_at='2024-12-31',as_of='2025-12-31',owner_consent=True)
        self.assertEqual(r['status'],'INSUFFICIENT_EVIDENCE')
        self.assertEqual(r['insights'],[])
    def test_future_released_not_analyzed(self):
        r=explore_local_cross_section(stats_fixture(future=True),metrics=('revenue','cashflow'),
            observation_at='2024-12-31',as_of='2025-12-31',owner_consent=True)
        self.assertEqual(r['status'],'INSUFFICIENT_EVIDENCE')
        self.assertEqual(r['insights'],[])
    def test_future_observation_rejected(self):
        with self.assertRaisesRegex(ValueError,'OBSERVATION_AFTER_CUTOFF'):
            explore_local_cross_section(stats_fixture(),metrics=('revenue','cashflow'),
                observation_at='2026-12-31',as_of='2025-12-31',owner_consent=True)

if __name__=='__main__':unittest.main()
