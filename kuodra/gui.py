"""Offline developer UI for the synthetic/local-file MVP. Not a packaged Windows product."""
from __future__ import annotations
from pathlib import Path
from kuodra.cli import analyze_bytes
from kuodra.report import export_local
from kuodra.safe_io import read_bounded_local, source_limit_for


def run_selected(*,country:str,issuer_id:str,as_of:str,source:str,output_dir:str,name:str='review',statement:str='CFS',pdf:bool=False,language:str='en',
                 dart_fiscal_end:str|None=None,dart_scope_attested:bool=False):
    p=Path(source)
    limit=source_limit_for(country)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>limit:
        raise ValueError('SOURCE_FILE_INVALID')
    report=analyze_bytes(read_bounded_local(p,limit=limit),
                         country=country,issuer_id=issuer_id,as_of=as_of,
                         statement=statement,dart_fiscal_end=dart_fiscal_end,
                         dart_request_fs_div_bound=dart_scope_attested)
    result=export_local(report,Path(output_dir),name,pdf=pdf,html_language=language)
    return report,result


def main(*, smoke_only:bool=False):
    """Local-only desktop screen; smoke_only inspects actual Tk widgets then exits."""
    import re
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from datetime import date
    import webbrowser
    from kuodra.release_gate import verify_evidence_bundle

    BG='#0b1321'
    CARD='#172336'
    FIELD='#26354b'
    TEXT='#eef4ff'
    MUTED='#a7b8ce'
    BLUE='#4d80c9'
    WARN='#ffd390'

    root=tk.Tk()
    root.title('KUODRA | Corporate evidence verification')
    root.geometry('930x650')
    root.minsize(800,610)
    root.configure(bg=BG)

    style=ttk.Style(root)
    style.theme_use('clam')
    style.configure('Q.TFrame',background=BG)
    style.configure('QCard.TFrame',background=CARD)
    style.configure('QTitle.TLabel',background=BG,foreground=TEXT,font=('Segoe UI',22,'bold'))
    style.configure('QSubtitle.TLabel',background=BG,foreground=MUTED,font=('Segoe UI',10))
    style.configure('QBadge.TLabel',background=BG,foreground=WARN,font=('Segoe UI',11,'bold'))
    style.configure('QLabel.TLabel',background=CARD,foreground=MUTED,font=('Segoe UI',10,'bold'))
    style.configure('QCard.TLabel',background=CARD,foreground=TEXT,font=('Segoe UI',10))
    style.configure('QStatus.TLabel',background=BG,foreground=WARN,font=('Segoe UI',10,'bold'))
    style.configure('QEntry.TEntry',font=('Segoe UI',10),fieldbackground=FIELD,
                    foreground=TEXT,insertcolor=TEXT,borderwidth=1,padding=7)
    style.configure('QSelect.TCombobox',font=('Segoe UI',10),fieldbackground=FIELD,
                    foreground=TEXT,background=FIELD,padding=6)
    style.map('QSelect.TCombobox',fieldbackground=[('readonly',FIELD)],
              foreground=[('readonly',TEXT)])
    style.configure('QButton.TButton',font=('Segoe UI',10),padding=(12,8),
                    foreground=TEXT,background='#2c4260',borderwidth=0)
    style.map('QButton.TButton',background=[('active','#3c5b83')])
    style.configure('QPrimary.TButton',font=('Segoe UI',10,'bold'),padding=(15,9),
                    foreground='white',background=BLUE,borderwidth=0)
    style.map('QPrimary.TButton',background=[('active','#6498e6')])
    style.configure('QCheck.TCheckbutton',background=CARD,foreground=TEXT,
                    font=('Segoe UI',10))
    style.map('QCheck.TCheckbutton',background=[('active',CARD)],
              foreground=[('active',TEXT)])

    # Keep critical actions reachable on smaller laptop screens. Unlike a
    # fixed-height form, the complete interface can scroll without clipping.
    host=ttk.Frame(root,style='Q.TFrame')
    host.pack(fill='both',expand=True)
    canvas=tk.Canvas(host,bg=BG,borderwidth=0,highlightthickness=0)
    scroll=ttk.Scrollbar(host,orient='vertical',command=canvas.yview)
    canvas.configure(yscrollcommand=scroll.set)
    scroll.pack(side='right',fill='y')
    canvas.pack(side='left',fill='both',expand=True)
    container=ttk.Frame(canvas,style='Q.TFrame',padding=(28,22))
    canvas_item=canvas.create_window((0,0),window=container,anchor='nw')
    def update_scroll_region(_event=None):
        bounds=canvas.bbox('all')
        if bounds:
            canvas.configure(scrollregion=bounds)
    def update_canvas_width(event):
        canvas.itemconfigure(canvas_item,width=event.width)
    container.bind('<Configure>',update_scroll_region)
    canvas.bind('<Configure>',update_canvas_width)
    def on_wheel(event):
        delta=getattr(event,'delta',0)
        if delta:
            canvas.yview_scroll(-int(delta/abs(delta)),'units')
    root.bind('<MouseWheel>',on_wheel)
    header=ttk.Frame(container,style='Q.TFrame')
    header.pack(fill='x',pady=(0,18))
    ttk.Label(header,text='KUODRA',style='QTitle.TLabel').grid(row=0,column=0,sticky='w')
    ttk.Label(header,text='OFFLINE STAGING  ·  GUARD HOLD',
              style='QBadge.TLabel').grid(row=0,column=1,sticky='e',padx=(20,0))
    ttk.Label(header,text='KR / US corporate financial evidence verification — source first',
              style='QSubtitle.TLabel').grid(row=1,column=0,columnspan=2,sticky='w',pady=(6,0))
    header.columnconfigure(0,weight=1)

    card=ttk.Frame(container,style='QCard.TFrame',padding=(25,21))
    card.pack(fill='x')
    country=tk.StringVar(value='KR')
    issuer=tk.StringVar(value='')
    asof=tk.StringVar(value=date.today().isoformat())
    statement=tk.StringVar(value='CFS')
    src=tk.StringVar(value='')
    out=tk.StringVar(value='')
    name=tk.StringVar(value='review')
    pdf=tk.BooleanVar(value=False)
    language=tk.StringVar(value='ko')
    dart_end=tk.StringVar(value='')
    dart_scope=tk.BooleanVar(value=False)
    status=tk.StringVar(value='Source must be authorized and local. No network requests or trades.')

    def row(i,title,var,*,values=None,browse=None):
        ttk.Label(card,text=title,style='QLabel.TLabel').grid(
            row=i,column=0,sticky='w',pady=6,padx=(0,16))
        if values:
            widget=ttk.Combobox(card,textvariable=var,values=values,
                                state='readonly',width=30,style='QSelect.TCombobox')
        else:
            widget=ttk.Entry(card,textvariable=var,width=58,style='QEntry.TEntry')
        widget.grid(row=i,column=1,sticky='ew',pady=6)
        if browse is not None:
            ttk.Button(card,text='Browse',command=browse,style='QButton.TButton').grid(
                row=i,column=2,padx=(12,0),sticky='ew',pady=5)
        return widget

    def choose_source():
        result=filedialog.askopenfilename(
            title='Choose a lawfully held SEC/DART-shaped JSON',
            filetypes=[('JSON files','*.json')])
        if result:src.set(result)

    def choose_output():
        result=filedialog.askdirectory(title='Choose a new local report folder')
        if result:out.set(result)

    def changed_country(*_):
        issuer.set('')  # Never pre-populate a synthetic company as real
        dart_end.set('')
        dart_scope.set(False)
    country.trace_add('write',changed_country)

    row(0,'Country',country,values=('KR','US'))
    row(1,'Official issuer ID',issuer)
    row(2,'As-of date',asof)
    row(3,'Financial statements',statement,values=('CFS','OFS'))
    row(4,'DART fiscal end (if needed)',dart_end)
    row(5,'Local financial JSON',src,browse=choose_source)
    row(6,'Export directory',out,browse=choose_output)
    row(7,'New export filename',name)
    row(8,'HTML language',language,values=('ko','en'))
    card.columnconfigure(1,weight=1)

    ttk.Checkbutton(card,text='Include PDF (ASCII labels only; Korean font gate pending)',
                    variable=pdf,style='QCheck.TCheckbutton').grid(
                        row=9,column=1,columnspan=2,sticky='w',pady=(9,0))
    ttk.Checkbutton(card,
        text='I confirm DART JSON request scope (CFS/OFS); not official authentication',
        variable=dart_scope,style='QCheck.TCheckbutton').grid(
            row=10,column=1,columnspan=2,sticky='w',pady=(5,0))

    footer=ttk.Frame(container,style='Q.TFrame')
    footer.pack(fill='x',pady=(18,4))
    ttk.Label(footer,text='HOLD  •  Source rights and publisher authenticity unverified',
              style='QStatus.TLabel').pack(anchor='w',pady=(0,7))
    ttk.Label(footer,textvariable=status,style='QSubtitle.TLabel',
              wraplength=820).pack(anchor='w',pady=(0,12))
    buttons=ttk.Frame(footer,style='Q.TFrame')
    buttons.pack(fill='x')
    saved={'html':None,'dir':None,'name':None}

    def safe_error(exc):
        code=str(exc)
        if not re.fullmatch(r'[A-Z][A-Z0-9_]{3,80}',code):
            code='LOCAL_ANALYSIS_FAILED'
        status.set('HOLD — '+code+'; check company, date and output path.')
        messagebox.showerror('KUODRA — HOLD','Analysis was not completed. Error: '+code)

    def run():
        try:
            report,paths=run_selected(
                country=country.get(),issuer_id=issuer.get(),
                as_of=asof.get(),statement=statement.get(),source=src.get(),
                output_dir=out.get(),name=name.get(),pdf=pdf.get(),language=language.get(),
                dart_fiscal_end=dart_end.get().strip() or None,
                dart_scope_attested=dart_scope.get())
            saved.update(html=Path(paths['html']['path']),dir=out.get(),name=name.get())
            status.set('HOLD — '+str(len(report['findings']))+
                ' conditional metrics; local HTML/JSON'+('/PDF' if pdf.get() else '')+
                ' created. No source or market rights verified.')
            messagebox.showinfo('KUODRA — LOCAL EXPORT',
                                'Evidence report saved. Review Guard HOLD and source limitations.')
        except (ValueError,KeyError,OSError,TypeError) as exc:
            safe_error(exc)

    def open_last():
        if saved['html'] is not None and saved['html'].is_file():
            webbrowser.open(saved['html'].resolve().as_uri())
        else:
            messagebox.showinfo('KUODRA','Run a local analysis before opening a report.')

    def verify_last():
        if saved['dir'] is None:
            messagebox.showinfo('KUODRA','Create an export to verify first.')
            return
        try:
            check=verify_evidence_bundle(saved['dir'],saved['name'],
                                         require_pdf=pdf.get())
            status.set('HOLD — '+check['status']+
                       '. Byte integrity only; not publisher authentication.')
        except (ValueError,OSError,KeyError,TypeError) as exc:
            safe_error(exc)

    ttk.Button(buttons,text='Analyze local source',style='QPrimary.TButton',
               command=run).pack(side='left',padx=(0,12))
    ttk.Button(buttons,text='Open HTML',style='QButton.TButton',
               command=open_last).pack(side='left',padx=(0,12))
    ttk.Button(buttons,text='Verify export',style='QButton.TButton',
               command=verify_last).pack(side='left')
    ttk.Label(container,
        text='No automatic API access, no trading, no investment advice  |  Developer evaluation only',
        style='QSubtitle.TLabel').pack(anchor='w',pady=(16,0))
    if smoke_only:
        # Real Windows host/window test, without file/network access, clicks
        # or private data. It proves only toolkit initialization and layout.
        try:
            root.update_idletasks()
            root.update()
            def texts(widget):
                values=[]
                try:
                    v=widget.cget('text')
                    if v: values.append(str(v))
                except tk.TclError:
                    pass
                for child in widget.winfo_children():
                    values.extend(texts(child))
                return values
            labels=texts(root)
            required=(
                'KUODRA','Official issuer ID','As-of date',
                'Financial statements','DART fiscal end (if needed)',
                'Local financial JSON','Export directory',
                'Analyze local source','Open HTML','Verify export',
                'OFFLINE STAGING  ·  GUARD HOLD'
            )
            missing=[label for label in required if label not in labels]
            if missing:
                raise RuntimeError('GUI_MISSING_REQUIRED_CONTROLS')
            if country.get() != 'KR' or issuer.get() or dart_scope.get():
                raise RuntimeError('GUI_UNSAFE_DEFAULTS')
            # Simulate a customer reaching the action bar on a small screen.
            canvas.yview_moveto(1.0)
            root.update_idletasks()
            root.update()
            bottom=buttons.winfo_rooty()+buttons.winfo_height()
            viewport_bottom=canvas.winfo_rooty()+canvas.winfo_height()
            if bottom>viewport_bottom+3:
                raise RuntimeError('GUI_ACTIONS_NOT_REACHABLE_AT_SCROLL_END')
            return {
                'schema':'kuodra.windows-gui-smoke.v1',
                'status':'TK_WINDOW_RENDERED_NO_NETWORK',
                'window_width':root.winfo_width(),
                'window_height':root.winfo_height(),
                'required_control_count':len(required),
                'missing_controls':0,
                'critical_actions_reachable':True,
                'scroll_canvas_initialized':True,
                'user_data_loaded':False,
                'network_requests':0,
                'consumer_release_ready':False,
            }
        finally:
            root.destroy()
    root.mainloop()


if __name__=='__main__':
    main()
