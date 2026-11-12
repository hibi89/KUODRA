"""Offline developer UI for the synthetic/local-file MVP. Not a packaged Windows product."""
from __future__ import annotations
from pathlib import Path
from kuodra.cli import analyze_bytes
from kuodra.report import export_local


def run_selected(*,country:str,issuer_id:str,as_of:str,source:str,output_dir:str,name:str='review',statement:str='CFS'):
    p=Path(source)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>1_000_000:
        raise ValueError('SOURCE_FILE_INVALID')
    report=analyze_bytes(p.read_bytes(),country=country,issuer_id=issuer_id,as_of=as_of,statement=statement)
    result=export_local(report,Path(output_dir),name)
    return report,result


def main():
    import tkinter as tk
    from tkinter import filedialog,messagebox,ttk
    from datetime import date
    from webbrowser import open as open_browser
    from pathlib import Path

    root=tk.Tk();root.title('KUODRA — Offline Company Evidence (Developer MVP)')
    root.geometry('820x510');root.minsize(720,460);root.configure(bg='#101722')
    style=ttk.Style(root)
    style.theme_use('clam')
    style.configure('TLabel',background='#101722',foreground='#edf0f7',font=('Segoe UI',11))
    style.configure('TButton',font=('Segoe UI',11))
    style.configure('TEntry',font=('Segoe UI',11))
    style.configure('TCombobox',font=('Segoe UI',11))
    frame=ttk.Frame(root,padding=24);frame.pack(fill='both',expand=True)
    country=tk.StringVar(value='KR');issuer=tk.StringVar(value='99998888');asof=tk.StringVar(value=date.today().isoformat())
    statement=tk.StringVar(value='CFS');src=tk.StringVar();out=tk.StringVar();name=tk.StringVar(value='review')
    hint=tk.StringVar(value='Data source: local file only • No external API • No investment advice.')

    def make_row(i,title,var,button=None,values=None):
        ttk.Label(frame,text=title).grid(row=i,column=0,sticky='w',pady=7)
        if values:
            w=ttk.Combobox(frame,textvariable=var,values=values,state='readonly',width=28)
        else:
            w=ttk.Entry(frame,textvariable=var,width=62)
        w.grid(row=i,column=1,sticky='ew',padx=8)
        if button:
            ttk.Button(frame,text='Browse',command=button).grid(row=i,column=2,padx=4)
    def selected_country(*_):
        issuer.set('99998888' if country.get()=='KR' else '0009999888')
    country.trace_add('write',selected_country)
    make_row(0,'Country',country,values=('KR','US'))
    make_row(1,'Official issuer ID',issuer)
    make_row(2,'Analysis date (YYYY-MM-DD)',asof)
    make_row(3,'Statement',statement,values=('CFS','OFS'))
    make_row(4,'Source JSON',src,button=lambda:src.set(filedialog.askopenfilename(title='Choose lawfully held source',filetypes=[('JSON files','*.json')]) or src.get()))
    make_row(5,'Report output folder',out,button=lambda:out.set(filedialog.askdirectory(title='Choose output folder') or out.get()))
    make_row(6,'Report name (new only)',name)
    frame.columnconfigure(1,weight=1)
    ttk.Label(frame,text='OFFLINE • SOURCE UNVERIFIED • HOLD',font=('Segoe UI',12,'bold')).grid(row=7,column=0,columnspan=3,sticky='w',pady=(18,2))
    ttk.Label(frame,textvariable=hint,wraplength=720).grid(row=8,column=0,columnspan=3,sticky='w',pady=8)
    last={'html':None}

    def run():
        try:
            report,artifacts=run_selected(country=country.get(),issuer_id=issuer.get(),as_of=asof.get(),source=src.get(),output_dir=out.get(),name=name.get(),statement=statement.get())
        except Exception as e:
            # Do not reveal confidential input contents/stack traces in GUI errors.
            hint.set('Analysis denied: '+type(e).__name__+': '+str(e)[:120])
            messagebox.showerror('KUODRA HOLD','Analysis denied. '+str(e)[:160])
            return
        last['html']=Path(artifacts['html']['path'])
        hint.set('HOLD / '+str(len(report['findings']))+' computed observations; report saved to the chosen folder.')
        messagebox.showinfo('KUODRA','Offline report generated. Source and market rights are NOT verified.')

    def open_last():
        if last['html'] and last['html'].exists():
            open_browser(last['html'].resolve().as_uri())
        else:
            messagebox.showinfo('KUODRA','Run an analysis to create a local HTML report first.')

    ttk.Button(frame,text='Analyze local file (HOLD)',command=run).grid(row=9,column=1,sticky='w',pady=16)
    ttk.Button(frame,text='Open last local HTML report',command=open_last).grid(row=9,column=1,sticky='e',pady=16)
    root.mainloop()

if __name__=='__main__':main()
