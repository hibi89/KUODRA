# KUODRA branch architecture and source folders

**main:** release/approved specification baseline. Product not sold; no source feature merged without tested develop and owner release gate.

**develop:** integration and selectively migrated KIC core with independent tests.

**feature/core-evidence:** canonical, source hashing, historical as-of, A/B/C + Guard base.

**feature/markets-kr-dart:** DART corp_code, rcept_no, CFS/OFS, K-IFRS mapping, corrected filings, KR synthetic/rights-gated API.

**feature/markets-us-sec:** SEC CIK/CompanyFacts/10-K, 403/429/fair access, authorized local files, US accounting normalization.

**feature/stats-ml:** FDR, heldout metrics, Dummy baseline, no-future-data and NO_TRAIN contracts.

**feature/desktop-reports:** Windows local UX, charts/formulas/HTML/PDF, package and QA.

**feature/enterprise-local:** PRIVATE ingestion/owner IAM/OS deny-egress (later, no real enterprise data until approved).

**feature/qa-commercial:** cross-country rights/legal/license audit, Windows customer release and business acceptance.

Changes: feature → tested develop → validated/approved main. Existence of branch does not imply built source or completed merge.

Target folder ownership:
- proofinvest/ initial original KIC Python back-end snapshots during transition
- kuodra/markets/kr and us data source adapters
- kuodra/pipeline issuer/time/units normalization
- kuodra/engines + stats_ml + guard domain logic
- kuodra/reports HTML/PDF evidence renderer
- desktop/ Windows GUI/packaging
- tests/ exact new repo tests, fixtures/synthetic/ no real customer data
- docs/ blueprint, rights, provenance, validation, SKU and handoff

Some target directories exist only in the blueprint until implementation. Do not represent empty dirs as completed functions. No force pushes, history rewrite, automated sale deployment or changing repo permissions.
