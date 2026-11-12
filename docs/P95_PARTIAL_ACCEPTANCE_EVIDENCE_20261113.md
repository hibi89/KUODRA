# KUODRA P95 attempt — VERIFIED PARTIAL DELIVERY, P95 **NOT YET ACHIEVED**
**2026-11-13 KST | Technical progress toward P95 | RELEASE HOLD / SALE NO-GO**

## Verdict
**Current provisional engineering assessment: 87/100 (previous 85/100, +2 pp)**, using the original D0–D8 weighted scope and exact CI. **The requested P95 milestone is NOT met**. This figure is a bounded internal engineering estimate and *not* 87% of production, financial, legal or buyer readiness. The P95 acceptance contract requires real, rights-cleared KR+US company E2Es, buyer Windows GUI/installer, and legal/rights risk substantially closed. Those prerequisites are not available without the owner's lawful key/contact, an external provider response and a real Windows 10/11 buyer test.

**Source:** `hibi89/KUODRA` private, `develop` [PR #5](https://github.com/hibi89/KUODRA/pull/5) merge `213e11ed5221b1d3ac668a157cac9341dfa2b652`. Original KIC repository, source and official submission remain unchanged. `main` stores documentation; no commercial code merged to main and no production service deployed.

## Exactly what changed
1. **SEC source size mismatch fixed:** `kuodra.safe_io.source_limit_for`, CLI and GUI now allow up to 10 MB of bounded local CompanyFacts while DART remains 1 MB. No symlink/hardlink, country mismatch, over-limit or client-origin rights bypass. Synthetic 1.2 MB issuer file is analyzed end-to-end in both CLI and GUI; public real SEC live payload remains untested.
2. **Consent-gated official provider entry:** `kuodra.official_review` makes one fixed-URL GET via the pre-existing SEC/DART allowlisted client only after explicit owner consent and legally supplied identifiers/key. A 403/429, DART error/status 013, wrong CIK/corp_code or absent key fail closed. Returned report says `publisher_authenticated=false`, `commercial_rights_verified=false`, `guard=HOLD`, `trade_executed=false`. The official source was **simulated in tests**, not contacted live.
3. **Owner-local external fetch CLI:** `python -m kuodra.official_cli` accepts `--consent` and local env `KUODRA_SEC_USER_AGENT` or `KUODRA_DART_API_KEY` (not command-line secret). There is no server proxy, no key in output, no background polling. Unsigned staged Windows entry also exposes `--official-review` with the exact same consent gate. An API key is a personal authorization and may not be shared or included in a purchased binary.
4. **Developer GUI UX:** dark card layout and distinct HOLD, blank company ID instead of fake ticker default, local PDF check box, HTML open and independent receipt integrity review. GUI stays local/offline by default. Controller tests verify no network, PDF, user-file preservation; real Windows GUI screenshot/monitor, Korean typography and buyer action testing **not done**.
5. **Windows portable integrity:** `kuodra.portable_manifest` inventories exact executable tree, file hashes and file set; ZIP is verified after unpack in a Korean-character path and supports safe no-Python-Path smoke. Manifest is explicitly **UNSIGNED**: not producer authentication, real installer verification or an approved customer release. The P95 Windows GitHub runner reported exact parity on **1,125 files**.
6. **Selected OSS dependency ledger:** installed packages/version/metadata collected, every item requires manual license verification. No claim that bundled DLLs/fonts/transitive packages have a complete NOTICE/license clearance.

## CI evidence
- Tested feature SHA: `441445ef0e60d24b1a33973f897f593c3bf6ceaa`.
- [PR #5 GitHub Actions #43292742904](https://github.com/hibi89/KUODRA/actions/runs/43292742904): Ubuntu `245 PASS / 0 FAIL`, Windows `245 PASS / 0 FAIL`. Staged unsigned PyInstaller Windows EXE smoke, source Guard HOLD, no Python PATH, ZIP extract in Korean path and exact SHA inventory (1,125 files) all PASS.
- Linux latest 245 tests, Windows latest 245 tests. Features include explicit NO_NETWORK_WITHOUT_CONSENT and API redaction and guarded output.
- Earlier temporary test failure in P95 candidate at Actions #43289953239 (Ubuntu 219 tests, one failure): synthetic 'a'×64 SHA accidentally contained the same 'a'×40 sequence as the fake credential; replaced synthetic checksum with distinct 'f'×64 and later full 245 PASS. **This was a test fixture collision, not a detected real token leak.** GitHub Actions intermediate runs cancelled by `cancel-in-progress` due to successive commits, not counted.
- Post-merge exact-`develop` CI should be checked separately from feature PR CI and added to STATUS/HANDOFF; never represent release/P95 complete merely by PR merge.

## Unchanged D0–D8 rubric and narrow incremental score
| Area | P85 | Latest partial P95 assessment | Evidence and remaining blockers |
|---|---:|---:|---|
| D0 design/provenance | 5 | 5/5 | Existing source/history and final design |
| D1 licensed source input | 9 | **10/12** | Opt-in SEC/DART gateway integrated and simulated error/consent tests; **actual lawfully used KR+US provider E2E missing** |
| D2 issuer/accounting/time | 12 | 12/13 | Existing synthetic as-of corrections and reconciliations; real issuer/IFRS verification outstanding |
| D3 A/B/C | 17 | 17/18 | No real licensed stock benchmark or verified sector business model |
| D4 ML | 11 | 11/12 | Synthetic-only issuer/time heldout, not financial predictive improvement |
| D5 Guard/private | 13 | 13/13 | scoped local safeguards; **OS-level private IAM/no-egress for confidential buyer data not certified** |
| D6 GUI/report | 10 | 10/10 | New GUI and PDF controller tests improve quality, no extra point; real buyer visual/font test still required |
| D7 Windows operations | 6 | **7/8** | Unsigned CI EXE, ZIP relocate and file hash inventory; no buyer Win10/11 installer/upgrade/uninstall or AV/signing |
| D8 customer/license/sale | 2 | 2/9 | Selected dependency metadata only, full redistribution license, buyer support, financial law and actual customers unverified |
| **Total** | **85** | **87/100 provisional** | **P95 target short by 8 points; hard gates still open** |

**Methodology:** these are assistant-assigned bounded engineering coverage points, not third-party certification, legal fitness or actual output confidence. Especially D5/D6's provisionally full *local* scores do not waive real confidential source/Windows/GUI acceptance hard gates.

## Source/data/legal stop conditions
- Real SEC CompanyFacts for one owner-approved CIK must be fetched lawfully with genuine identifying User-Agent and analyzed against official 10-K dates and XBRL. We have not made a real SEC GET or claimed a verified external publisher.
- A real DART `corp_code` (8 digits) + owner-provided 40-character OpenDART API key must be tested for annual statement, actual fiscal dates, correction/receipt and accounting taxonomy. The API key must **not** be pasted in chat, emailed or checked into any repo; OpenDART terms prohibit a third party using another member's credentials.
- No vendor-supplied market/index historical series until properly licensed. `A=UNAVAILABLE` otherwise.
- Buyer Win10/11 physical GUI+Korean PDF, signed/notice-complete installer with upgrade/uninstall, malware/SmartScreen, exact source hash, source non-deletion, OS-level credential/no-egress and actual customer validation remain absent.
- OSS package licenses + all bundled DLL/bootloader/fonts and original corporate prose ownership, Korean finance regulation, business registration/sales terms/refunds/support and owner release GO still pending.
- Therefore no production release, seller listing, charged customer distribution, market performance guarantee, auto trading, 95% declaration or score inflation. `RELEASE HOLD / SALE NO-GO`.

## Implementer-only next action
Only after the owner supplies *on their own local Windows* their real official SEC contact/real permitted files, separately obtains an OpenDART key and approves authorized external calls, run commands and checklist in [P95 real source and release gates](P95_REAL_SOURCE_AND_RELEASE_GATE_20261113.md). The assistant can continue all independent code/CI work; it cannot fabricate real access rights, third-party contractual licenses, physical buyer device acceptance or a financial legal review. Set central Kmong KUODRA **87% provisional and [작업중] toward P95** while other products remain untouched. Record exact commit and CI proof after merge.
