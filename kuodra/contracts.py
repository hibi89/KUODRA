"""Conservative offline-only source observations. No network, no model, no orders."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re

METRICS = frozenset({'revenue','net_income','operating_cashflow','receivables','inventory','liabilities','equity'})
MAX_BYTES = 1_000_000
D = Decimal
_ID_US = re.compile(r'^\d{10}$')
_ID_KR = re.compile(r'^\d{8}$')
_DIGITS = re.compile(r'^-?(0|[1-9]\d{0,17})$')


def parse_date(s: str) -> date:
    if type(s) is not str or len(s) != 10 or not re.fullmatch(r'\d{4}-\d\d-\d\d',s):
        raise ValueError('INVALID_DATE')
    try:
        d = date.fromisoformat(s)
    except ValueError as e:
        raise ValueError('INVALID_DATE') from e
    if d.isoformat()!=s:
        raise ValueError('INVALID_DATE')
    return d


def parse_amount(value: object) -> Decimal:
    if isinstance(value,bool) or type(value) not in (int,str):
        raise ValueError('INVALID_AMOUNT')
    s=str(value)
    if not _DIGITS.fullmatch(s) or s == '-0':
        raise ValueError('INVALID_AMOUNT')
    try:
        v=D(s)
    except InvalidOperation as e:
        raise ValueError('INVALID_AMOUNT') from e
    if abs(v)>D('999999999999999999'):
        raise ValueError('AMOUNT_LIMIT')
    return v


def bounded_json(raw: bytes, *, max_bytes:int=MAX_BYTES) -> dict:
    if type(max_bytes) is not int or not 1<=max_bytes<=10_000_000:
        raise ValueError('SOURCE_LIMIT_INVALID')
    if type(raw) is not bytes or not 0<len(raw)<=max_bytes:
        raise ValueError('SOURCE_SIZE_INVALID')
    def no_duplicate(pairs):
        result={}
        for key,val in pairs:
            if key in result:
                raise ValueError('DUPLICATE_JSON_KEY')
            result[key]=val
        return result
    try:
        obj=json.loads(raw.decode('utf-8','strict'),object_pairs_hook=no_duplicate)
    except (UnicodeError, ValueError) as e:
        raise ValueError('SOURCE_JSON_INVALID') from e
    if type(obj) is not dict:
        raise ValueError('SOURCE_JSON_OBJECT_REQUIRED')
    return obj


def validate_entity(country:str,issuer_id:str)->None:
    if country not in ('KR','US') or type(issuer_id) is not str:
        raise ValueError('COUNTRY_ID_INVALID')
    pattern=_ID_KR if country=='KR' else _ID_US
    if not pattern.fullmatch(issuer_id):
        raise ValueError('COUNTRY_ID_INVALID')


@dataclass(frozen=True)
class Observation:
    country:str
    issuer_id:str
    metric:str
    fiscal_end:str
    available_at:str
    value:Decimal
    unit:str
    statement:str
    source_ref:str
    source_sha256:str

    def as_json(self):
        d=asdict(self)
        d['value']=str(d['value'])
        return d


def observation(*, country,issuer_id,metric,fiscal_end,available_at,value,unit,statement,source_ref,source_sha256)->Observation:
    validate_entity(country,issuer_id)
    if metric not in METRICS:
        raise ValueError('METRIC_UNSUPPORTED')
    period=parse_date(fiscal_end)
    released=parse_date(available_at)
    if released<period:
        raise ValueError('RELEASE_BEFORE_PERIOD')
    if unit not in ('KRW','USD') or unit != ('KRW' if country=='KR' else 'USD'):
        raise ValueError('CURRENCY_MISMATCH')
    if statement not in ('CFS','OFS'):
        raise ValueError('STATEMENT_INVALID')
    if (type(source_ref) is not str or not 4<=len(source_ref)<=100
        or re.search(r'[\x00-\x1f<>]',source_ref)
        or type(source_sha256) is not str or not re.fullmatch('[0-9a-f]{64}',source_sha256)):
        raise ValueError('SOURCE_EVIDENCE_INVALID')
    return Observation(country,issuer_id,metric,period.isoformat(),released.isoformat(),parse_amount(value),unit,statement,source_ref,source_sha256)


def digest(raw:bytes)->str:
    return sha256(raw).hexdigest()
