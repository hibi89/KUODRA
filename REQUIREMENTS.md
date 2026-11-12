# KUODRA FINAL PRODUCT 100/100 — single authoritative acceptance definition
**Product:** evidence-grounded, privacy-respecting local Windows company finance/disclosure verification tool supporting Korean DART and United States SEC. BASIC first, PRO second, BUSINESS when proven. No investment recommendations or automated order placement.

## Buyer journeys
1. BASIC: Launch on clean Windows PC → choose KR/US → company official identifier + period/as-of → locally input lawful file or opt in to authorized source query → obtain verified account and financial B findings → see source, formula, chart/table and HOLD reasons → export readable report.
2. PRO: Compare multiple fiscal periods or comparable peers and licensed stock/index series when entitled; optional statistical and ML insights with independent heldout evaluation, baseline and provenance. Missing features are explicitly UNAVAILABLE.
3. BUSINESS: Locally analyze owner-approved restricted CSV, read-only SQLite and deliberately structured PDF/DOCX; account isolation, no-egress and local OS controls must be actually proven before sale.
4. Error path: identification mismatch, amended filing, future information leak, CFS/OFS conflation, exchange-rate assumption, undocumented source/rights or insufficient data → deny, with actionable user explanation. No silent fill or false confidence.
5. Restart/repeat: no destruction of customer inputs or previous exports, idempotent cache keyed by rights/source/fiscal vintage/owner, no unapproved network call.

## Weighted final engineering and sale acceptance (100 points)
| Area | Weight | Evidence required |
|---|---:|---|
| D0 Final design, documentation, traceability | 5 | README, AGENTS, REQUIREMENTS, BLUEPRINT, SCHEMA, KIC provenance, branches, 10-part HANDOFF consistent |
| D1 Licensed country-specific source input | 12 | KR DART + US SEC lawful source adapters or customer-owned files, rights/rate/auth/403/429, two actual lawful E2Es |
| D2 Canonical identity, accounting, time | 13 | CIK vs DART corp_code, issuer aliases, fiscal/YTD, CFS/OFS, currency/unit, filing amendments, publication/as-of, collision/future negative tests |
| D3 A/B/C source-grounded engines | 18 | A rights-gated market/financial comparison or unavailable; B finance integrity formulas and facts; C comparable peer cohort, report/HOLD fallback |
| D4 ML/statistical interpretation | 12 | FDR, sample count, Dummy baseline, time/issuer holdouts, no leakage, appropriate MAE/RMSE or calibration/Brier, NO_TRAIN on weak data |
| D5 Guard, audit, private security | 13 | Evidence sha/locator + VERIFIED/CONFLICT/UNAVAILABLE, HOLD/REJECT, principal/access/no-egress, malicious document/output denial |
| D6 Customer interface and visual reports | 10 | company/period UX, source hyperlinks, >=2 formulas, readable table+graph, human explanation of errors, faithful HTML/PDF and independent visual QA |
| D7 Windows packaging and operations | 8 | clean Win10/11, installer/launch/upgrade/uninstall, no required Python for buyers, path/Unicode/AV/security, files preserved |
| D8 Real end-to-end and sale readiness | 9 | licensed actual company examples both countries, user acceptance, OSS notices, financial compliance, help/support/returns/price, owner sale GO |
| **TOTAL** | **100** | **Not based merely on number of tests or copied files** |

**Current new repo: 89/100 PROVISIONAL INTERNAL ENGINEERING, P95 TARGET NOT ACHIEVED.** [Current P95 follow-up](docs/P95_FOLLOWUP_EVIDENCE_20261113.md) preserves fixed D0–D8 weighting: D0=5 / D1=11 / D2=12 / D3=17 / D4=11 / D5=13 / D6=10 / D7=8 (only unsigned Windows runner staging) / D8=2. Source `develop@8b8801991870f1a98117b68bd23ed2e99c77cacb`; exact feature [CI #43298114834](https://github.com/hibi89/KUODRA/actions/runs/43298114834) Ubuntu/Windows **275 PASS each**, Windows ZIP SHA+staging install/uninstall preserves sentinel. **P95 real authenticated/rights-cleared KR+US filings, consumer Windows10/11, licensed market data, finance compliance, OS deny-egress and owner sale GO have NOT passed**. Technical points are not external certification or commercial readiness. **RELEASE HOLD / SALE NO-GO**, no release main merge.

## Milestones (not automatic scores)
- P50: Core transferred with independent regression, synthetic KR/US file→canonical→B+Guard→basic report, initial UI.
- P70: Source and fiscal reconciliation for both countries, measured B/C; rights-gated A; evidence reports.
- P85: Complete optional ML safety, graphs/formulas, Windows installation, failure/recovery and negative security testing.
- P95: Source entitlement and actual KR/US data E2E, final customer UI, independent Windows tests, legal/right risks largely closed.
- P100: Buyer-ready complete rights and financial review, hash-pinned installer and reports, support/refund terms, owner release approval.

No fabricated improvement of financial prediction or trading outcomes. Measured local CI is not proof of real market superiority.
