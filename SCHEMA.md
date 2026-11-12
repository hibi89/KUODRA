# KUODRA canonical financial data schema v1

Mandatory observation fields: dataset_id, entity_id (country-prefixed legal entity ID, e.g. KR_DART and US_CIK namespaces, not a guessed ticker), metric_id, observation_at, available_at, value (decimal), unit, source_id, access_level (PUBLIC/PRIVATE), evidence_sha256.

Additional contextual fields when needed: country, company_name, ticker_alias, corp_code_or_cik, fiscal_start, fiscal_end, fiscal_year, fiscal_period, report_type, statement_type, consolidation CFS/OFS, currency, K-IFRS/US-GAAP taxonomy, accession_or_rcept_no, publisher URL, source_span, revision_vintage, source_published_at, parser_version, account_map_version, permitted_purpose, dataset_owner, verified_source_identity, rights_status, group_id and feature_horizon.

**Invariants:** no cross-issuer merge by ticker alone; do not mix CFS/OFS, units, currencies, FY vs YTD or periods without validated conversion; available_at <= analysis as_of; observation_at <= available_at; source receipt + revision preserved; amendment never backdated. Missing data is null/unavailable, never silently zero or filled forward. Authorization to process PRIVATE is per owner and is not implied by uniform schema.

Trust zones: PUBLIC approved data gateway may fetch only allowlisted official source under quota; PRIVATE customer source is owner-readonly and no outbound private data by default. Explicit permission required to locally join; derived outputs inherit the most restrictive source access. The SHA of local bytes does not prove official origin or licensed redistribution.

Report contract: request_id, entity/country/fiscal period/as_of, input_receipts[], canonical_version, engine_findings[{A|B|C, status, metrics, formula, evidence, caveats}], ml{status, sample, baseline, heldout, evaluation}, guard{decision, reasons, policy}, human_review, exported_at, export_sha256. Guard APPROVE only means report review eligible, never trade approval.
