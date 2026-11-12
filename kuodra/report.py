"""Escaped offline HTML report and atomic no-overwrite artifact saver."""
from __future__ import annotations
from decimal import Decimal
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import os
import re


def render_html(report:dict)->str:
    if report.get('schema')!='kuodra.offline-review.v1':raise ValueError('REPORT_SCHEMA_INVALID')
    e=lambda x:escape(str(x),quote=True)
    rows=''.join('<tr><td>'+e(o['fiscal_end'])+'</td><td>'+e(o['metric'])+'</td><td>'+e(o['amount'])+'</td><td>'+e(o['source'])+'</td></tr>' for o in report['evidence'])
    cards=''.join('<article><h3>'+e(f['name'])+'</h3><p><code>'+e(f['formula'])+'</code></p><strong>'+e(f['value'])+' '+e(f['unit'])+'</strong><p>'+e(f['explain'])+'</p></article>' for f in report['findings'])
    chart_metric='revenue' if any(r['metric']=='revenue' for r in report['evidence']) else 'net_income'
    vals=[(r['fiscal_end'],Decimal(r['amount'])) for r in report['evidence'] if r['metric']==chart_metric]
    vals=sorted(vals,key=lambda x:x[0])
    vmax=max((abs(n) for _,n in vals),default=Decimal('1')) or Decimal('1')
    bars=''.join('<div class="bar"><span>'+e(year)+'</span><div class="track"><div style="width:'+str(round(float(abs(n)/vmax)*100,1))+'%"></div></div><span>'+e(n)+' '+e(report['currency'])+'</span></div>' for year,n in vals)
    chart_title='Annual '+chart_metric+' (same metric and currency; synthetic test data)'
    warnings=''.join('<li>'+e(x)+'</li>' for x in report['warnings'])
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KUODRA offline evidence report</title><style>body{font:16px system-ui;background:#101722;color:#edf0f7;max-width:1050px;margin:36px auto;padding:16px}h1{font-size:30px}small,.muted{color:#a7b4c9}article{display:inline-block;vertical-align:top;min-width:220px;max-width:300px;padding:18px;margin:6px;background:#202b3c;border-radius:12px}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #33445a;text-align:left}.bar{display:flex;gap:15px;align-items:center;padding:6px 0}.bar span{width:180px}.track{flex:1;background:#33445a;height:14px;border-radius:8px}.track div{height:100%;background:#5f9dea;border-radius:8px}code{font-size:12px;color:#9acbfa}mark{background:#ffcc66;padding:4px 8px;border-radius:6px}</style><h1>KUODRA | Corporate evidence</h1><p><mark>HOLD — unverified local source</mark></p><p>'''+e(report['country'])+' / '+e(report['issuer_id'])+' / '+e(report['statement'])+' / '+e(report['as_of'])+'''</p><h2>Available engine findings</h2>'''+cards+'''<h2>'''+e(chart_title)+'''</h2>'''+bars+'''<h2>Local source observations</h2><table><thead><tr><th>Fiscal end</th><th>Metric</th><th>Value</th><th>Receipt</th></tr></thead><tbody>'''+rows+'''</tbody></table><h2>Limitations</h2><ul>'''+warnings+'''</ul><p class="muted">A: '''+e(report['engine_a'])+' | C: '+e(report['engine_c'])+' | ML: '+e(report['ml'])+'''</p><small>Offline synthetically tested interface. No investment advice, no live quote, no SEC/DART publisher authentication. See matching JSON for source hashes.</small></html>'''


def export_local(report:dict,output_dir:Path,stem:str='review')->dict:
    if type(stem) is not str or not re.fullmatch('[A-Za-z0-9_-]{1,48}',stem):raise ValueError('OUTPUT_STEM_INVALID')
    root=Path(output_dir)
    if not root.exists() or not root.is_dir() or root.is_symlink():raise ValueError('OUTPUT_DIRECTORY_INVALID')
    data=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    html=render_html(report).encode('utf-8')
    files={'json':data,'html':html}
    paths={ext:root/(stem+'.'+ext) for ext in files}
    if any(p.exists() or p.is_symlink() for p in paths.values()):raise FileExistsError('OUTPUT_EXISTS_NO_OVERWRITE')
    created=[]
    try:
        for ext,bytes_ in files.items():
            fd=os.open(paths[ext],os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            created.append(paths[ext])
            with os.fdopen(fd,'wb') as f:
                f.write(bytes_)
                f.flush();os.fsync(f.fileno())
    except Exception:
        for p in created:
            try:p.unlink(missing_ok=True)
            except OSError:pass
        raise
    return {ext:{'path':str(paths[ext]),'sha256':sha256(data_).hexdigest()} for ext,data_ in files.items()}
