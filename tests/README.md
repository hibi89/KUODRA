# KIC-derived core regression snapshot

Files copied unchanged from hibi89/hibi89-kic-proofinvest @ lead/kic on 2026-11-12. Original blob hashes in docs/KIC_REUSE_MAP.md. All fixtures use synthetic values. Run on this exact branch:

python -m unittest discover -s tests -p 'test_kuodra_*.py'
python -m unittest discover -s tests -p 'test_guard_agent.py'

Optional ML tests require scikit-learn; tests may SKIP when absent. Verify result count, failures, code SHA and paths before claiming pass. This copy has no U.S. SEC real-data or DART API integration and is not a production release.
