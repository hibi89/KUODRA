"""Offline OpenDART annual financial-statement subset adapter. No API calls."""
from __future__ import annotations
import re
from kuodra.contracts import bounded_json, digest, observation,parse_date,validate_entity

ACCOUNTS={
'ifrs-full_Revenue':('revenue','IS'),
'ifrs-full_ProfitLoss':('net_income','IS'),
'ifrs-full_CashFlowsFromUsedInOperatingActivities':('operating_cashflow','CF'),
'ifrs-full_TradeAndOtherCurrentReceivables':('receivables','BS'),
'ifrs-full_Inventories':('inventory','BS'),
'ifrs-full_Liabilities':('liabilities','BS'),
'ifrs-full_Equity':('equity','BS'),
}

def parse_dart_annual(raw:bytes,*,issuer_id:str,as_of:str,statement:str='CFS'):
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
    seen={};out=[];src=digest(raw)
    for item in items:
        if type(item) is not dict:raise ValueError('DART_ROW_INVALID')
        if item.get('corp_code')!=issuer_id:raise ValueError('DART_CORP_MISMATCH')
        if item.get('reprt_code')!='11011' or item.get('fs_div')!=statement:continue
        aid=item.get('account_id')
        if aid not in ACCOUNTS:continue
        metric,sj=ACCOUNTS[aid]
        if item.get('sj_div')!=sj:raise ValueError('DART_STATEMENT_SECTION_MISMATCH')
        year=item.get('bsns_year')
        if type(year) is not str or not re.fullmatch(r'20\d{2}',year):raise ValueError('DART_YEAR_INVALID')
        end=parse_date(year+'-12-31')
        receipt=item.get('rcept_no')
        if type(receipt) is not str or not re.fullmatch(r'20\d{12}',receipt):raise ValueError('DART_RECEIPT_INVALID')
        available=parse_date(receipt[:4]+'-'+receipt[4:6]+'-'+receipt[6:8])
        if available>cutoff:continue
        val=item.get('thstrm_amount')
        if type(val) is not str or not re.fullmatch(r'-?(0|[1-9]\d{0,17})',val.replace(',','')):
            raise ValueError('DART_AMOUNT_INVALID')
        obs=observation(country='KR',issuer_id=issuer_id,metric=metric,
            fiscal_end=end.isoformat(),available_at=available.isoformat(),value=val.replace(',',''),
            unit='KRW',statement=statement,source_ref='DART:'+receipt,source_sha256=src)
        key=(metric,obs.fiscal_end)
        if key in seen:
            if seen[key].value!=obs.value:raise ValueError('DART_CONFLICTING_FILINGS')
            continue
        seen[key]=obs;out.append(obs)
    if not out:raise ValueError('DART_NO_ELIGIBLE_ANNUAL_FACTS')
    return out
