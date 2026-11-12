"""KUODRA Windows local desktop entrypoint.

PyInstaller onedir staging only; this is not a signed/sale-ready installer.
Self-test never creates a Tk window and never starts an external service.
"""
from __future__ import annotations
import argparse
import json
import sys


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ['--self-test']:
        from kuodra.contracts import parse_date
        from kuodra.release_gate import verify_evidence_bundle
        from kuodra.heldout import evaluate_synthetic_heldout
        from kuodra.official_cli import main as official_review_cli
        assert parse_date('2025-11-13').isoformat() == '2025-11-13'
        assert (callable(verify_evidence_bundle) and callable(evaluate_synthetic_heldout)
                and callable(official_review_cli))
        print(json.dumps({'schema': 'kuodra.desktop-self-test.v1',
                          'status': 'STAGED_OFFLINE_ONLY', 'network_requests': 0,
                          'trade_executed': False, 'consumer_release_ready': False},sort_keys=True))
        return 0
    if args == ['--gui-smoke']:
        # Real, short-lived Tk initialization on the Windows runner;
        # it never selects a source, calls the provider or exports.
        from kuodra.gui import main as gui_main
        print(json.dumps(gui_main(smoke_only=True),sort_keys=True))
        return 0
    if args[:1] == ['--verify-export']:
        if len(args) not in (2, 3):
            raise SystemExit('Usage: --verify-export <directory> [stem]')
        from kuodra.release_gate import verify_evidence_bundle
        result = verify_evidence_bundle(args[1], args[2] if len(args) == 3 else 'review',
                                        require_pdf=False)
        print(json.dumps(result, sort_keys=True))
        return 0
    if args[:1] == ['--official-review']:
        # External provider access is still impossible without --consent and
        # a valid owner-supplied contact/API key in the environment.
        from kuodra.official_cli import main as official_main
        return official_main(args[1:])
    if args[:1] == ['--offline-review']:
        from kuodra.cli import main as cli_main
        return cli_main(args[1:])
    if args:
        raise SystemExit('Use --self-test, --verify-export <dir> [stem], --offline-review <args>, --official-review <args> with explicit consent, or launch local-only GUI without args')
    from kuodra.gui import main as gui_main
    gui_main()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
