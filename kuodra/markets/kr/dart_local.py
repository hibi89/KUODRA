"""Offline OpenDART full annual financial statement subset, explicit period.

Never assume fiscal year ends Dec 31. Only actual thstrm_dt date spans are
accepted and original rcept_no is retained; file source isn't authenticated.
"""
from __future__ import annotations
import re
from kuodra.contracts import bounded_json,digest,observation,parse_date,validate_entity
from kuodra.revisions import reconcile_annual_facts

ACCOUNTS={
'ifrs-full_Revenue':('revenue','IS'),
'ifrs-full_ProfitLoss':('net_income','IS'),
'ifrs-full_CashFlowsFromUsedInOperatingActivities':('operating_cashflow','CF'),
'ifrs-full_TradeAndOtherCurrentReceivables':('receivables','BS'),
'ifrs-full_Inventories':('inventory','BS'),
'ifrs-full_Liabilities':('liabilities','BS'),
'ifrs-full_Equity':('equity','BS'),
}
_DATE_TOKEN=re.compile(r'(?:19|20)\d{2}[.-]\d{2}[.-]\d{2}')
_FULL_PERIOD=re.compile(r'(?:19|20)\d{2}[.-]\d{2}[.-]\d{2}(?: *~ *(?:19|20)\d{2}[.-]\d{2}[.-]\d{2})?\Z',re.ASCII)
_RECEIPT=re.compile(r'20\d{12}\Z',re.ASCII)
_YEAR=re.compile(r'20\d{2}\Z',re.ASCII)
_NUMBER=re.compile(r'-?(?:0|[1-9]\d{0,17}|[1-9]\d{0,2}(?:,\d{3}){1,5})\Z',re.ASCII)


def _date_from_period(text: str, *, year: str):
    if type(text) is not str or not 10 <= len(text) <= 90:
        raise ValueError('DART_FISCAL_PERIOD_MISSING')
    if not _FULL_PERIOD.fullmatch(text.strip()):
        raise ValueError('DART_FISCAL_PERIOD_INVALID')
    tokens=_DATE_TOKEN.findall(text)
    if len(tokens) not in (1,2) or len(text.strip()) > 90:
        raise ValueError('DART_FISCAL_PERIOD_INVALID')
    dates=[parse_date(x.replace('.','-')) for x in tokens]
    if len(dates)==2 and not 350 <= (dates[1]-dates[0]).days <= 380:
        raise ValueError('DART_FISCAL_SPAN_INVALID')
    if dates[-1].year!=int(year):
        raise ValueError('DART_FISCAL_YEAR_MISMATCH')
    return dates[-1]


def parse_dart_annual(raw:bytes,*,issuer_id:str,as_of:str,statement:str='CFS',
                      with_audit:bool=False,
                      fiscal_end_override:str|None=None,
                      request_fs_div_bound:bool=False):
    """Parse annual financial facts without inventing fields absent from DART.

    Official fnlttSinglAcntAll rows do not provide fs_div or thstrm_dt.
    fs_div is a *request* parameter. Only callers who explicitly bound the
    request to CFS/OFS may accept absent response fs_div. Fiscal-end date must
    be separately supplied and crosschecked against business year; supplying
    this date is NOT issuer, audit, rights or publisher authentication.
    """
    validate_entity('KR',issuer_id)
    cutoff=parse_date(as_of)
    obj=bounded_json(raw)
    if obj.get('status')!='000':
        raise ValueError('DART_UNSUCCESSFUL')
    items=obj.get('list')
    if type(items) is not list or not 0<len(items)<=2000:
        raise ValueError('DART_ROWS_INVALID')
    if statement not in ('CFS','OFS'):
        raise ValueError('STATEMENT_INVALID')
    if type(request_fs_div_bound) is not bool:
        raise ValueError('DART_REQUEST_BOUND_FLAG_INVALID')
    if fiscal_end_override is not None:
        override_end=parse_date(fiscal_end_override)
    else:
        override_end=None
    candidates=[];src=digest(raw)
    for item in items:
        if type(item) is not dict:
            raise ValueError('DART_ROW_INVALID')
        if item.get('corp_code')!=issuer_id:
            raise ValueError('DART_CORP_MISMATCH')
        if item.get('reprt_code')!='11011':
            continue
        reported_scope=item.get('fs_div')
        if reported_scope is None:
            if not request_fs_div_bound:
                raise ValueError('DART_FS_DIV_REQUEST_SCOPE_NOT_BOUND')
        elif reported_scope!=statement:
            # A response row cannot silently override the request scope.
            if request_fs_div_bound:
                raise ValueError('DART_FS_DIV_REQUEST_RESPONSE_MISMATCH')
            continue
        aid=item.get('account_id')
        if aid not in ACCOUNTS:
            continue
        metric,section=ACCOUNTS[aid]
        if item.get('sj_div')!=section:
            raise ValueError('DART_STATEMENT_SECTION_MISMATCH')
        year=item.get('bsns_year')
        if type(year) is not str or not _YEAR.fullmatch(year):
            raise ValueError('DART_YEAR_INVALID')
        period_text=item.get('thstrm_dt')
        if period_text is None:
            if override_end is None:
                raise ValueError('DART_FISCAL_PERIOD_MISSING')
            if override_end.year!=int(year):
                raise ValueError('DART_FISCAL_YEAR_MISMATCH')
            end=override_end
        else:
            end=_date_from_period(period_text,year=year)
            if override_end is not None and end!=override_end:
                raise ValueError('DART_FISCAL_END_SOURCE_CONFLICT')
        receipt=item.get('rcept_no')
        if type(receipt) is not str or not _RECEIPT.fullmatch(receipt):
            raise ValueError('DART_RECEIPT_INVALID')
        available=parse_date(receipt[:4]+'-'+receipt[4:6]+'-'+receipt[6:8])
        if available>cutoff:
            continue
        if item.get('currency')!='KRW':
            raise ValueError('DART_CURRENCY_NOT_EXPLICIT_KRW')
        val=item.get('thstrm_amount')
        if val is None or val == '':
            # Official DART can return empty accounts. Missing is not zero.
            # Do not fabricate a value; omit only that unsupported observation.
            continue
        if type(val) is not str or not _NUMBER.fullmatch(val):
            raise ValueError('DART_AMOUNT_INVALID')
        candidates.append(observation(
            country='KR',issuer_id=issuer_id,metric=metric,
            fiscal_end=end.isoformat(),available_at=available.isoformat(),
            value=val.replace(',',''),unit='KRW',statement=statement,
            source_ref='DART:'+receipt,source_sha256=src,
        ))
    if not candidates:
        raise ValueError('DART_NO_ELIGIBLE_ANNUAL_FACTS')
    selected,audit=reconcile_annual_facts(candidates,as_of=as_of)
    return (selected,audit) if with_audit else selected
