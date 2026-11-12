"""Deterministic financial B + evidence Guard for locally supplied facts."""
from __future__ import annotations
from decimal import Decimal
from kuodra.contracts import Observation, parse_date


def _f(x:Decimal)->str:
    return format(x,'f')

def build_review(records:list[Observation],*,as_of:str):
    cutoff=parse_date(as_of)
    if not isinstance(records,list) or not records or any(not isinstance(x,Observation) for x in records):
        raise ValueError('REVIEW_RECORDS_INVALID')
    identity={(r.country,r.issuer_id,r.statement,r.unit) for r in records}
    if len(identity)!=1:raise ValueError('REVIEW_SCOPE_MISMATCH')
    country,issuer_id,statement,unit=identity.pop()
    eligible=[r for r in records if parse_date(r.available_at)<=cutoff]
    if not eligible:raise ValueError('FUTURE_ONLY_SOURCE')
    byperiod={};sources=set()
    for r in eligible:
        row=byperiod.setdefault(r.fiscal_end,{})
        if r.metric in row and row[r.metric].value!=r.value:
            raise ValueError('CONFLICTING_OBSERVATION')
        row[r.metric]=r
        sources.add(r.source_ref)
    periods=sorted(byperiod,reverse=True)
    current=byperiod[periods[0]]
    findings=[]
    def add(name,formula,inputs,val,explain):
        findings.append({'name':name,'formula':formula,'inputs':inputs,'value':_f(val),
                         'unit':unit if name=='accrual_gap' else 'ratio',
                         'explain':explain})
    ni=current.get('net_income');cfo=current.get('operating_cashflow')
    if ni and cfo:
        add('accrual_gap','NetIncome - OperatingCashFlow',('net_income','operating_cashflow'),
            ni.value-cfo.value,'Difference is a review clue, not proof of misconduct')
        if ni.value>0:
            add('cash_conversion','OperatingCashFlow / NetIncome',('operating_cashflow','net_income'),
                (cfo.value/ni.value).quantize(Decimal('0.0001')),'Operating cash versus net earnings')
    li=current.get('liabilities');eq=current.get('equity')
    if li and eq and eq.value>0:
        add('liabilities_to_equity','TotalLiabilities / Equity',('liabilities','equity'),
            (li.value/eq.value).quantize(Decimal('0.0001')),'Total liabilities; not necessarily interest-bearing debt')
    prev=byperiod[periods[1]] if len(periods)>1 else None
    if prev:
        for metric in ('revenue','receivables','inventory'):
            a,b=current.get(metric),prev.get(metric)
            if a and b and b.value>0:
                add('growth_'+metric,metric+'_current / '+metric+'_previous - 1',(metric,),
                    (a.value/b.value-1).quantize(Decimal('0.0001')),'Comparable FY changes only')
    warnings=['Publisher identity and commercial source rights are NOT attested by an uploaded file. Review is held.']
    if len(periods)<2:warnings.append('No comparable second fiscal year: growth unavailable')
    if not findings:warnings.append('Insufficient aligned financial metrics')
    # Conservative cross-period diagnostic questions, never misconduct findings.
    financial_flags=[]
    if ni and cfo and ni.value>0 and cfo.value<0:
        financial_flags.append({'code':'PROFIT_POSITIVE_CFO_NEGATIVE',
           'status':'REVIEW_ONLY_NOT_FRAUD',
           'explain':'Positive earnings but negative operating cashflow require context and source review',
           'source_refs':sorted({ni.source_ref,cfo.source_ref})})
    if prev and current.get('revenue') and prev.get('revenue') and prev['revenue'].value>0:
        current_revenue=current['revenue']
        previous_revenue=prev['revenue']
        rev_delta=current_revenue.value/previous_revenue.value-1
        for metric,code in (('receivables','RECEIVABLES_OUTPACE_REVENUE'),
                            ('inventory','INVENTORY_OUTPACES_REVENUE')):
            c,p=current.get(metric),prev.get(metric)
            if c and p and p.value>0 and c.value/p.value-1>rev_delta:
                financial_flags.append({'code':code,'status':'REVIEW_ONLY_NOT_FRAUD',
                   'explain':metric+' percentage growth exceeds revenue growth over the same comparable fiscal years',
                   'source_refs':sorted({c.source_ref,p.source_ref,
                                         current_revenue.source_ref,previous_revenue.source_ref})})
    findings.sort(key=lambda x:x['name'])
    evidence=[{'metric':r.metric,'fiscal_end':r.fiscal_end,'available_at':r.available_at,
        'amount':_f(r.value),'source':r.source_ref,'sha256':r.source_sha256} for r in eligible]
    evidence.sort(key=lambda r:(r['fiscal_end'],r['metric'],r['source']))
    return {'schema':'kuodra.offline-review.v1','country':country,'issuer_id':issuer_id,
            'statement':statement,'currency':unit,'as_of':as_of,'periods':periods,
            'source_verified':False,'rights_verified':False,'guard':'HOLD',
            'engine_a':'UNAVAILABLE_NO_LICENSED_MARKET_DATA',
            'engine_b':'CALCULATED_UNVERIFIED_SOURCE' if findings else 'INSUFFICIENT_EVIDENCE',
            'engine_c':'UNAVAILABLE_NO_MATCHED_PEERS',
            'ml':'NO_TRAIN_NO_VALIDATED_FINANCIAL_SAMPLES',
            'findings':findings,'financial_flags':financial_flags,'evidence':evidence,'warnings':warnings,'trade_executed':False}
