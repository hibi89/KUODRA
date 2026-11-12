"""Optional bounded, legible PDF evidence export (ReportLab).

English/ASCII first-party labels only. Non-ASCII customer annotations are
refused until licensed embedded Unicode font support is accepted for Windows.
No live market feed and no silent conversion of unverified files to verified.
"""
from __future__ import annotations
from io import BytesIO
from decimal import Decimal
from html import escape as html_escape


def render_pdf_bytes(report: dict) -> bytes:
    if type(report) is not dict or report.get('schema')!='kuodra.offline-review.v1':
        raise ValueError('PDF_REPORT_SCHEMA_INVALID')
    evidence=report.get('evidence')
    findings=report.get('findings')
    if type(evidence) is not list or type(findings) is not list or len(evidence)>100 or len(findings)>24:
        raise ValueError('PDF_REPORT_TOO_LARGE')
    # Prevent silent loss of Korean, non-ASCII issuer names/annotations, emoji.
    for field in (report.get('warnings',[]),report.get('periods',[])):
        if type(field) is not list:
            raise ValueError('PDF_CONTRACT_INVALID')
    def ascii_text(value):
        s=str(value)
        if len(s)>350 or any(ord(c)>126 or ord(c)<32 for c in s):
            raise ValueError('PDF_NON_ASCII_OR_CONTROL_REQUIRES_FONT_REVIEW')
        return html_escape(s, quote=True)
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    from reportlab.graphics.shapes import Drawing, Rect, String

    buffer=BytesIO()
    document=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=17*mm,leftMargin=17*mm,
                               topMargin=13*mm,bottomMargin=13*mm,allowSplitting=1,
                               title='KUODRA corporate evidence — local synthetic example')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Meta',parent=styles['Normal'],fontSize=9,leading=13,spaceAfter=6))
    styles.add(ParagraphStyle(name='SmallEvidence',parent=styles['Normal'],fontSize=7,leading=10))
    styles.add(ParagraphStyle(name='HoldText',parent=styles['Normal'],textColor=colors.HexColor('#8d4600'),
                              fontSize=10,leading=13,spaceAfter=5))
    flow=[]
    flow.append(Paragraph('KUODRA | Corporate evidence review',styles['Heading1']))
    flow.append(Paragraph('HOLD — UNVERIFIED LOCAL SOURCE. NO INVESTMENT ADVICE.',styles['HoldText']))
    flow.append(Paragraph('Country: %s | Entity: %s | Scope: %s | As of: %s | Currency: %s' % tuple(
        ascii_text(report.get(k,'')) for k in ('country','issuer_id','statement','as_of','currency')), styles['Meta']))
    flow.append(Paragraph('Financial findings — calculated, not authenticated',styles['Heading2']))
    if not findings:
        flow.append(Paragraph('No comparable findings were available.',styles['Meta']))
    for f in findings:
        row=[
            Paragraph('<b>'+ascii_text(f.get('name'))+'</b>',styles['SmallEvidence']),
            Paragraph(ascii_text(f.get('formula')),styles['SmallEvidence']),
            Paragraph(ascii_text(f.get('value'))+' '+ascii_text(f.get('unit')),styles['SmallEvidence']),
        ]
        table=Table([row],colWidths=[42*mm,88*mm,44*mm],hAlign='LEFT')
        table.setStyle(TableStyle([
          ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#eaf1fc')),
          ('BOX',(0,0),(-1,-1),0.4,colors.HexColor('#b9c7d9')),
          ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ]))
        flow.append(KeepTogether([table,Spacer(1,2*mm)]))
    flags=report.get('financial_flags',[])
    if flags:
        flow.append(Paragraph('Financial review questions (not fraud evidence)',styles['Heading2']))
        for entry in flags:
            flow.append(Paragraph(ascii_text(entry['code'])+' — '+
                                  ascii_text(entry['explain'])+
                                  '; evidence: '+ascii_text(','.join(entry['source_refs'])),
                                  styles['SmallEvidence']))
    nums=[(r['fiscal_end'],Decimal(r['amount'])) for r in evidence if r['metric']=='revenue']
    nums.sort(key=lambda x:x[0])
    if nums:
        flow.append(Paragraph('Revenue by fiscal period (unverified source)',styles['Heading2']))
        chart=Drawing(490,max(60,25*len(nums)+5))
        vmax=max(abs(v) for _,v in nums) or Decimal(1)
        for idx,(fy,v) in enumerate(nums):
            y=chart.height-24*(idx+1)
            width=float(abs(v)/vmax)*280
            chart.add(String(0,y+2,ascii_text(fy),fontSize=9))
            chart.add(Rect(82,y,width,12,fillColor=colors.HexColor('#4c82c9'),strokeColor=None))
            chart.add(String(370,y+2,ascii_text(v)+' '+ascii_text(report['currency']),fontSize=8))
        flow.append(chart)
    flow.append(Paragraph('Source evidence (selected as of request time)',styles['Heading2']))
    rows=[[Paragraph(v,styles['SmallEvidence']) for v in ('Fiscal end','Metric','Amount','Filing reference')]]
    for r in evidence:
        rows.append([Paragraph(ascii_text(r.get(k,'')),styles['SmallEvidence'])
                     for k in ('fiscal_end','metric','amount','source')])
    t=Table(rows,colWidths=[29*mm,42*mm,36*mm,67*mm],repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dde7f5')),
         ('LINEBELOW',(0,0),(-1,-1),0.35,colors.HexColor('#d0d7df')),
         ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    flow.append(t)
    peers=report.get('peer_comparison',{})
    if peers:
        flow.append(Paragraph('Peer comparisons (descriptive, NOT authenticated)',styles['Heading2']))
        for item in peers.get('comparisons',[]):
            for name,delta in item['deltas'].items():
                flow.append(Paragraph('Peer '+ascii_text(item['issuer_id'])+' | '+ascii_text(name)+' | delta '+ascii_text(delta),styles['SmallEvidence']))
    if report.get('synthetic_market_a'):
        market=report['synthetic_market_a']
        flow.append(Paragraph('Synthetic price/index demonstration only',styles['Heading2']))
        flow.append(Paragraph('Stock '+ascii_text(market['stock_total_return'])+' / benchmark '+ascii_text(market['benchmark_total_return'])+' / beta '+ascii_text(market['beta']),styles['SmallEvidence']))
    stats=report.get('exploratory_statistics')
    if stats:
        flow.append(Paragraph('Owner-local exploratory FDR (not a prediction)',styles['Heading2']))
        flow.append(Paragraph('Status: '+ascii_text(stats['status'])+'; guard HOLD; model trained false.',styles['SmallEvidence']))
        for item in stats.get('insights',[]):
            flow.append(Paragraph(ascii_text(item['metric_a'])+' / '+ascii_text(item['metric_b'])+
                                  ' | paired '+ascii_text(item['paired_n'])+
                                  ' | r '+ascii_text(item['pearson_r'])+
                                  ' | adjusted q '+ascii_text(item['q_bh_fdr']),styles['SmallEvidence']))
    heldout=report.get('synthetic_heldout')
    if heldout:
        flow.append(Paragraph('Synthetic group/time holdout — NOT a real market forecast',styles['Heading2']))
        flow.append(Paragraph('Status: '+ascii_text(heldout['status'])+' | Guard HOLD | issuer/time leakage checked',styles['SmallEvidence']))
        if heldout['status']=='EVALUATED_SYNTHETIC_ONLY':
            flow.append(Paragraph('Model MAE '+ascii_text(heldout['model_mae'])+' / Dummy MAE '+ascii_text(heldout['dummy_mae'])+
                                  ' | model RMSE '+ascii_text(heldout['model_rmse'])+' / Dummy RMSE '+ascii_text(heldout['dummy_rmse']),styles['SmallEvidence']))
    rev=report.get('revision_audit',[])
    if rev:
        flow.append(Paragraph('As-of filing revisions (latest dated filing selected)',styles['Heading2']))
        for entry in rev:
            flow.append(Paragraph('%s %s: %s; %s earlier candidate(s), amount changed: %s' % (
                ascii_text(entry['fiscal_end']),ascii_text(entry['metric']),
                ascii_text(entry['chosen_source']),len(entry['superseded']),
                ascii_text(entry['revised_amount'])),styles['SmallEvidence']))
    flow.append(Spacer(1,1*mm))
    flow.append(Paragraph('Guard, rights and limits',styles['Heading2']))
    for w in report.get('warnings',[]):
        flow.append(Paragraph('- '+ascii_text(w),styles['Meta']))
    flow.append(Paragraph('Market A: %s | Peer C: %s | ML: %s' % tuple(
        ascii_text(report.get(k)) for k in ('engine_a','engine_c','ml')), styles['Meta']))
    flow.append(Paragraph('All publisher authenticity and rights remain UNVERIFIED. Input data is local. Trade executed: false.',styles['SmallEvidence']))
    def number_footer(canvas,doc):
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor('#637388'))
        canvas.drawRightString(A4[0]-17*mm,12*mm,f'KUODRA local evidence | page {doc.page}')
    document.build(flow,onFirstPage=number_footer,onLaterPages=number_footer)
    data=buffer.getvalue()
    if not data.startswith(b'%PDF-') or len(data)>1_000_000:
        raise ValueError('PDF_RENDER_INVALID')
    return data
