"""Fail-closed synthetic issuer/time held-out evaluation; never a stock forecast.

No private rows, ticker identity, or observed test labels leave the process.
A synthetic evaluation score is *not* evidence of real market prediction.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re

_SCHEMA = 'kuodra.synthetic-heldout.v1'
_NUMBER = re.compile(r'-?(?:0|[1-9][0-9]{0,8})(?:\.[0-9]{1,6})?\Z')
_ID = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,31}\Z')
_ROW_KEYS = {'issuer_id', 'observed_at', 'released_at', 'split', 'feature', 'target'}


def _day(value: object) -> date:
    if type(value) is not str or not re.fullmatch(r'\d{4}-\d\d-\d\d', value):
        raise ValueError('HELDOUT_DATE_INVALID')
    try:
        d = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError('HELDOUT_DATE_INVALID') from exc
    if d.isoformat() != value:
        raise ValueError('HELDOUT_DATE_INVALID')
    return d


def _num(value: object) -> Decimal:
    if type(value) is not str or not _NUMBER.fullmatch(value):
        raise ValueError('HELDOUT_NUMBER_INVALID')
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError('HELDOUT_NUMBER_INVALID') from exc


def _metric(predictions: list[Decimal], truth: list[Decimal]) -> tuple[str, str]:
    if len(predictions) != len(truth) or not truth:
        raise ValueError('HELDOUT_METRIC_INVALID')
    n = Decimal(len(truth))
    diffs = [p - t for p, t in zip(predictions, truth)]
    mae = sum((abs(x) for x in diffs), Decimal(0)) / n
    rmse = (sum((x*x for x in diffs), Decimal(0)) / n).sqrt()
    return format(mae.quantize(Decimal('0.0001')), 'f'), format(rmse.quantize(Decimal('0.0001')), 'f')


def evaluate_synthetic_heldout(raw: bytes, *, as_of: str, owner_consent: bool) -> dict:
    if owner_consent is not True:
        raise ValueError('HELDOUT_OWNER_CONSENT_REQUIRED')
    if type(raw) is not bytes or not 0 < len(raw) <= 150_000:
        raise ValueError('HELDOUT_INPUT_SIZE_INVALID')
    cutoff = _day(as_of)
    try:
        def strict_pairs(pairs):
            out = {}
            for k, v in pairs:
                if k in out:
                    raise ValueError('HELDOUT_DUPLICATE_JSON_KEY')
                out[k] = v
            return out
        payload = json.loads(raw.decode('utf-8', errors='strict'), object_pairs_hook=strict_pairs)
    except (UnicodeError, ValueError) as exc:
        raise ValueError('HELDOUT_JSON_INVALID') from exc
    if (type(payload) is not dict or set(payload) != {'schema', 'mode', 'rows'}
            or payload['schema'] != _SCHEMA or payload['mode'] != 'SYNTHETIC_TEST_ONLY'
            or type(payload['rows']) is not list or not 1 <= len(payload['rows']) <= 1000):
        raise ValueError('HELDOUT_SYNTHETIC_CONTRACT_REQUIRED')
    train, test, seen = [], [], set()
    for row in payload['rows']:
        if type(row) is not dict or set(row) != _ROW_KEYS:
            raise ValueError('HELDOUT_ROW_FIELDS_INVALID')
        issuer = row['issuer_id']
        if type(issuer) is not str or not _ID.fullmatch(issuer):
            raise ValueError('HELDOUT_ISSUER_INVALID')
        t, released = _day(row['observed_at']), _day(row['released_at'])
        if t > released or released > cutoff:
            raise ValueError('HELDOUT_AS_OF_LEAKAGE')
        split = row['split']
        if split not in ('train', 'test'):
            raise ValueError('HELDOUT_SPLIT_INVALID')
        key = (issuer, t)
        if key in seen:
            raise ValueError('HELDOUT_DUPLICATE_OBSERVATION')
        seen.add(key)
        item = (issuer, t, released, _num(row['feature']), _num(row['target']))
        (train if split == 'train' else test).append(item)
    if len(train) < 20 or len(test) < 8:
        return {'schema': 'kuodra.heldout-result.v1', 'status': 'NO_TRAIN_INSUFFICIENT_SAMPLES',
                'guard': 'HOLD', 'model_trained': False, 'prediction_claim': False,
                'raw_rows_exported': False, 'input_sha256': sha256(raw).hexdigest(),
                'training_n': len(train), 'test_n': len(test)}
    if {r[0] for r in train} & {r[0] for r in test}:
        raise ValueError('HELDOUT_ISSUER_LEAKAGE')
    if max(r[2] for r in train) >= min(r[1] for r in test):
        raise ValueError('HELDOUT_TIME_LEAKAGE')
    n = Decimal(len(train))
    mean_x = sum((r[3] for r in train), Decimal(0)) / n
    mean_y = sum((r[4] for r in train), Decimal(0)) / n
    variance = sum(((r[3]-mean_x)**2 for r in train), Decimal(0))
    if variance == 0:
        return {'schema': 'kuodra.heldout-result.v1', 'status': 'NO_TRAIN_CONSTANT_FEATURE',
                'guard': 'HOLD', 'model_trained': False, 'prediction_claim': False,
                'raw_rows_exported': False, 'input_sha256': sha256(raw).hexdigest(),
                'training_n': len(train), 'test_n': len(test)}
    covariance = sum(((r[3]-mean_x)*(r[4]-mean_y) for r in train), Decimal(0))
    slope = covariance/(variance + n)  # regularized linear baseline, train only
    intercept = mean_y - slope*mean_x
    labels = [r[4] for r in test]
    evaluated = _metric([intercept+slope*r[3] for r in test], labels)
    dummy = _metric([mean_y for _ in test], labels)
    return {'schema': 'kuodra.heldout-result.v1',
            'status': 'EVALUATED_SYNTHETIC_ONLY', 'guard': 'HOLD',
            'training_n': len(train), 'test_n': len(test),
            'issuer_group_disjoint': True, 'time_release_disjoint': True,
            'algorithm': 'regularized_one_feature_linear_vs_train_mean_dummy',
            'model_mae': evaluated[0], 'model_rmse': evaluated[1],
            'dummy_mae': dummy[0], 'dummy_rmse': dummy[1],
            'input_sha256': sha256(raw).hexdigest(),
            'model_trained': True, 'raw_rows_exported': False,
            'prediction_claim': False, 'market_performance_verified': False}
