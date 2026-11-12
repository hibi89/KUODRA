# KUODRA P85 — provisional engineering milestone acceptance, RELEASE HOLD
**2026-11-13 KST · Internal scope evaluation, NOT a customer/commercial release approval**

## Verdict and scope
**P85 internal engineering target: 85/100 provisional (P70 + 15%p).** This is a human-assessed technical coverage metric backed by exact SHA CI and narrowly scoped offline/synthetic scenarios. It does NOT mean the 100-point real-source, customer security, law/rights and Windows installer gates are 85% actually cleared. Those hard gates remain **BLOCKED/UNVERIFIED**. Owner sale and merge-to-main GO were not given.

- Product source: `hibi89/KUODRA@develop` code integration commit **`46889e4ea14aaa27feb7874f6bf120aee3010dee`**, via [PR #4](https://github.com/hibi89/KUODRA/pull/4); `main` is release/architecture/doc-only.
- Last feature functional SHA `03ea607c239b773cfcfca61557b9064e8764759a`, tested at [Actions #43286155661](https://github.com/hibi89/KUODRA/actions/runs/43286155661) both Ubuntu & Windows **197 PASS / 0 FAIL / 0 SKIP**, Windows PyInstaller `--onedir` unsigned EXE self-test, full offline KR synthetic report + receipt verifier, ZIP compress/extract into a Korean path and protected customer sentinel unchanged, no preinstalled Python PATH used during EXE smoke.
- Post integration PR-scope [Actions #43286619965](https://github.com/hibi89/KUODRA/actions/runs/43286619965) both Ubuntu & Windows **197 PASS / 0 FAIL**, Windows staged EXE, ZIP+Korean-path and original-preservation checks **SUCCESS**. GitHub check uses a temporary PR merge ref of the code merge plus main's docs baseline; it is not a production build or a buyer's Windows machine. No hosted Production URL or delivery binary published.
- Retained P70 baseline `cee8edc6d85d7d513fb93748d21501342624a1c1`, 146 PASS/OS, and KIC contest original source/SHA unchanged. KIC 82% competition percentage was never inherited.

## Feature diff from P70
1. `kuodra/heldout.py`: **synthetic-only** issuer-disjoint + release-time-disjoint train/test, regularized one-feature baseline vs train-mean Dummy, MAE/RMSE, minimum sample, leakage/duplicate/malformed records blocked. `prediction_claim=false`, `Guard=HOLD`; **not a real equity forecast or calibrated finance ML**.
2. `kuodra/review.py`: source-linked **positive accounting earnings with negative operating cash**, receivables growth above revenue growth, inventory growth above revenue growth flags. These are **review questions, not fraud findings**; country/year/source/period constraints and prior formula evidence retained.
3. `kuodra/report.py`, `kuodra/report_pdf.py`: show the synthetic holdout vs Dummy, B flags, source evidence and limitations in HTML/PDF; 4-file JSON/HTML/(optional PDF)/unsigned-receipt no-overwrite export.
4. `kuodra/release_gate.py`: independent bounded file/hash/evidence/Guard/receipt verifier, rejects altered HTML/JSON and fake PDF, symlinks, hardlinks, forged receipt scope. SHA match does **not** establish producer identity/market license/cryptographic signing.
5. `kuodra/safe_io.py`: bounded read-only local input with fd/path inode recheck, symlink/hardlink rejection and no silent network access; not an OS IAM/no-egress sandbox. `kuodra/report.py` now **never unlinks any output after a partial failure**; incomplete files require explicit owner inspection and new output stem. Test simulates another process replacing created output path.
6. `desktop/entry.py` and workflow: staged unsigned PyInstaller Windows onedir binary, local `--self-test`, `--offline-review`, `--verify-export`; zip relocation/Korean path run and unrelated-file preservation. **Not an installer, signed package, tested Windows 10/11 buyer interaction, controlled upgrade/uninstall or third-party license clearance**.
7. Regression tests: exact new P85 197/197 on both CI platforms. Windows test initially 1 FAIL in [#43285839249](https://github.com/hibi89/KUODRA/actions/runs/43285839249) because old tamper test wrote HTML in Windows default cp1252 rather than UTF-8; fixed test encoding in `03ea607...` and the next two runs passed. Earlier installed dependency CI failures remain historical P70, not new success evidence.

## Provisional internal coverage breakdown (fixed 100-point product denominator)
| Domain | P70 | P85 tentative | Engineering evidence, remaining hard gate |
|---|---:|---:|---|
| D0 design/source trace | 5 | 5/5 | unchanged blueprint, KIC unchanged, GitHub exact SHA |
| D1 country data access | 9 | 9/12 | lawful local/fake SEC/DART transport; **no authenticated rights-cleared real KR+US provider E2E** |
| D2 accounting/timeline | 12 | 12/13 | existing annual revision/date/CIK-corp mapping, real-filing taxonomy verification pending |
| D3 A/B/C financial engines | 16 | 17/18 | new source-linked financial B review flags; real licensed A and verified industry C pending |
| D4 stats/ML | 8 | 11/12 | synthetic grouped/time-heldout Dummy baseline; *no real finance model quality validation* |
| D5 Guard/provenance/local security | 11 | 13/13 | evidence/receipt, bounded local read, never-delete failure behavior; **OS IAM/no-egress for real confidential data remains a commercial blocker despite provisional local-scope credit** |
| D6 visual evidence UX | 9 | 10/10 | evidence charts/table/formulas, conditional ML vs Dummy, guarded HTML/PDF; actual buyer GUI/Korean fonts still not independently visually accepted |
| D7 Windows portable/operations | 0 | 6/8 | unsigned CI onedir EXE + Python-PATH excluded smoke, ZIP extraction/Unicode path and source-preservation. Proper installer/AV/upgrade/uninstall/Win10/11 customer test pending |
| D8 owner fulfillment readiness | 0 | 2/9 | explicit [staging acceptance and support/rights checklist](P85_CUSTOMER_ACCEPTANCE_CHECKLIST_20261113.md), SHA-bound handoff and synthetic CI; **no actual buyers, formal OSS license review, support/returns or legal approval** |
| **Total** | **70** | **85 provisional** | **Scope score only; release gate is NOT MET** |

**Important methodological caveat:** Partial point allocation is a judgment, not an independent external certification. D5 and D6's local engineering ceilings do not waive requirements for real OS/IAM, buyer GUI/typography, and finance data rights; those remain hard blockers even when a domain's provisional scoped engineering credit is full. Do not apply this score to external advertisements.

## Stop / pivot and pending 95/100
1. Acquire actual lawful SEC companyfacts and OpenDART customer-owned key/files and validate issuer/fiscal/filing publisher E2E with use/redistribution rights. Any HTTP 403/429/013 -> stop, not workaround. Until then Engine A with real index data UNAVAILABLE.
2. Verify user-facing Windows 10/11 no-Python interactive GUI, Korean PDF/fonts, user directory non-deletion on upgrade/uninstall, actual package integrity/signature/Defender, source notices and support/returns. The staged ZIP is temporary CI evidence, **not published deliverable or signed buyer app**.
3. Real-model data usefulness and company-time split; optional synthetic ML does not establish prediction performance. No verified issuer/sector source, private enterprise IAM/OS deny-egress, legal financial advisory clearance or consent for commercial sale.
4. No new code to main, no Vercel/production, paid APIs, secrets, customer uploads, data rights override, auto trading or sale. `SALE NO-GO` / `RELEASE HOLD` stays in force.
5. Subsequent P95 development must be owner-requested and scored from new exact SHA tests; P85 `[작업중]` can be removed on verified **engineering milestone only**, not to imply sale readiness.

## Reproduction/rollback
- CI: `python -m pip install -r requirements-ml.txt -r requirements-report.txt "scipy>=1.11,<2.0"`, `python -m compileall -q proofinvest kuodra tests`, `python -m unittest discover -s tests -v`, and Windows workflow PyInstaller ZIP staged checks.
- Verify code merge commit `46889e4ea14aaa27feb7874f6bf120aee3010dee`. Rollback via previous P70 `cee8edc6d85d7d513fb93748d21501342624a1c1` or preserved Git history; no force push.
- Evidence: PR #4, Actions #43286155661 and #43286619965; `develop` owns code, `main` documentation/release hold, central `kmong-productization` candidate KUODRA row should be updated to 85 provisional without touching other products.
