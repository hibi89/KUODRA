# KUODRA P85 — Owner acceptance rehearsal, delivery boundaries and customer support gate
**2026-11-13 KST · Internal engineering preparation, NOT a consumer installation/release manual**

## 1. What exists and what does not
- P85 code is developed/validated on `develop` only after independent CI. `main` carries the approved product blueprint, contracts and evidence documents; no release merge to main or authorized paid distribution.
- The Windows CI creates an **unsigned PyInstaller onedir/ZIP staging candidate**. This is not an MSI/NSIS setup, not signed, and not approved by Microsoft Defender/SmartScreen or a real end-user machine. No production site, no automatic stock trading.
- Local tests use synthetic DART-shaped and SEC-shaped fiscal statements, plus optionally user-owned controlled files. The program does **not** authenticate that a locally supplied file is truly published by SEC/DART or grant commercial reuse rights.
- A: no licensed market/benchmark data => `UNAVAILABLE`; B: calculated unverified source and context/financial flags; C: only limited matched and unauthenticated synthetic peers; ML: only synthetic issuer/time holdout and KIC descriptive FDR. Even excellent synthetic Dummy-comparison scores are **not financial prediction performance**.
- Guard stays `HOLD`, `trade_executed=false`; own-file hash matching is not publisher authentication nor signature.

## 2. Staging-only owner acceptance script (tested by CI, not a customer instruction)
1. Use a clean temporary folder (avoid shared directories, customer archives or any production data). Keep a copy of inputs and note the source SHA/commit.
2. Run `KUODRA.exe --self-test`. Require JSON `status=STAGED_OFFLINE_ONLY`, `consumer_release_ready=false`, `trade_executed=false`.
3. With synthetic fixtures (kept in the GitHub source repo, **not guaranteed bundled in the ZIP**), run from the checkout's working directory:
```powershell
.\dist\KUODRA\KUODRA.exe --offline-review --country KR --issuer-id 99998888 --as-of 2025-11-12 --source fixtures/synthetic/kr_dart.json --output-dir C:\TEMP\kuodra-qa-output --name smoke
.\dist\KUODRA\KUODRA.exe --verify-export C:\TEMP\kuodra-qa-output smoke
```
4. Confirm `smoke.json`, `smoke.html`, `smoke.receipt.json` (and `smoke.pdf` when explicitly requested) match their hashes. The receipt is **unsigned**, and `FILES_INTACT_NOT_AUTHENTICATED` or `UNSIGNED_RECEIPT_MATCHED_NOT_AUTHENTICATED` is not a commercial source approval.
5. Verify the status continues to be `HOLD`, `rights_verified=false` and no source contact/real financial credentials or customer names are exposed.
6. Do **not** place outputs in a folder containing unrelated files when testing a fresh release. The export uses no-overwrite; a failed partial export leaves files untouched for manual review instead of deleting possibly substituted user paths.
7. Windows ZIP relocation test must extract into a Korean-character path, execute the relocated `--self-test`, and preserve a separate sentinel original outside the extraction directory. This is an automated runner proof only; it does not test Win10/11 on a buyer machine.

## 3. Help, support and failure handling proposal (unapproved commercial terms)
- `SOURCE_UNAVAILABLE` / `HOLD`: no official publisher authentication or missing licensed stock data. Explain data limitation rather than telling the customer to retry with a bypass.
- `NO_TRAIN`: sample/lag/group split invalid or prediction unsupported. Do not offer an 'AI accuracy' guarantee or forced model train.
- `OUTPUT_EXISTS_NO_OVERWRITE`: choose a **new file name and empty folder**; do not delete prior analysis or overwrite reports automatically.
- `VERIFY_RECEIPT_HASH_MISMATCH`: treat export as untrusted; keep original files, don't rewrite receipt or mark the financial report verified.
- `403/429` SEC or DART status denial: stop, respect provider quotas and use properly licensed customer file inputs. Never bypass or hide the denial.
- Support tickets should request **version/commit SHA, exact command flags minus identifiers, error code and a synthetic reproduction**. Do not ask for API keys, raw statements, customer account numbers, screenshots with sensitive content or private data to be uploaded to chat/email.

## 4. Data rights, source notices and distribution audit
| Component / data | Known use | Commercial distribution gate |
|---|---|---|
| Python stdlib, Decimal, SQLite | local arithmetic and program logic | validate Python and bundled DLL notices before executable shipping |
| scipy / scikit-learn | stats/ML regression and optional evaluation | audit exact installed package versions, transitive dependencies, licenses/NOTICE from produced executable |
| ReportLab | PDF generation | review exact bundled library license, fonts and embedded assets |
| PyInstaller / bootloader | frozen unsigned staging EXE | confirm bootloader and all dynamic libraries NOTICE and distribution terms |
| SEC original numeric facts | lawful cited computations | separate authored prose/figures, filing authentication, fair-access/robots and redistribution rights |
| KR OpenDART | authorized company filing access | specific API key/account terms, rights and commercial cache/redistribution limits |
| Nasdaq/KRX/Massive | market index/price data | **NOT LICENSED FOR PRODUCT BUNDLING** until contractual verification |
No final LICENSE/NOTICE collection, publisher authentication, market-data contract, lawyer opinion or commercial consent has been accepted. Do not market the product on the strength of this document.

## 5. Remaining customer delivery acceptance (all pending)
- Independent lawful US **and** KR real filing end-to-end, publisher/source identities, fiscal revisions, taxonomy and rights proof.
- Real customer Windows 10/11 no-Python tests, interactive GUI rendering, installed fonts and Korean PDF legibility, SmartScreen/Defender, full upgrade/uninstall with unrelated files preserved.
- Installer/ZIP checksum and reproducibility, full third-party binary NOTICE, license review, customer-facing Korean tutorial/manual with confirmed screenshots and customer feedback.
- Legal/investment-advice scope and advertising compliance, refund policy/seller obligations, price and support promise acceptance, owner's explicit `SALE GO`.
- OS/process-level IAM and no-egress for any real institution private files. Existing local gateway/disabled optional external call is not such a security guarantee.

## 6. Acceptance principle
The P85 target can only refer to a **bounded, provisional internal engineering scope**, not 85% of legal sale readiness or consumer release. Exact source SHA, CI run, both OS test count, executable/ZIP steps and remaining gates must be recorded in `docs/P85_ACCEPTANCE_EVIDENCE_20261113.md`. Final credit to D8, if any, is solely for this explicit owner fulfillment and support plan, not for actual buyers or licenses. Preserve existing `RELEASE HOLD` and do not merge to main without explicit release approval.
