"""Manual, single-shot SEC/OpenDART fetch and local HOLD report.

No automatic collection, background work, data licensing approval or sale.
Network is OFF until --consent is explicitly supplied and one of the
KUODRA_SEC_USER_AGENT / KUODRA_DART_API_KEY local environment variables is set.
Never print these values, include them in output or place them in Git.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path

from kuodra.official_review import analyze_opted_in_once
from kuodra.report import export_local
from kuodra.release_gate import verify_evidence_bundle


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(
        description='Single explicitly-authorized official source review (Guard HOLD)')
    parser.add_argument('--country',choices=('KR','US'),required=True)
    parser.add_argument('--issuer-id',required=True)
    parser.add_argument('--as-of',required=True)
    parser.add_argument('--statement',choices=('CFS','OFS'),default='CFS')
    parser.add_argument('--business-year',help='DART annual year, only for KR')
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--name',default='official_review')
    parser.add_argument('--pdf',action='store_true')
    parser.add_argument('--consent',action='store_true',
        help='I authorize exactly one request to SEC or DART using my own credentials/contact')
    args=parser.parse_args(argv)
    if not args.consent:
        parser.error('OFFICIAL_SOURCE_EXPLICIT_OWNER_CONSENT_REQUIRED')
    if args.country=='US' and args.business_year is not None:
        parser.error('SEC_DOES_NOT_USE_DART_BUSINESS_YEAR')
    if args.country=='KR' and not args.business_year:
        parser.error('DART_BUSINESS_YEAR_REQUIRED')
    try:
        # Env credentials are read only after owner consent. No values printed.
        report=analyze_opted_in_once(
            country=args.country,issuer_id=args.issuer_id,as_of=args.as_of,
            owner_consent=True,statement=args.statement,
            sec_user_agent=(os.environ.get('KUODRA_SEC_USER_AGENT')
                            if args.country=='US' else None),
            dart_api_key=(os.environ.get('KUODRA_DART_API_KEY')
                          if args.country=='KR' else None),
            dart_business_year=args.business_year if args.country=='KR' else None,
        )
        saved=export_local(report,args.output_dir,args.name,pdf=args.pdf)
        checked=verify_evidence_bundle(args.output_dir,args.name,require_pdf=args.pdf)
        if any(item['sha256']!=checked['file_hashes'].get(ext)
               for ext,item in saved.items()):
            raise ValueError('OFFICIAL_EXPORT_INTEGRITY_MISMATCH')
    except (ValueError,OSError,KeyError) as exc:
        # The source gateway error vocabulary is intentionally credential-free.
        parser.error(type(exc).__name__ + ': ' + str(exc)[:120])
    print(json.dumps({
        'guard':'HOLD','source_publisher_authenticated':False,
        'commercial_rights_verified':False,
        'report_status':checked['status'],
        'input_sha256':report['official_source_request']['input_sha256'],
        'output_sha256':checked['file_hashes'],
        'network_requests':1,
        'automatic_retries':0,
    },sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
