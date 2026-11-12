# KUODRA P95 external-source, customer delivery and rights acceptance gates
**2026-11-13 KST · plan + independently actionable test criteria, not an approval**

## Decision and implementation routes
**Option A — local/BYOK single-shot official access (chosen for P95 candidate):** Each owner voluntarily supplies a lawful SEC contact User-Agent or their own OpenDART API key in an environment variable. A bounded, allowlisted one-shot GET is consumed in memory; issuer and accounting context are validated by the existing local A/B/C/B-Guard pipeline. No mandatory server/billing, no credential storage, no cross-customer data pooling and no quote reselling.

**Option B — vendor-hosted aggregator/SaaS (deferred):** Convenient common updates, but vendor stores customer access, assumes price/index/data redistribution obligations, incurs ongoing hosting and breach/availability risk, and needs new owner consent plus security/finance compliance. Not authorized.

**Windows delivery A — unsigned portable ZIP (staging only, chosen for engineering):** CI can build and execute without Python and compare exact file SHA after Korean-path extraction. Cannot assure genuine vendor signature, antivirus acceptance, install/upgrade/uninstall or Windows 10/11 customer use. **B — signed installer with clean-machine rollback** is required for release but blocked pending certificate/installation, third-party NOTICE and real customer test.

## Implemented candidate scope (merge status and CI results must be checked)
- Local SEC CompanyFacts-shaped source accepts **up to 10 MB** in CLI/GUI, matching the parser limit; KR full annual DART remains bounded to 1 MB in offline file mode. Both continue to reject links, altered source scope, non-authorized inputs and output overwrite.
- Opted-in official gateway `kuodra.official_review.analyze_opted_in_once` uses `build_sec_request` / `build_dart_request`, fixed HTTPS allowlist, issuer ID and requested year checks, 403/429/status-denial with no bypass/retries, no API key in output. This is not publisher attestation or commercial data licensing. Default existing GUI and offline CLI **never fetch remotely**.
- Optional Python CLI `python -m kuodra.official_cli` accesses only a provider after `--consent`. It uses locally configured environment variables, never includes a key in argument flags, logs or output. The unsigned Windows onedir source originally includes offline-only entrypoint; availability of official mode in an executable must be independently proved before marketing it as a customer feature.
- Windows portable staging `kuodra.portable_manifest` records exact bytes and file inventory as an **unsigned** manifest; a relocated ZIP must match and still present `consumer_release_approved=false`. Matching a SHA is not producer authentication.
- Selected dependency ledger `kuodra.dependency_ledger` prints exact installed runtime versions and extracted LICENSE hints with `commercial_distribution_approved=false`. It is **not** a comprehensive SBOM for transitive DLLs and not a substitute for full NOTICE license review.
- GUI controller: read-only source, local HTML/JSON/PDF opt-in with evidence receipt, verify report, visible Guard HOLD, no automatic provider calls; visual cross-platform customer acceptance is outstanding.

## How owner can later test actual sources without exposing secrets
**No real credentials have been obtained or used by the assistant. Do not paste secret tokens into a chat or GitHub.**

US source: user locally sets `KUODRA_SEC_USER_AGENT` to an **honest, identifying contact** accepted by SEC and runs:
```text
python -m kuodra.official_cli --country US --issuer-id 0000320193 --as-of YYYY-MM-DD --output-dir <existing-empty-folder> --name us-demo --consent
```
KR source: user obtains own lawfully issued OpenDART key, stores it in local `KUODRA_DART_API_KEY`, and runs:
```text
python -m kuodra.official_cli --country KR --issuer-id <official-8-digit-corp-code> --business-year 2024 --as-of YYYY-MM-DD --output-dir <existing-empty-folder> --name kr-demo --consent
```
- Both workflows are one explicit request and output local HOLD, even if source geometry parses. Do not treat successful HTTPS as publisher or commercial use authorization. CLI commands are examples to be run **only when** the owner approves service contact and provides lawful credentials on their own machine. No owner contact was invented; do not auto-fill.
- If official data exceeds the bounded parser budget, source is unsupported: use rights-held **local file** after explicit size/code review, not bypass/hidden retries.
- Provider may return 403/429/status 013: stop. An absent DART key is a real product limitation, not a test failure that can be fixed by faking data.
- Record exact CIK/corp_code, fiscal period, filing accession/rcept_no, selected account metrics, amount/currency, published-vs-observed date and unique source hash. Validate with official human-readable filing and correct IFRS/US-GAAP taxonomy on real companies; no prediction claims.
- Never publish/download bundled original filings, private licensed quotes, user secrets or customer files in the GitHub repository.

## Official source/rights references (access is not a blanket redistribution license)
- SEC CompanyFacts and submissions JSON: https://www.sec.gov/search-filings/edgar-application-programming-interfaces — no API key, source metadata, XBRL facts; fair-access and actual issuer contents remain constraints.
- SEC fair-access policy: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data — verified User-Agent, throttle, no 403/429 circumvention.
- DART `fnlttSinglAcntAll` request/response contract: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020 — 40-character key, corp_code, year, report/financial scope, currency, receipt, account ID, actual period.
- DART terms: https://opendart.fss.or.kr/intro/terms.do — provider terms and third-party data rights need case-specific review.
- American copyright facts vs authored prose: https://www.copyright.gov/help/faq/faq-general.html . Company source numbers may support independent analysis, but long written passages/graphics and commercial benchmark data remain rights-controlled.
- KRX/Nasdaq/Massive/S&P market/index redistribution for proprietary price/benchmark series: separate contract and product terms; never infer a right from the API's being viewable in a browser.

## Mandatory acceptance before P95 or public consumer release
| Gate | Current evidence | Remaining requirement |
|---|---|---|
| SEC actual company E2E | Official contract and simulated transport covered; live authentic source **not tested** | Lawful real CompanyFacts, identity, published/account/years, human cross-check + source/terms |
| DART actual company E2E | Official documented field schema; simulated 40-char key and status covered | Own API key + live request, real 8-digit corp_code/year/revisions, terms/redistribution |
| Sector / licensed stock data | A synthetic-only, B source-linked, C descriptive | Verifiable lawful price/index rights or explicit A=UNAVAILABLE; real peer business model |
| Private data OS protection | read-only bounded helpers and negative file tests | Windows process/no-egress, owner ACL, malicious document sandbox proof |
| Consumer Windows | Hosted Windows runner PyInstaller + extracted ZIP staging | Real Win10/11 buyer, interactive GUI, Korean fonts, AV/SmartScreen, upgrades, uninstaller, no loss |
| License and legal | Selected runtime dependency hints, no signed executable | Full transitive LICENSE/NOTICE; finance law, privacy, refund/help, price and vendor rights |
| Release | source SHA & staging check, Guard HOLD | Owner go-live approval, signed/distributable package hash and buyer acceptance |
**No P95 final-acceptance claim is legitimate while any relevant hard gate above remains unverified.** Preserve old KIC source and original submissions, keep commercial `RELEASE HOLD / SALE NO-GO`. Update central 85-to-new-score only if independently tested P95 partial engineering credit is defensible; never mark 95 to satisfy a target number.
