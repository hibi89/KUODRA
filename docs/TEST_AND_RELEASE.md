# KUODRA independent test and release plan
Current status on new repo: tests run 0 / no actual customer Windows app / no authorized real external source E2E / no sales.

Required unit+adversarial cases:
1. US CIK & KR corp_code strict namespace, ticker alias correction, separate amendments and company identity.
2. DART fiscal YTD vs quarterly delta, CFS/OFS, differing currencies/units, 10-K/10-Q/annual, as-of release.
3. Authorized raw file vs opted-in HTTP sources: SEC 403/429 and call budget, DART auth/quota, rights-absent A UNAVAILABLE; fail closed.
4. B CFO vs NI, revenue vs receivables/inventory, debt/equity with zero denominator. C peer comparable and incomparable cohorts. A risk metrics only with licensed market series.
5. ML chronological/issuer-heldout negative tests, leakage, Dummy, sample size and FDR, NO_TRAIN.
6. PRIVATE role ACL and no network, malicious docs, path escapes, duplicate source, original replays and audit receipts.
7. Actual dashboard source hyperlinks, table, at least 2 visible formulas, graph, clear limits, PDF/HTML exact-page review.
8. Windows 10/11 buyer machine with no preinstalled Python, Unicode path, restart/install/uninstall and Defender/SmartScreen, backup/cleanup/rollback.
9. Source/data commercial rights, NOTICE/licensing, buyer support/returns, business price test and explicit owner release GO.

Record exact source+test SHA, commands, PASS/FAIL/SKIP, environment and screenshots/artifacts. CI success not proof of Production, market validity or legal entitlement.
