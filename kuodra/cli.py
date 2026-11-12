"""Human-triggered offline CLI. No network or trading actions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from kuodra.markets.us.sec_local import parse_sec_companyfacts
from kuodra.markets.kr.dart_local import parse_dart_annual
from kuodra.review import build_review
from kuodra.report import export_local
from kuodra.kic_bridge import normalize_observations_via_kic
from kuodra.peers import compare_peers
from kuodra.market_a import evaluate_synthetic_market_a
from kuodra.contracts import bounded_json
from kuodra.exploration import explore_local_cross_section
from kuodra.heldout import evaluate_synthetic_heldout
from kuodra.release_gate import verify_evidence_bundle


def analyze_bytes(raw:bytes,*,country:str,issuer_id:str,as_of:str,statement:str='CFS',
                  peer_inputs:tuple[tuple[bytes,str],...]=(),
                  synthetic_sector_code:str|None=None,
                  synthetic_market_raw:bytes|None=None,
                  owner_stats_raw:bytes|None=None,stats_metrics:tuple[str,...]=(),
                  stats_observation_at:str|None=None,stats_owner_consent:bool=False,
                  synthetic_heldout_raw:bytes|None=None,heldout_owner_consent:bool=False):
    adapter={'US':parse_sec_companyfacts,'KR':parse_dart_annual}.get(country)
    if adapter is None:raise ValueError('COUNTRY_UNSUPPORTED')
    rows, revision_audit = adapter(raw,issuer_id=issuer_id,as_of=as_of,statement=statement,with_audit=True)
    # KIC canonical validation is mandatory before a report is exported.
    # Nothing from the PRIVATE canonical raw rowset is copied to report output.
    canonical = normalize_observations_via_kic(rows,as_of=as_of)
    report = build_review(rows,as_of=as_of)
    report['revision_audit'] = revision_audit
    report['fiscal_reconciliation'] = {
        'period_source': 'official filing-shaped fiscal date fields, not inferred Dec 31' if country == 'KR' else 'SEC period end + annual duration',
        'revisions_considered': sum(a['candidate_count']-1 for a in revision_audit),
        'revisions_changing_values': sum(bool(a['revised_amount']) for a in revision_audit),
        'publisher_authenticated': False,
        'rights_verified': False,
    }
    if type(peer_inputs) is not tuple or len(peer_inputs)>10:
        raise ValueError('PEER_INPUTS_INVALID')
    if peer_inputs:
        peer_reports=[]
        ids=[issuer_id]
        for peer in peer_inputs:
            if (type(peer) is not tuple or len(peer)!=2 or
                    type(peer[0]) is not bytes or type(peer[1]) is not str):
                raise ValueError('PEER_INPUT_INVALID')
            peer_rows=adapter(peer[0],issuer_id=peer[1],as_of=as_of,statement=statement)
            normalize_observations_via_kic(peer_rows,as_of=as_of)
            peer_reports.append(build_review(peer_rows,as_of=as_of))
            ids.append(peer[1])
        sector=None
        if synthetic_sector_code is not None:
            sector={'code':synthetic_sector_code,'issuers':ids,'origin':'SYNTHETIC_TEST_ONLY'}
        cohort=compare_peers(report,peer_reports,synthetic_sector=sector)
        report['peer_comparison']=cohort
        report['engine_c']=cohort['status']
        report['warnings'].append('Peer comparison is descriptive and does not verify real industry comparability.')
    elif synthetic_sector_code is not None:
        raise ValueError('SECTOR_WITHOUT_PEERS')
    if synthetic_market_raw is not None:
        obj=bounded_json(synthetic_market_raw)
        if set(obj)!={'mode','stock','benchmark'} or obj.get('mode')!='SYNTHETIC_TEST_ONLY':
            raise ValueError('MARKET_SYNTHETIC_MODE_REQUIRED')
        market=evaluate_synthetic_market_a(obj['stock'],obj['benchmark'])
        report['synthetic_market_a']=market
        report['engine_a']=market['status']
        report['warnings'].append('Engine A is synthetic mathematical demonstration only; no licensed stock/index data.')
    if owner_stats_raw is not None:
        if stats_observation_at is None:
            raise ValueError('STATS_OBSERVATION_REQUIRED')
        exploration=explore_local_cross_section(
            owner_stats_raw,metrics=stats_metrics,observation_at=stats_observation_at,
            as_of=as_of,owner_consent=stats_owner_consent)
        report['exploratory_statistics']=exploration
        if exploration['status']=='EXPLORATORY_INDEPENDENCE_UNVERIFIED':
            report['ml']='EXPLORATORY_STATS_HOLD_NO_PREDICTION'
        report['warnings'].append('Exploratory local statistics cannot verify investment causality or returns.')
    if synthetic_heldout_raw is not None:
        heldout = evaluate_synthetic_heldout(synthetic_heldout_raw,as_of=as_of,
                                             owner_consent=heldout_owner_consent)
        report['synthetic_heldout'] = heldout
        report['ml'] = ('SYNTHETIC_HOLDOUT_ONLY_NO_REAL_PREDICTION'
                        if heldout['status']=='EVALUATED_SYNTHETIC_ONLY'
                        else heldout['status'])
        report['warnings'].append('Synthetic split scores are NOT verified financial prediction or trading outcomes.')
    report['canonical_audit'] = {
        'schema': canonical['canonical']['schema'],
        'validated_rows': canonical['canonical']['rows'],
        'source_sha256': canonical['original_source_sha256'],
        'canonical_input_sha256': canonical['canonical_input_sha256'],
        'source_authenticated': False,
        'commercial_rights_verified': False,
        'private_data_exported': False,
        # Explicitly distinguish private raw material from derived statistics.
        # Owner-consented statistics may disclose non-raw aggregates in reports.
        'owner_private_statistics_in_report': owner_stats_raw is not None,
    }
    return report


def main(argv=None):
    p=argparse.ArgumentParser(description='KUODRA offline company financial evidence verifier (no live requests)')
    p.add_argument('--country',choices=['KR','US'],required=True)
    p.add_argument('--issuer-id',required=True,help='DART 8-digit corp_code or SEC 10-digit CIK')
    p.add_argument('--as-of',required=True,help='YYYY-MM-DD')
    p.add_argument('--source',type=Path,required=True,help='lawfully held local JSON file')
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--name',default='review')
    p.add_argument('--statement',choices=['CFS','OFS'],default='CFS')
    p.add_argument('--peer-source',type=Path,help='Optional lawful peer filing; no sector equivalence is assumed')
    p.add_argument('--peer-issuer-id',help='Official peer issuer ID, required with --peer-source')
    p.add_argument('--synthetic-sector-code',help='Explicit synthetic test code only; not industry authentication')
    p.add_argument('--synthetic-market-file',type=Path,help='Only synthetic price/index JSON; never real market data')
    p.add_argument('--stats-source',type=Path,help='Owner-owned canonical CSV; local only, no upload')
    p.add_argument('--stats-metrics',help='Comma separated predeclared metrics for BH-FDR')
    p.add_argument('--stats-observation',help='Observation date YYYY-MM-DD')
    p.add_argument('--stats-consent',action='store_true',help='I authorize local analysis of my owned CSV')
    p.add_argument('--synthetic-heldout-source',type=Path,help='Optional synthetic-only held-out dataset; local, never real-market forecast')
    p.add_argument('--heldout-consent',action='store_true',help='I authorize local synthetic-only heldout evaluation')
    p.add_argument('--pdf',action='store_true',help='Optional printable PDF (requires ReportLab); no Unicode font bundled')
    args=p.parse_args(argv)
    if bool(args.peer_source) != bool(args.peer_issuer_id):
        p.error('PEER_SOURCE_AND_ID_REQUIRED_TOGETHER')
    if args.source.is_symlink() or not args.source.is_file() or args.source.stat().st_size>1_000_000:
        p.error('SOURCE_FILE_INVALID')
    try:
        def safe_read(path):
            if path is None:return None
            if path.is_symlink() or not path.is_file() or path.stat().st_size>1_000_000:
                raise ValueError('OPTIONAL_SOURCE_FILE_INVALID')
            return path.read_bytes()
        peers=((safe_read(args.peer_source),args.peer_issuer_id),) if args.peer_source else ()
        market=safe_read(args.synthetic_market_file)
        stats=safe_read(args.stats_source)
        heldout=safe_read(args.synthetic_heldout_source)
        metrics=tuple(args.stats_metrics.split(',')) if args.stats_metrics else ()
        report=analyze_bytes(args.source.read_bytes(),country=args.country,issuer_id=args.issuer_id,as_of=args.as_of,statement=args.statement,peer_inputs=peers,synthetic_sector_code=args.synthetic_sector_code,synthetic_market_raw=market,owner_stats_raw=stats,stats_metrics=metrics,stats_observation_at=args.stats_observation,stats_owner_consent=args.stats_consent,synthetic_heldout_raw=heldout,heldout_owner_consent=args.heldout_consent)
        r=export_local(report,args.output_dir,args.name,pdf=args.pdf)
        integrity=verify_evidence_bundle(args.output_dir,args.name,require_pdf=args.pdf)
        for kind,details in r.items():
            if details['sha256'] != integrity['file_hashes'][kind]:
                raise ValueError('OUTPUT_SHA_INTEGRITY_MISMATCH')
    except (ValueError,KeyError,OSError) as exc:
        p.error(str(exc))
    print(json.dumps({'guard':report['guard'],'artifacts':r},ensure_ascii=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
