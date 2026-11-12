"""Strict interoperability with the original KIC canonical numeric core.

The raw file is unverified; canonicalizing data does not authenticate a filing,
transfer commercial rights, or grant Guard investment approval.
"""
from __future__ import annotations

import csv
from io import StringIO
from hashlib import sha256
from kuodra.contracts import Observation, parse_date
from proofinvest.kuodra_unified_core import normalize_local_csv

_HEADER = ("entity_id", "metric_id", "observation_at", "available_at", "value", "unit")


def normalize_observations_via_kic(records: list[Observation], *, as_of: str) -> dict:
    if type(records) is not list or not 1 <= len(records) <= 5000:
        raise ValueError("KIC_BRIDGE_RECORD_COUNT_INVALID")
    cutoff = parse_date(as_of)
    if any(type(r) is not Observation for r in records):
        raise ValueError("KIC_BRIDGE_RECORD_TYPE_INVALID")
    ids = {(r.country, r.issuer_id, r.statement, r.unit, r.source_sha256) for r in records}
    if len(ids) != 1:
        raise ValueError("KIC_BRIDGE_MIXED_SOURCE_SCOPE_DENIED")
    country, issuer_id, statement, unit, original_sha = next(iter(ids))
    if any(parse_date(r.fiscal_end) > parse_date(r.available_at) or
           parse_date(r.available_at) > cutoff for r in records):
        raise ValueError("KIC_BRIDGE_FUTURE_RELEASE_DENIED")
    out = StringIO(newline="")
    w = csv.writer(out, lineterminator="\n")
    w.writerow(_HEADER)
    for r in sorted(records, key=lambda x: (x.fiscal_end, x.metric)):
        w.writerow((f"{country}_{issuer_id}", r.metric,
                    r.fiscal_end + "T00:00:00Z", r.available_at + "T00:00:00Z",
                    str(r.value), unit))
    raw = out.getvalue().encode("utf-8")
    dataset = normalize_local_csv(raw,
                                  dataset_id=f"local{country}{original_sha[:16]}",
                                  source_id=f"file{original_sha[:16]}",
                                  access_level="PRIVATE", consent=True)
    if dataset.get("rows") != len(records):
        raise ValueError("KIC_BRIDGE_ROW_LOSS")
    return {
        "canonical": dataset,
        "original_source_sha256": original_sha,
        "original_country": country,
        "original_issuer_id": issuer_id,
        "statement": statement,
        "canonical_input_sha256": sha256(raw).hexdigest(),
        "publisher_authenticated": False,
        "commercial_rights_verified": False,
        "guard": "HOLD",
    }
