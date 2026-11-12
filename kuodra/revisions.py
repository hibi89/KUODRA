"""Offline, source-visible reconciliation of repeated financial facts.

Do not infer publisher authenticity. Choose the most recently *available*
observation as of the explicit cutoff, preserving every conflicting earlier
observation in an audit. Same-day conflicting facts fail closed because date-only
receipts cannot establish publication order.
"""
from __future__ import annotations

from collections import defaultdict
from kuodra.contracts import Observation, parse_date


def reconcile_annual_facts(candidates: list[Observation], *, as_of: str, max_candidates: int = 6000):
    cutoff = parse_date(as_of)
    if (type(candidates) is not list or not 1 <= len(candidates) <= max_candidates
            or any(type(c) is not Observation for c in candidates)):
        raise ValueError('RECONCILIATION_INPUT_INVALID')
    groups: dict[tuple, list[Observation]] = defaultdict(list)
    for r in candidates:
        if parse_date(r.available_at) > cutoff:
            raise ValueError('RECONCILIATION_FUTURE_INPUT')
        groups[(r.country, r.issuer_id, r.statement, r.metric, r.fiscal_end, r.unit)].append(r)
    result, audit = [], []
    for key, all_rows in sorted(groups.items()):
        # Within a day the official JSON extracts contain only filing dates;
        # two distinct numeric values cannot be sequenced deterministically.
        days: dict[str, list[Observation]] = defaultdict(list)
        for r in all_rows:
            days[r.available_at].append(r)
        for day, day_rows in days.items():
            if len({r.value for r in day_rows}) != 1:
                raise ValueError('RECONCILIATION_SAME_DAY_CONFLICT')
        latest_day = max(days)
        latest = sorted(days[latest_day], key=lambda r:r.source_ref)[0]
        result.append(latest)
        distinct_values = {r.value for r in all_rows}
        if len(all_rows) > 1:
            audit.append({
                'metric': latest.metric,
                'fiscal_end': latest.fiscal_end,
                'chosen_filed_at': latest.available_at,
                'chosen_source': latest.source_ref,
                'candidate_count': len(all_rows),
                'revised_amount': len(distinct_values) > 1,
                'superseded': [
                    {'filed_at': r.available_at, 'source': r.source_ref, 'amount': str(r.value)}
                    for r in sorted(all_rows, key=lambda x:(x.available_at, x.source_ref))
                    if r is not latest
                ],
                'publisher_authenticated': False,
            })
    return result, sorted(audit, key=lambda a:(a['fiscal_end'],a['metric']))
