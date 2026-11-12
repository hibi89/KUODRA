"""Owner-consented *local* cross-sectional, non-predictive financial exploration.

Reuse KIC's independently tested Benjamini-Hochberg engine. Raw private input
is never copied to the report or sent over the network. This is descriptive
statistics with independence unverified, NOT stock prediction or model training.
"""
from __future__ import annotations
from hashlib import sha256
from kuodra.contracts import parse_date
from proofinvest.kuodra_unified_core import normalize_local_csv
from proofinvest.kuodra_stats import cross_section_fdr


def explore_local_cross_section(raw:bytes, *, metrics:tuple[str,...],
                                observation_at:str, as_of:str,
                                owner_consent:bool=False) ->dict:
    if owner_consent is not True:
        raise ValueError('STATS_EXPLICIT_OWNER_CONSENT_REQUIRED')
    if type(raw) is not bytes or not 0<len(raw)<=1_000_000:
        raise ValueError('STATS_SOURCE_SIZE_DENIED')
    if type(metrics) is not tuple or not 2<=len(metrics)<=12:
        raise ValueError('STATS_METRICS_INVALID')
    observed=parse_date(observation_at)
    cutoff=parse_date(as_of)
    if observed>cutoff:
        raise ValueError('STATS_OBSERVATION_AFTER_CUTOFF')
    h=sha256(raw).hexdigest()
    dataset=normalize_local_csv(
        raw,dataset_id='stats'+h[:20],source_id='owned'+h[:20],
        access_level='PRIVATE',consent=True)
    report=cross_section_fdr(dataset,metrics=metrics,
        observation_at=observed.isoformat()+'T00:00:00Z',
        as_of=cutoff.isoformat()+'T00:00:00Z',min_pairs=30,max_results=3)
    # Public KIC stats result contains only cross-sectional effect candidates,
    # no raw owner CSV rows or individual issuer values.
    return {'schema':'kuodra.local-stats-gate.v1','status':report['status'],
            'guard':'HOLD','owner_approved_local_analysis':True,
            'publisher_authenticated':False,'commercial_rights_verified':False,
            'model_trained':False,'prediction_claim':False,
            'dataset_sha256':h,'eligible_entities':report.get('eligible_entities',0),
            'hypotheses_planned':report.get('hypotheses_planned'),
            'multiple_testing_method':report.get('multiple_testing_method'),
            'insights':report.get('insights',[]),
            'reason':report.get('reason'),
            'limitations':['Sample independence and financial causality are not verified',
                           'No validated stock return or probability forecast',
                           'Input remains on owner local host; derived report is private']}
