"""Human-triggered offline CLI. No network or trading actions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from kuodra.markets.us.sec_local import parse_sec_companyfacts
from kuodra.markets.kr.dart_local import parse_dart_annual
from kuodra.review import build_review
from kuodra.report import export_local


def analyze_bytes(raw:bytes,*,country:str,issuer_id:str,as_of:str,statement:str='CFS'):
    adapter={'US':parse_sec_companyfacts,'KR':parse_dart_annual}.get(country)
    if adapter is None:raise ValueError('COUNTRY_UNSUPPORTED')
    return build_review(adapter(raw,issuer_id=issuer_id,as_of=as_of,statement=statement),as_of=as_of)


def main(argv=None):
    p=argparse.ArgumentParser(description='KUODRA offline company financial evidence verifier (no live requests)')
    p.add_argument('--country',choices=['KR','US'],required=True)
    p.add_argument('--issuer-id',required=True,help='DART 8-digit corp_code or SEC 10-digit CIK')
    p.add_argument('--as-of',required=True,help='YYYY-MM-DD')
    p.add_argument('--source',type=Path,required=True,help='lawfully held local JSON file')
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--name',default='review')
    p.add_argument('--statement',choices=['CFS','OFS'],default='CFS')
    args=p.parse_args(argv)
    if args.source.is_symlink() or not args.source.is_file() or args.source.stat().st_size>1_000_000:
        p.error('SOURCE_FILE_INVALID')
    try:
        report=analyze_bytes(args.source.read_bytes(),country=args.country,issuer_id=args.issuer_id,as_of=args.as_of,statement=args.statement)
        r=export_local(report,args.output_dir,args.name)
    except (ValueError,KeyError,OSError) as exc:
        p.error(str(exc))
    print(json.dumps({'guard':report['guard'],'artifacts':r},ensure_ascii=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
