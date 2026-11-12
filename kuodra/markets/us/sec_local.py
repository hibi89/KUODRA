"""Offline SEC CompanyFacts *shape* adapter. No source authenticity claim."""
from __future__ import annotations
from kuodra.contracts import bounded_json, digest, observation, parse_date, validate_entity

TAGS={'Revenues':'revenue','RevenueFromContractWithCustomerExcludingAssessedTax':'revenue','NetIncomeLoss':'net_income',
'NetCashProvidedByUsedInOperatingActivities':'operating_cashflow',
'AccountsNotesAndOtherReceivablesNetCurrent':'receivables',
'InventoryNet':'inventory','Liabilities':'liabilities','StockholdersEquity':'equity'}


def parse_sec_companyfacts(raw:bytes,*,issuer_id:str,as_of:str,statement:str='CFS'):
    validate_entity('US',issuer_id)
    cutoff=parse_date(as_of)
    obj=bounded_json(raw)
    if obj.get('cik')!=int(issuer_id):
        raise ValueError('SEC_CIK_MISMATCH')
    usgaap=obj.get('facts',{}).get('us-gaap',{})
    if type(usgaap) is not dict or not usgaap:
        raise ValueError('SEC_FACTS_MISSING')
    if statement not in ('CFS','OFS'):
        raise ValueError('STATEMENT_INVALID')
    result=[]; seen={}; source_sha=digest(raw)
    for tag,metric in TAGS.items():
        fact=usgaap.get(tag)
        if fact is None: continue
        if type(fact) is not dict: raise ValueError('SEC_FACT_INVALID')
        units=fact.get('units',{})
        if type(units) is not dict: raise ValueError('SEC_UNITS_INVALID')
        observations=units.get('USD',[])
        if type(observations) is not list or len(observations)>2000: raise ValueError('SEC_ROWS_INVALID')
        for e in observations:
            if type(e) is not dict: raise ValueError('SEC_ROW_INVALID')
            if e.get('form') not in ('10-K','10-K/A'): continue
            if e.get('fp')!='FY': continue
            filed=parse_date(e.get('filed'))
            end=parse_date(e.get('end'))
            if filed>cutoff: continue
            if metric in ('revenue','net_income','operating_cashflow') and not e.get('start'):
                raise ValueError('SEC_ANNUAL_FLOW_START_MISSING')
            if e.get('start'):
                start=parse_date(e['start'])
                if not (350 <= (end-start).days <= 380):
                    continue  # Annual flow only; balance-sheet concepts have no start
            accession=e.get('accn')
            if type(accession) is not str or not accession or len(accession)>50: raise ValueError('SEC_ACCESSION_INVALID')
            obs=observation(country='US',issuer_id=issuer_id,metric=metric,fiscal_end=end.isoformat(),
                available_at=filed.isoformat(),value=e.get('val'),unit='USD',statement=statement,
                source_ref='SEC:'+accession,source_sha256=source_sha)
            key=(metric,obs.fiscal_end)
            previous=seen.get(key)
            if previous is not None:
                if previous.value != obs.value:
                    raise ValueError('SEC_CONFLICTING_FILING_OR_AMENDMENT')
                # duplicate cross filing requires conservative same figure; keep older evidence
                continue
            seen[key]=obs;result.append(obs)
    if not result:
        raise ValueError('SEC_NO_ELIGIBLE_ANNUAL_FACTS')
    return result
