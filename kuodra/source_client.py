"""Explicit opt-in official SEC/OpenDART fetch gateway, inactive by default.

No background polling, caching to disk, retries or 403/429 bypass. Credentials
are caller-supplied and not returned or logged. Not a license/rights verifier.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable
from urllib.parse import urlencode,parse_qs
import re
import urllib.request
import urllib.error
from kuodra.contracts import validate_entity

_SEC_HOST='data.sec.gov'
_DART_HOST='opendart.fss.or.kr'
_SEC_UA=re.compile(r'KUODRA/1\.0 \([^()\r\n]{8,120}\)\Z')
_DART_KEY=re.compile(r'[0-9a-fA-F]{40}\Z')
_YEAR=re.compile(r'20\d{2}\Z')


@dataclass(frozen=True)
class SourceResult:
    provider: str
    content: bytes
    content_type: str
    source_url: str  # SEC URL only; DART URL excludes key.
    publisher_authenticated: bool  # no TLS-independent publisher attestation
    commercial_rights_verified: bool


def build_sec_request(cik: str, *, user_agent: str, opt_in: bool) -> urllib.request.Request:
    validate_entity('US',cik)
    if opt_in is not True or type(user_agent) is not str or not _SEC_UA.fullmatch(user_agent):
        raise ValueError('SEC_EXPLICIT_CONSENT_AND_IDENTIFIABLE_AGENT_REQUIRED')
    return urllib.request.Request(
        f'https://{_SEC_HOST}/api/xbrl/companyfacts/CIK{cik}.json',
        headers={'User-Agent':user_agent,'Accept':'application/json'},method='GET')


def build_dart_request(corp_code:str, *, year:str, api_key:str, opt_in:bool,
                       statement:str='CFS') -> urllib.request.Request:
    validate_entity('KR',corp_code)
    if (opt_in is not True or type(year) is not str or not _YEAR.fullmatch(year)
            or type(api_key) is not str or not _DART_KEY.fullmatch(api_key)
            or statement not in ('CFS','OFS')):
        raise ValueError('DART_EXPLICIT_CONSENT_KEY_AND_SCOPE_REQUIRED')
    q=urlencode({'crtfc_key':api_key,'corp_code':corp_code,'bsns_year':year,
                 'reprt_code':'11011','fs_div':statement})
    return urllib.request.Request(f'https://{_DART_HOST}/api/fnlttSinglAcntAll.json?{q}',
                                  headers={'Accept':'application/json'},method='GET')


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise ValueError('PROVIDER_REDIRECT_DENIED')


def _transport(req: urllib.request.Request, timeout:float):
    # Explicitly reject automatic redirects; no auth or data forwarded elsewhere.
    with urllib.request.build_opener(_NoRedirect()).open(req,timeout=timeout) as resp:
        length=resp.headers.get('Content-Length')
        if length and int(length)>10_000_000:
            raise ValueError('PROVIDER_SOURCE_TOO_LARGE')
        ct=resp.headers.get('Content-Type','')
        if 'json' not in ct.lower():
            raise ValueError('PROVIDER_RESPONSE_NOT_JSON')
        data=resp.read(10_000_001)
        if not data or len(data)>10_000_000:
            raise ValueError('PROVIDER_SOURCE_TOO_LARGE')
        return data,ct


def fetch_once(req:urllib.request.Request, *,provider:str,opt_in:bool,
               transport:Callable|None=None,timeout:float=8.0) -> SourceResult:
    if opt_in is not True or provider not in ('SEC','DART') or not 1.0<=timeout<=10.0:
        raise ValueError('PROVIDER_REQUEST_UNAUTHORIZED')
    if type(req) is not urllib.request.Request or req.get_method()!='GET':
        raise ValueError('PROVIDER_REQUEST_SHAPE_DENIED')
    from urllib.parse import urlsplit
    url=urlsplit(req.full_url)
    host=_SEC_HOST if provider=='SEC' else _DART_HOST
    if url.scheme!='https' or url.hostname!=host or url.port not in (None,443) or url.username or url.password:
        raise ValueError('PROVIDER_HOST_DENIED')
    if provider=='SEC':
        if (url.query or not re.fullmatch(r'/api/xbrl/companyfacts/CIK\d{10}\.json',url.path)
                or not _SEC_UA.fullmatch(req.get_header('User-agent') or '')):
            raise ValueError('SEC_ROUTE_OR_AGENT_DENIED')
    if provider=='DART':
        if url.path!='/api/fnlttSinglAcntAll.json':
            raise ValueError('DART_ROUTE_DENIED')
        try:
            params=parse_qs(url.query,keep_blank_values=True,strict_parsing=True)
        except ValueError:
            raise ValueError('DART_REQUEST_SCOPE_DENIED') from None
        if (set(params)!={'crtfc_key','corp_code','bsns_year','reprt_code','fs_div'}
                or any(len(v)!=1 for v in params.values())
                or not _DART_KEY.fullmatch(params['crtfc_key'][0])
                or not _YEAR.fullmatch(params['bsns_year'][0])
                or not re.fullmatch(r'\d{8}',params['corp_code'][0])
                or params['reprt_code']!=['11011']
                or params['fs_div'][0] not in ('CFS','OFS')):
            raise ValueError('DART_REQUEST_SCOPE_DENIED')
    transport=_transport if transport is None else transport
    try:
        data,ct=transport(req,timeout)
    except urllib.error.HTTPError as e:
        if e.code==403: raise ValueError('PROVIDER_FORBIDDEN_NO_BYPASS') from None
        if e.code==429: raise ValueError('PROVIDER_RATE_LIMIT_NO_RETRY') from None
        raise ValueError('PROVIDER_HTTP_ERROR') from None
    except (urllib.error.URLError,TimeoutError,OSError):
        raise ValueError('PROVIDER_NETWORK_UNAVAILABLE') from None
    if type(data) is not bytes or not 0<len(data)<=10_000_000 or type(ct) is not str or 'json' not in ct.lower():
        raise ValueError('PROVIDER_RESPONSE_INVALID')
    try:
        payload=json.loads(data)
    except (ValueError, UnicodeError):
        raise ValueError('PROVIDER_JSON_INVALID') from None
    if type(payload) is not dict:
        raise ValueError('PROVIDER_JSON_OBJECT_REQUIRED')
    if provider=='DART' and payload.get('status')!='000':
        # An HTTP 200 from OpenDART can contain an application-level error.
        # Do not silently expose it as a verified financial data response.
        raise ValueError('DART_APPLICATION_STATUS_NOT_SUCCESS')
    if provider=='SEC' and (type(payload.get('facts')) is not dict
                            or type(payload.get('cik')) is not int
                            or str(payload['cik']).zfill(10)!=url.path[-15:-5]):
        raise ValueError('SEC_COMPANYFACTS_SCOPE_OR_PAYLOAD_INVALID')
    return SourceResult(provider=provider,content=data,content_type=ct,
                        source_url=(req.full_url if provider=='SEC' else f'https://{_DART_HOST}/api/fnlttSinglAcntAll.json'),
                        publisher_authenticated=False,commercial_rights_verified=False)
