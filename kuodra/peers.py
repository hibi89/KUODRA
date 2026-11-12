"""Strict offline peer comparison. No live rankings or inferred investment decisions."""
from __future__ import annotations
from decimal import Decimal

_ALLOWED={'cash_conversion','liabilities_to_equity','growth_revenue','growth_inventory','growth_receivables'}

def compare_peers(subject:dict, peers:list[dict]):
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
    base={f['name']:Decimal(f['value']) for f in subject['findings'] if f['name'] in _ALLOWED}
    cohort=[]
    for p in peers:
        facts={f['name']:Decimal(f['value']) for f in p['findings'] if f['name'] in _ALLOWED}
        common=sorted(set(base)&set(facts))
        cohort.append({'issuer_id':p['issuer_id'],'common_metrics':common,
                       'deltas':{m:str(base[m]-facts[m]) for m in common}})
    status='DESCRIPTIVE_PEER_ONLY_UNVERIFIED' if any(x['common_metrics'] for x in cohort) else 'INSUFFICIENT_PEERS'
    return {'schema':'kuodra.offline-peers.v1','status':status,'guard':'HOLD','source_rights_verified':False,
            'country':subject['country'],'subject_issuer':subject['issuer_id'],'as_of':subject['as_of'],
            'comparison_count':len(cohort),'comparisons':cohort,
            'limitations':['Peer equivalence requires additional independent sector/business-model validation',
                'Unauthenticated local files are NOT official issuer facts',
                'No investment ranking or predictive claim']}
