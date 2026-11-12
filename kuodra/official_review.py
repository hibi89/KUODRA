"""One explicit, rights-gated official-source request to the existing local pipeline.

No default network operation, background updates, disk cache, private document
upload, data resale, publisher attestation or commercial-use authorization.
The provider gateway is allowlisted, single-shot and fail-closed.

DART credentials MUST come from the caller's local runtime, never be logged,
serialized, shown in reports, or checked into GitHub.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Callable

from kuodra.cli import analyze_bytes
from kuodra.contracts import parse_date, validate_entity
from kuodra.source_client import (
    build_dart_request, build_sec_request, fetch_once,
)


def analyze_opted_in_once(
    *,
    country: str,
    issuer_id: str,
    as_of: str,
    owner_consent: bool,
    statement: str = 'CFS',
    sec_user_agent: str | None = None,
    dart_api_key: str | None = None,
    dart_business_year: str | None = None,
    transport: Callable | None = None,
) -> dict:
    if owner_consent is not True:
        raise ValueError('OFFICIAL_SOURCE_EXPLICIT_OWNER_CONSENT_REQUIRED')
    validate_entity(country, issuer_id)
    parse_date(as_of)
    if country == 'US':
        if dart_api_key is not None or dart_business_year is not None:
            raise ValueError('OFFICIAL_US_UNEXPECTED_DART_CREDENTIALS')
        request = build_sec_request(
            issuer_id, user_agent=sec_user_agent, opt_in=True)
        provider = 'SEC'
    else:
        if sec_user_agent is not None:
            raise ValueError('OFFICIAL_KR_UNEXPECTED_SEC_CONTACT')
        request = build_dart_request(
            issuer_id, year=dart_business_year, api_key=dart_api_key,
            opt_in=True, statement=statement)
        provider = 'DART'
    # fetch_once verifies HTTPS allowlist, route, GET, content type and basic
    # issuer/status. No retry of 403/429 and no redirects or data forwarding.
    kwargs = {'provider': provider, 'opt_in': True}
    if transport is not None:
        kwargs['transport'] = transport
    result = fetch_once(request, **kwargs)
    report = analyze_bytes(
        result.content, country=country, issuer_id=issuer_id,
        as_of=as_of, statement=statement,
    )
    # Never include raw private source bytes, DART query string or API key.
    if country == 'KR' and '?' in result.source_url:
        raise ValueError('OFFICIAL_PROVIDER_URL_CREDENTIAL_LEAK_DENIED')
    report['official_source_request'] = {
        'provider': provider,
        'fixed_url_no_credential': result.source_url,
        'input_sha256': sha256(result.content).hexdigest(),
        'source_publisher_authenticated': False,
        'commercial_rights_verified': False,
        'provider_response_parsed': True,
        'requested_by_owner': True,
        'automatic_retry_count': 0,
    }
    report['source_verified'] = False
    report['rights_verified'] = False
    report['guard'] = 'HOLD'
    report['warnings'].append(
        'An official endpoint response was parsed after owner opt-in; '
        'TLS endpoint reachability, issuer identity and content rights '
        'are not independent proof of authenticity or redistribution permission.')
    return report
