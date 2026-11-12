# KUODRA P95 continuation — DART CIS compatibility and frozen Windows Tk GUI proof
**Checkpoint: 2026-11-13 KST | target 95 NOT achieved | last scored bounded engineering 89/100 provisional | RELEASE HOLD**

## Scope, source and decisions
- Product: `hibi89/KUODRA` private, latest source integrated only to `develop` via [PR #7](https://github.com/hibi89/KUODRA/pull/7), merge `733104a08fb99f4baf5bf4be520b0f7d88729f56`. `main` remains documentation/release baseline, no user sale package/deployment.
- Real issue: official OpenDART `fnlttSinglAcntAll` lists `sj_div` values BS / IS / **CIS** / CF / SCE, while earlier KUODRA allowed revenue and `ProfitLoss` only when `sj_div=IS`. A valid company income statement in CIS could fail to expose source facts.
- Choice A (implemented): permit **IS or CIS** only for `ifrs-full_Revenue` and `ifrs-full_ProfitLoss`; retain strict BS/CF boundaries and existing as-of logic. If duplicate IS/CIS observations from the same filing date disagree numerically, `RECONCILIATION_SAME_DAY_CONFLICT` aborts instead of preferring either. Identical values are deduplicated through existing reconciliation with audit. B alternative (rejected): blindly prioritize IS over CIS, which could hide a material discrepancy.
- Official source: [OpenDART complete single-company statement contract](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020). No real issuer/key or owner confidential data were used. Synthetic schema-shaped test inputs do NOT prove real provider identity/rights and keep Guard HOLD.

## GUI and Windows evidence
- The native tkinter app previously had a fixed-height form containing 11 rows and could clip bottom actions on a small-screen customer device. Updated UI wraps the same controls in a vertically scrolling Canvas and scrollbar; keeps country/issuer/statement/as-of/source, financial result logic and no-network default unchanged.
- Added `--gui-smoke` staging-only command to `desktop/entry.py`. On a real Windows-hosted GitHub runner this instantiates the actual **PyInstaller-frozen** tkinter application, checks 11 required controls, safe default country/empty issuer, Guard HOLD label, no external source/network, scrolls to the bottom, and asserts action bar reaches the viewport. Destroys the test window immediately; never tests real owner files or buyer clicks.
- Feature branch exact HEAD `49d78a013ad51495d8facc0d82e3c2103a2ae99d` checked by [GitHub Actions #43302772793](https://github.com/hibi89/KUODRA/actions/runs/43302772793): **Ubuntu 282 PASS / 0 FAIL**, **Windows 282 PASS / 0 FAIL**; Windows unsigned PyInstaller EXE self-test + frozen Tk GUI smoke + ZIP exact 1,125-file SHA verification in Korean path, side-by-side safe install/verify/explicit remove, customer sentinel preserved: **SUCCESS**. Test command `python -m unittest discover -s tests -v`.
- The Windows-hosted GitHub runner is not proof of a consumer Windows 10/11 install, 100%-scale screenshots, Korean font/PDF print quality, SmartScreen/Defender behavior, permission/OS sandbox, installer signature or the full customer mouse-and-keyboard journey.
- Post-merge exact SHA CI is to be checked separately; do not conflate feature PR CI with sale proof. CI without screenshots cannot claim pixel-perfect visual acceptance.

## Fixed rubric: keep 89 provisional, do not manufacture points
| Area | Previously | Now | Rationale |
|---|---:|---:|---|
| D0 design | 5/5 | 5/5 | unchanged source/spec trace |
| D1 country source input | 11/12 | 11/12 | CIS compatibility improves real-schema handling; actual lawful KR+US provider E2E not done, so no credit for last point |
| D2 accounting/identity | 12/13 | 12/13 | additional official mapping checked but no real issuer/authentic restatement verification |
| D3 A/B/C | 17/18 | 17/18 | real licensed market/sector evidence still missing |
| D4 statistical/ML | 11/12 | 11/12 | synthetic grouped holdout only |
| D5 Guard/private security | 13/13 | 13/13 | local safeguards only, institution OS IAM/no-egress untested |
| D6 customer UI/report | 10/10 | 10/10 | actual Windows runner smoke improves evidence but no extra point available; real buyer UX and fonts remain unverified |
| D7 Windows staging/ops | 8/8 | 8/8 | Tk frozen startup and scroll checks improve evidence but no additional point; unsigned portable is not sale-ready installer |
| D8 actual sale readiness | 2/9 | 2/9 | lawfully authorized company data, complete OSS notices, customer acceptance, financial legal clearance and owner sale GO missing |
| **Engineering subtotal** | **89** | **89 provisional** | **User P95 target not met, 6 points remain under original rubric** |

Caveat: D5/6/7 provisional local-scope full credits do **not** waive the real buyer/contract/security gates originally stated by REQUIREMENTS.md. This score is an internal engineering progress indicator, not independently certified legal/production completeness.

## Remaining blockers before P95 / sale GO
1. Owner-authorized SEC public company financial CompanyFacts **actual** E2E with identifiable genuine User-Agent (no invented person/contact), correct CIK/form/period/fact reconciled to official filing and lawful terms.
2. One real OpenDART company annual filing via **owner's own** lawfully issued key, request FS scope, corp_code and independently checked fiscal-end and receipt number; no key in GitHub/chat; confirm rights to distribute derived content. APIs do not authorize market/index resale.
3. Clean consumer Windows 10/11 interactive GUI + Korean browser-to-PDF + antivirus/SmartScreen + signed installer, upgrade/uninstall no data loss, real customer usability and binary transitive dependency LICENSE/NOTICE audit.
4. Confirm financial-advice/advertising/privacy/sales-support/refund boundaries with qualified review; obtain explicit owner release approval. Do not disable Guard HOLD, fabricate financial prediction, publish executable, deploy production or remove central P95 `[작업중]` marker until gates met.

**Safe rollback:** previous integrated functional SHA `8b8801991870f1a98117b68bd23ed2e99c77cacb`, preserved Git history without force push. Original KIC submissions/sources unchanged. No paid/new API/permissions or buyer data were touched.
