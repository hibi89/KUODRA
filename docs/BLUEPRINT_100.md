# KUODRA — definitive commercial product blueprint (2026-11-12 KST)

## 0. Product identity and non-negotiables
KUODRA is an evidence-grounded **financial research and corporate filing verification** product, expanding KIC ProofInvest/KUODRA's existing technical assets. Brand KUODRA was owner-selected from an earlier K+QUADRA concept; never advertise unexplained performance multipliers. It is *not* affiliated with KIC, not investment advice, not a trading bot, and not a validated market-prediction system.

Customer benefits: (i) reconcile contradictory reports/units and filings; (ii) explain suspect revenue/cash/inventory/receivables with a reproducible formula; (iii) cross-check relevant industry comparators only when meaningful; (iv) keep owner private data local; (v) show source, uncertainty and why Guard held a claim. Existing KIC engineering success ≠ released commercial software.

### Target customers and order
1. Korean retail analysts/finance learners/small researchers: KOSPI/KOSDAQ DART and financial integrity.
2. SMEs, finance/accounting/credit-supply-chain analysts: company and trading counterparty financial checks without unsupported credit-rating declarations.
3. US company researchers: SEC XBRL/CompanyFacts and optional lawful comparisons.
4. Later B2B on-premise internal documents and authorized client data, only after IAM and no-egress acceptance.

## 1. End-to-end workflow
- Start local Windows program → choose KR or US + company alias/ticker → resolve authoritative legal identifier (KR DART corp_code vs US CIK) and check validity/as-of.
- Choose fiscal/filing period, consolidated/separate and cutoff available_at; user consent and source rights checked before any online call.
- Load only legal owned local files or rights-approved data. Never bundle unlicensed quotes, index histories or third-party report prose.
- Store distinct immutable source receipt (publisher, URL, filing accession/receipt, byte SHA, retrieval date, rights/consent) separate from normalized factual observations.
- Map source country/fiscal codes to versioned canonical schema with explicit currency, unit, fiscal_start/end, observation_at, available_at, statement type, CFS/OFS and amendment vintage. Fail closed on ambiguities.
- Engine A/B/C each return a status, exact calculation, evidence and limitation; if no entitled market data, A=UNAVAILABLE but B/C still run.
- Optional stats/ML uses predeclared target/interval, release-time-safe chronological/issuer-held-out splits, Dummy baseline, FDR; absent valid evidence => NO_TRAIN.
- Guard checks identity, rights, contradictory source, release time, authorization and evidence. Outcomes are report-review eligibility only, never authority to buy/sell.
- UI presents company, period, figures, **charts/tables/equations**, original links, contradiction/risks and caveats. Generate local HTML/PDF/JSON receipt that includes source/version SHA, fails safely if destination exists.
- Human decides; report and raw source must remain separate, repeat analysis is deterministic for same source/version.

## 2. System boundaries and architecture
~~~text
User company/period/as-of and ownership consent
     |       |
     |   Source-rights / privacy / API budget gate
     v       v
US collector SEC   KR collector DART   OWNER local CSV/SQLite/PDF/DOCX
   public allowlist, bounded GET        private local worker, no-egress
     |               |                         |
     +------ provenance + publisher receipts --+
                         |
       issuer identity + fiscal/unit/time mapping
                         |
         canonical long schema (source preserved)
                         |
       A Market       B Finance Integrity       C Industry
       [licensed]     [verified statements]     [matched peers]
                         |
        optional stats/ML, strict historical holdout
                         |
        Evidence ledger + deterministic Guard HOLD
                         |
          human reviewed desktop dashboard
                         |
            local HTML/PDF/report receipt
~~~
Choose common engine + country adapters (vs separate KR fork) to avoid duplication and preserve existing SEC code, with single documented schema. Choose buyer-owned local Windows delivery (vs SaaS) for low recurring costs and private data risk; later host option requires new approval.

## 3. US SEC adapter
- official CIK mapping, ticker and legal issuer history; submissions and CompanyFacts JSON plus filing accession, 10-K/10-Q/A amendments, 8-K where appropriate; XBRL taxonomies and share units.
- Distinguish FY/yearly vs Q/YTD, split dates, statement and fiscal vintage. No automatic replacement of past facts with later-released amendments at historical as-of.
- SEC API requires identifiable User-Agent and fair-access controls (currently up to 10 requests/second); use much lower configured budget, cache by CIK/source/vintage, wait/stop on 429, no bypass of 403. For offline customer-provided files, origin is **not authenticated** unless independently verified.
- Fact/numeric source-derived computations may be provided with citation, while full authored company document prose/charts and market/index content need separate redistribution rights. No bulk company dataset resale by default.

## 4. KR DART adapter
- corp_code (official legal entity), stock_code and name aliases with observation/release/validity dates; never reuse US CIK to represent KR issuer.
- Quarterly/half/annual report and corrections, source rcept_no, CFS/OFS, K-IFRS account identifiers, financial statements, discrete quarter vs YTD and cash flow amount semantics.
- Account-specific mapping for revenue, operating income, net income, CFO, inventory, receivables, assets/liabilities/equity, CAPEX where proved; missing/disputed accounting labels remain unavailable. Comparisons must normalize period and currency (KRW vs USD).
- Actual OpenDART endpoint/key usage and cache/redistribution rights require provider-specific approval. Prefer lawful buyer local files in early MVP. No unlicensed KRX price scraper; if market data unavailable Engine A=UNAVAILABLE.

## 5. Engine A — Market Reality
Input rights-cleared stock return series, true benchmark series and aligned issuer fundamentals. Basic return R=(P_end/P_start)-1, simple relative delta R_stock-R_market. Where sample and volatility permit beta=cov(returns_stock, returns_market)/var(returns_market). Report calendar/price adjustment/dividends/splits, sample size and data licenses. Price-vs-revenue/EPS growth gap may be flagged as an *inconsistency needing examination*, never an exact 'bubble percent' or causal attribution. If market/benchmark unavailable or rights unclear: A=UNAVAILABLE, no disguised proxy ETF/index substitution.

## 6. Engine B — Financial Integrity
- Cash conversion CFO / NetIncome where denominator valid and meaning clearly explained; accrual gap NetIncome - CFO. Sign and sector nuances require cautious interpretation.
- Revenue growth vs receivables growth; inventory growth vs revenue; debt-to-equity (define liabilities vs interest-bearing debt); CAPEX/depreciation and debt/interest coverage when accounts/industry allow.
- Period-normalize quarter/YTD vs FY and CFS/OFS, show formulas, baseline, target, source URL/receipt and contradictory revisions. Flags are **candidates for human examination**, not confirmed fraud, accounting misconduct or credit default.

## 7. Engine C — Industry and Peer Context
- Comparators chosen by validated sector/industry, business model, geography, fiscal periods, currencies and source usage rights; 2 or more peers preferred, explicit peer-selection reason.
- Explain revenue/cash/earnings relative growth, peer dispersion and any industry/macro context **with source**; no pretending sector GDP implies an individual company's market share.
- If peers have no comparable verified data C=HOLD/UNAVAILABLE and no invented ranking or probability.

## 8. ML and multivariate statistical discovery
- Start with original same-country/or authorized-owner canonical data, declare target, lag, horizon and hypothesis/exploratory status.
- Feature building must enforce available_at<=as_of and observation_at<=available_at, release vintages, no issuer/group or time leakage; fold-local preprocessing.
- For exploratory associations show paired n, missingness, correlation/effect, uncertainty, multiple hypothesis adjustment (Benjamini-Hochberg FDR where applicable) and counterexamples, not causation.
- For prediction do chronological walk-forward/heldout, compare against Dummy, evaluate MAE/RMSE or suitable classification; calibrated probabilities and Brier only with enough independent ground truth. A high in-sample score is not a customer claim.
- Negative tests: shuffled labels, future-only features, repeated issuer IDs, stale revisions, too-small sample; if fail => NO_TRAIN/INSUFFICIENT_EVIDENCE. An LLM only explains already verified numeric evidence and cannot override Guard.

## 9. Evidence, Guard and local security
- Immutable original bytes/receipts separated from derived facts/features and exports. SHA detects changed bytes, **not publisher authenticity or legal rights**. Metadata includes source, original locator, issuer/period, observation/availability/revision, program/algorithm version and processing errors.
- Status contract VERIFIED / CONFLICT / UNAVAILABLE and Guard REVIEW_ELIGIBLE / HOLD / REJECT, with reasons, human override only through explicit review without rewriting evidence.
- Customer PRIVATE data: approved local read-only processing, no outbound network by default, distinct owner access, no SQL writes, no raw content/filename/derived private features in logs/prompts/cloud AI. Real IAM/firewall deny-egress has to be proven under OS; an in-memory class alone is not an enterprise security boundary.
- Handle malicious PDF/DOCX/CSV/SQLite, DTD/XXE, ZIP bombs, symlinks, HTML injection, file deletion races, overlarge inputs, duplicate replays. On uncertain rights/auth/metadata, fail closed.

## 10. Desktop/UI and evidence reports
- Initial core uses existing Python 3.11+, SQLite/Decimal, selective scikit-learn and local Streamlit as a dev UI; commercial customer needs a Windows package tested without preinstalled Python. Pick validated desktop wrapper after comparing launch/security/updates.
- UI: clear country/issuer, period and data-source form; analysis progress/errors and whether data is synthetic/real/verified; A/B/C result cards with rights status; charts (finance trends and peer bars), table (period/metric), >=2 visible formulas, verified source links, Guard reasons and limitations.
- HTML first, PDF exported only after visual/embedded font/source-link/integrity tests. Never simply fill a 10-page KIC-style proposal with text; demonstrate actual buyer-facing calculations and screenshots. Reports include request ID, time, data provenance, source right, formula/feature/method version, no-trading disclaimer and output SHA.
- Report save should use new unique name/version or fail without overwriting customer files; archive/raw original remains outside exported ZIP unless explicitly allowed.

## 11. Error recovery, API costs and repeatability
- Default offline/local file processing = no mandatory subscription/cloud, bounded memory/CPU. For opted-in sources cache and throttle by actual documented provider quota; request budgets/429 safe backoff (bounded), 403 immediate stop, nonfatal status visible.
- Triggered by human request, no background market-wide crawl, automatic trading, global price redistribution, hidden online upload, unauthorized scheduled monitoring.
- Retries must not duplicate reports, mutate source or leak user files; keep input/output hash and fresh immutable version. Windows startup/failure/upgrade/uninstall must preserve reports and customer originals.
- Source rights and code/library licenses assessed before any buyer distribution; customer-owned data rights cannot be assumed from mere file presence.

## 12. SKU, price and go-to-market hypotheses
BASIC single-company KR/US fundamental verification + evidence/Guard report: proposed market test KRW 49k–79k.
PRO multi-period/peer comparison, conditional A/B/C/ML, source-bounded charts: 129k–199k hypothesis.
BUSINESS authorized on-premise private finance files, role/egress verified; separate quote later. Not approved for current release.
First customers: company/disclosure researchers and SMEs assessing supplier financial narratives, not trading signal seekers. Competitive listings alone are not verified actual demand; validate installation, usability, buyer inquiries and returns/support.

## 13. 50 → 70 → 85 → 95 → 100 delivery sequence
- **Initial P0 D0 5/100 (historical 2026-11-12 baseline); CURRENT P50 50/100 provisional per STATUS and acceptance evidence:** product design, schema, policy, branch architecture, KIC source inventory. Product not executable from main.
- **P50 target:** safely migrated core and exact-SHA tests run in new repo, offline KR+US sample canonical/B/Guard, basic report and local UI.
- **P70:** source-licensed actual KR+US company cases and peer B/C, rights-gated A, verified time/unit/filing amendments, credible evidence outputs.
- **P85:** optional ML holdout/FDR, negative privacy security and Windows packaging, comparison charts/formulas, retry/error UX.
- **P95:** test verified real data with legal rights and full Windows customer scenarios, feedback, OSS/software licenses, sales docs and support policies.
- **P100:** rights and financial-regulatory owner GO, delivered Windows binary hash, accepted source/graphics/report, reproducible installed behavior, returns/refund support and verified customer experience.
No increase from counting migrated KIC tests as new CI. D0..D8 weights are in REQUIREMENTS and release acceptance requires separate evidence per scope.

## 14. Deferred and excluded
No paid SaaS, institutional KIC secret data, default external LLM/RAG, autonomous trading, open-ended scraping, automatic 'top picks', real-time index subscription, proof of fraud or guaranteed predictive returns. These need separate approved product scope and rights. This document is a **final build specification, not a declaration of completed capabilities**.
