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
        assert parse_date('2025-11-13').isoformat() == '2025-11-13'
        assert callable(verify_evidence_bundle) and callable(evaluate_synthetic_heldout)
        print(json.dumps({'schema': 'kuodra.desktop-self-test.v1',
                          'status': 'STAGED_OFFLINE_ONLY', 'network_requests': 0,
                          'trade_executed': False, 'consumer_release_ready': False},sort_keys=True))
        return 0
    if args[:1] == ['--verify-export']:
        if len(args) not in (2, 3):
            raise SystemExit('Usage: --verify-export <directory> [stem]')
        from kuodra.release_gate import verify_evidence_bundle
        result = verify_evidence_bundle(args[1], args[2] if len(args) == 3 else 'review',
                                        require_pdf=False)
        print(json.dumps(result, sort_keys=True))
        return 0
    if args[:1] == ['--offline-review']:
        from kuodra.cli import main as cli_main
        return cli_main(args[1:])
    if args:
        raise SystemExit('Use --self-test, --verify-export <dir> [stem], --offline-review <args>, or launch GUI without args')
    from kuodra.gui import main as gui_main
    gui_main()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
