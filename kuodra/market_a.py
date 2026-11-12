"""Synthetic-only local market-vs-benchmark math, never a licensed feed.

All real price/index datasets remain gated by independent commercial-use
clearance. This module intentionally refuses real/unverified series; it is an
engineering calculation demonstration, not a backtest or investing signal.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal, InvalidOperation
from kuodra.contracts import parse_date


def _series(rows: list[dict]) -> list[tuple[date, Decimal]]:
    if type(rows) is not list or not 6 <= len(rows) <= 300:
        raise ValueError('A_SAMPLE_COUNT_INVALID')
    out=[]
    for row in rows:
        if type(row) is not dict or set(row)!={'date','close'}:
            raise ValueError('A_SERIES_SCHEMA_INVALID')
        d=parse_date(row['date'])
        v=row['close']
        if type(v) is not str:
            raise ValueError('A_PRICE_STRING_REQUIRED')
        try:
            x=Decimal(v)
        except (InvalidOperation,ValueError) as exc:
            raise ValueError('A_PRICE_INVALID') from exc
        if not x.is_finite() or x<=0 or x>Decimal('1000000000000'):
            raise ValueError('A_PRICE_INVALID')
        if out and out[-1][0]>=d:
            raise ValueError('A_DATES_NOT_STRICT_ASCENDING')
        out.append((d,x))
    return out


def evaluate_synthetic_market_a(stock: list[dict], benchmark: list[dict], *,
                                stock_label: str='SYNTHETIC_STOCK',
                                benchmark_label: str='SYNTHETIC_INDEX',
                                use_mode: str='SYNTHETIC_TEST_ONLY') -> dict:
    if use_mode != 'SYNTHETIC_TEST_ONLY' or stock_label!='SYNTHETIC_STOCK' or benchmark_label!='SYNTHETIC_INDEX':
        raise ValueError('A_UNLICENSED_MARKET_DATA_DENIED')
    a,b=_series(stock),_series(benchmark)
    if [d for d,_ in a]!=[d for d,_ in b]:
        raise ValueError('A_MARKET_CALENDAR_MISMATCH')
    stock_rets=[a[i][1]/a[i-1][1]-1 for i in range(1,len(a))]
    market_rets=[b[i][1]/b[i-1][1]-1 for i in range(1,len(b))]
    n=len(market_rets)
    smean=sum(stock_rets)/n;mmean=sum(market_rets)/n
    cov=sum((x-smean)*(y-mmean) for x,y in zip(stock_rets,market_rets))/n
    var=sum((y-mmean)**2 for y in market_rets)/n
    beta=None if var==0 else cov/var
    def num(x):return None if x is None else str(x.quantize(Decimal('0.000001')))
    return {'schema':'kuodra.synthetic-engine-a.v1','status':'SYNTHETIC_DESCRIPTIVE_ONLY',
            'guard':'HOLD','trade_executed':False,'licensed_market_data_used':False,
            'stock_label':stock_label,'benchmark_label':benchmark_label,
            'sample_returns':n,'first_date':a[0][0].isoformat(),'last_date':a[-1][0].isoformat(),
            'stock_total_return':num(a[-1][1]/a[0][1]-1),
            'benchmark_total_return':num(b[-1][1]/b[0][1]-1),
            'simple_relative_delta':num(a[-1][1]/a[0][1]-b[-1][1]/b[0][1]),
            'beta':num(beta),
            'limitations':['Synthetic values only, not a company or licensed index',
                           'No historical alpha claim, investor suitability or forecast',
                           'Real market data requires separate verified commercial licence']}
