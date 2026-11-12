# KUODRA — Global Financial Evidence Intelligence

Independent commercial **Korean + US corporate disclosure and financial evidence verification** software.

**State as of 2026-11-13 KST:** P50 engineering 50/100 provisional ACCEPTED on tested develop SHA 74c2f4db6ef419780d66a89a1e15c91fab4bd272; RELEASE HOLD, not commercial-ready. See docs/P50_ACCEPTANCE_EVIDENCE_20261113.md.

## Product promise (final target, not implemented delivery)
User chooses KR (DART) or US (SEC), company and as-of date, supplies authorized filings/local documents or explicitly authorized official API access, then the system validates provenance, fiscal period, units, issuer identity and release time. A market-vs-fundamentals (rights-gated), B financial integrity, C peer/industry context and optional calibrated/tested ML produce source-bound numbers, formulas, charts, uncertainty, Guard HOLD/REJECT and an auditable HTML/PDF report. No trading or individualized buy/sell advice.

## Startup reading order
HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → docs/BLUEPRINT_100.md → SCHEMA.md → docs/KIC_REUSE_MAP.md → docs/BRANCHES.md → source + tests.

## Ownership, scope and original
This private repository is the **commercial source of truth**. The KIC competition original remains separate and unchanged at https://github.com/hibi89/hibi89-kic-proofinvest/tree/lead/kic .
Source-test legacy SHA 808e62ef78904ec95448338b8573c7d8683b516c, Linux/Windows each 2,397 tests with 0 failed (Windows 1 skip) on legacy GitHub Actions 42737631543. **Those are legacy historical test counts; no new repo test has passed by inheritance.**

Architecture: **main** release/design baseline, **develop** tested integration, feature branches listed in docs/BRANCHES.md. Newly imported code may be present on develop without main merge. The first version should run locally on Windows with no mandatory cloud service and should work with lawful operator-owned files. Data rights are assessed independently from API connectivity.
