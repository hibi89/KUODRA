"""Offline SEC CompanyFacts financial facts with as-of revision reconciliation.

SEC API data *shape* is not proof of a genuine publisher download or data rights.
Only supported USD US-GAAP annual facts are accepted. No network calls.
"""
from __future__ import annotations
import re
from kuodra.contracts import bounded_json, digest, observation, parse_date, validate_entity
from kuodra.revisions import reconcile_annual_facts

TAGS={
    'Revenues':'revenue',
    'RevenueFromContractWithCustomerExcludingAssessedTax':'revenue',
    'NetIncomeLoss':'net_income',
    'NetCashProvidedByUsedInOperatingActivities':'operating_cashflow',
    'AccountsNotesAndOtherReceivablesNetCurrent':'receivables',
    'InventoryNet':'inventory',
    'Liabilities':'liabilities',
    'StockholdersEquity':'equity',
}
_FLOW={'revenue','net_income','operating_cashflow'}
_ACC=re.compile(r'\d{10}-\d{2}-\d{6}\Z', re.ASCII)


def parse_sec_companyfacts(raw: bytes, *, issuer_id: str, as_of: str,
                           statement: str = 'CFS', with_audit: bool = False):
    validate_entity('US', issuer_id)
    cutoff=parse_date(as_of)
    obj=bounded_json(raw,max_bytes=10_000_000)
    if type(obj.get('cik')) is not int or obj['cik'] != int(issuer_id):
        raise ValueError('SEC_CIK_MISMATCH')
    if statement not in ('CFS','OFS'):
        raise ValueError('STATEMENT_INVALID')
    # CompanyFacts is per issuer and generally does not reliably label CFS/OFS.
    # Its use in OFS must not masquerade as verified unconsolidated statements.
    if statement == 'OFS':
        raise ValueError('SEC_OFS_NOT_VERIFIABLE_FROM_COMPANYFACTS')
    facts=obj.get('facts')
    if type(facts) is not dict:
        raise ValueError('SEC_FACTS_MISSING')
    usgaap=facts.get('us-gaap')
    if type(usgaap) is not dict or not usgaap:
        raise ValueError('SEC_FACTS_MISSING')
    candidates=[]; src=digest(raw)
    for tag,metric in TAGS.items():
        fact=usgaap.get(tag)
        if fact is None:
            continue
        if type(fact) is not dict or type(fact.get('units')) is not dict:
            raise ValueError('SEC_FACT_OR_UNITS_INVALID')
        u=fact['units']
        # Units other than USD must never be interpreted as US dollars.
        if 'USD' not in u:
            continue
        entries=u['USD']
        if type(entries) is not list or len(entries)>2000:
            raise ValueError('SEC_ROWS_INVALID')
        for row in entries:
            if type(row) is not dict:
                raise ValueError('SEC_ROW_INVALID')
            if row.get('form') not in ('10-K','10-K/A') or row.get('fp')!='FY':
                continue
            released=parse_date(row.get('filed'))
            end=parse_date(row.get('end'))
            if released > cutoff:
                continue
            if metric in _FLOW:
                if not row.get('start'):
                    raise ValueError('SEC_ANNUAL_FLOW_START_MISSING')
                start=parse_date(row['start'])
                if not 350 <= (end-start).days <= 380:
                    continue
            elif row.get('start') is not None:
                # An instantaneous balance-sheet fact cannot be a duration.
                raise ValueError('SEC_STOCK_FACT_HAS_DURATION')
            accession=row.get('accn')
            if type(accession) is not str or not _ACC.fullmatch(accession):
                raise ValueError('SEC_ACCESSION_INVALID')
            candidates.append(observation(
                country='US', issuer_id=issuer_id, metric=metric,
                fiscal_end=end.isoformat(), available_at=released.isoformat(),
                value=row.get('val'), unit='USD', statement='CFS',
                source_ref='SEC:'+accession, source_sha256=src,
            ))
    if not candidates:
        raise ValueError('SEC_NO_ELIGIBLE_ANNUAL_FACTS')
    selected,audit=reconcile_annual_facts(candidates,as_of=as_of)
    return (selected,audit) if with_audit else selected
