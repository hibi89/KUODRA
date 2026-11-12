"""Strict offline peer comparison. No live rankings or inferred investment decisions."""
from __future__ import annotations
from decimal import Decimal

_ALLOWED={'cash_conversion','liabilities_to_equity','growth_revenue','growth_inventory','growth_receivables'}

def compare_peers(subject:dict, peers:list[dict], *, synthetic_sector:dict|None=None):
    if type(subject) is not dict or subject.get('schema')!='kuodra.offline-review.v1':
        raise ValueError('SUBJECT_REPORT_INVALID')
    if type(peers) is not list or not 1 <=len(peers)<=10:
        raise ValueError('PEER_SAMPLE_INVALID')
    key=lambda r:(r.get('country'),r.get('currency'),r.get('statement'),r.get('as_of'),tuple(r.get('periods',[])[:1]))
    sid=(subject['country'],subject['issuer_id'])
    seen={sid}
    if not subject.get('periods'):raise ValueError('SUBJECT_PERIOD_MISSING')
    for p in peers:
        if type(p) is not dict or p.get('schema')!='kuodra.offline-review.v1':raise ValueError('PEER_REPORT_INVALID')
        if key(p)!=key(subject):raise ValueError('PEER_INCOMPARABLE_PERIOD_OR_CURRENCY')
        pid=(p['country'],p['issuer_id'])
        if pid in seen:raise ValueError('DUPLICATE_PEER_ISSUER')
        seen.add(pid)
    if synthetic_sector is not None:
        if (type(synthetic_sector) is not dict or set(synthetic_sector)!={'code','issuers','origin'}
                or synthetic_sector['origin']!='SYNTHETIC_TEST_ONLY'
                or type(synthetic_sector['code']) is not str
                or not synthetic_sector['code'].isalnum()
                or type(synthetic_sector['issuers']) is not list
                or set(synthetic_sector['issuers']) != {subject['issuer_id'],*(p['issuer_id'] for p in peers)}):
            raise ValueError('PEER_SECTOR_EVIDENCE_INVALID')
    base={f['name']:Decimal(f['value']) for f in subject['findings'] if f['name'] in _ALLOWED}
    cohort=[]
    for p in peers:
        facts={f['name']:Decimal(f['value']) for f in p['findings'] if f['name'] in _ALLOWED}
        common=sorted(set(base)&set(facts))
        cohort.append({'issuer_id':p['issuer_id'],'common_metrics':common,
                       'deltas':{m:str(base[m]-facts[m]) for m in common}})
    status=('SYNTHETIC_SECTOR_COHORT_HOLD' if synthetic_sector is not None else 'DESCRIPTIVE_PEER_ONLY_UNVERIFIED') if any(x['common_metrics'] for x in cohort) else 'INSUFFICIENT_PEERS'
    return {'schema':'kuodra.offline-peers.v1','status':status,'guard':'HOLD','source_rights_verified':False,
            'country':subject['country'],'subject_issuer':subject['issuer_id'],'as_of':subject['as_of'],
            'comparison_count':len(cohort),'comparisons':cohort,
            'sector_policy':{'code':synthetic_sector['code'],'source':'SYNTHETIC_TEST_ONLY','authenticated':False} if synthetic_sector is not None else {'authenticated':False,'reason':'NO_VERIFIED_SECTOR_CLASSIFICATION'},
            'limitations':['Peer equivalence requires additional independent sector/business-model validation',
                'Unauthenticated local files are NOT official issuer facts',
                'No investment ranking or predictive claim']}
