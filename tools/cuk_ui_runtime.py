#!/usr/bin/env python3
"""Render safe @ui directives embedded in a .cuk file into interactive HTML."""
from __future__ import annotations
import argparse, html, json, re
from pathlib import Path

ALLOWED = {"app", "theme", "navigation", "screen", "text", "metric", "field", "action", "filter", "report", "end"}

def parse_ui(source: str) -> dict:
    ui = {"app":"PusingCuk App","theme":"system","navigation":[],"screens":[]}
    screen = None
    for line_no, line in enumerate(source.splitlines(), 1):
        m = re.match(r"^\s*#\s*@([a-z_]+)\s*(.*?)\s*$", line)
        if not m: continue
        kind, payload = m.groups()
        if kind not in ALLOWED: raise ValueError(f"UI directive tidak dikenal pada baris {line_no}: {kind}")
        if kind == "app":
            if not payload: raise ValueError(f"Nama aplikasi kosong pada baris {line_no}")
            ui["app"] = payload
        elif kind == "theme":
            if payload not in {"system","light","dark"}: raise ValueError(f"Tema tidak valid pada baris {line_no}")
            ui["theme"] = payload
        elif kind == "navigation":
            for item in payload.split(","):
                key, sep, label = item.partition(":")
                key, label = key.strip(), label.strip()
                if not sep or not re.fullmatch(r"[a-z][a-z0-9_]*", key) or not label: raise ValueError(f"Navigasi tidak valid pada baris {line_no}")
                ui["navigation"].append({"id":key,"label":label})
        elif kind == "screen":
            key, sep, label = payload.partition(":")
            key, label = key.strip(), label.strip()
            if not sep or not re.fullmatch(r"[a-z][a-z0-9_]*", key) or not label: raise ValueError(f"Layar tidak valid pada baris {line_no}")
            screen = {"id":key,"title":label,"texts":[],"metrics":[],"fields":[],"actions":[],"filters":[],"reports":[]}
            ui["screens"].append(screen)
        elif kind == "end": screen = None
        else:
            if screen is None: raise ValueError(f"@{kind} harus berada di dalam @screen (baris {line_no})")
            key, sep, rest = payload.partition(":")
            if not sep or not key.strip(): raise ValueError(f"Payload @{kind} tidak valid pada baris {line_no}")
            parts = rest.split(":")
            item = {"id":key.strip(),"label":parts[0].strip()}
            if kind == "field":
                item["type"] = parts[1].strip() if len(parts)>1 else "text"
                item["rules"] = ":".join(parts[2:]).strip() if len(parts)>2 else ""
                if item["type"] not in {"text","date","select","integer"}: raise ValueError(f"Tipe field tidak didukung: {item['type']}")
            target = {"text":"texts","metric":"metrics","field":"fields","action":"actions","filter":"filters","report":"reports"}[kind]
            screen[target].append(item)
    if not ui["screens"]: raise ValueError("Tidak ada @screen")
    ids = [s["id"] for s in ui["screens"]]
    if len(ids) != len(set(ids)): raise ValueError("ID layar duplikat")
    if not ui["navigation"] or any(n["id"] not in set(ids) for n in ui["navigation"]): raise ValueError("Navigasi kosong atau menunjuk ke layar yang tidak ada")
    return ui

def render(ui: dict) -> str:
    e = html.escape
    nav = "".join(f'<button class="nav" data-route="{e(n["id"],quote=True)}">{e(n["label"])}</button>' for n in ui["navigation"])
    screens = []
    for s in ui["screens"]:
        body = "".join(f'<p>{e(x["label"])}</p>' for x in s["texts"])
        if s["metrics"]:
            body += '<div class="metrics">' + "".join(f'<article><small>{e(m["label"])}</small><strong id="metric-{e(m["id"],quote=True)}">—</strong></article>' for m in s["metrics"]) + '</div>'
        for f in s["fields"] + s["filters"]:
            typ = f.get("type","text"); itype = {"integer":"number","select":"text"}.get(typ,typ)
            req = " required" if "required" in f.get("rules","") else ""
            minimum = ' min="0" step="1"' if typ=="integer" or "min=0" in f.get("rules","") else ""
            if typ == "select":
                body += f'<label>{e(f["label"])}<select name="{e(f["id"],quote=True)}"{req}><option value="">Memuat pilihan…</option></select></label>'
            else:
                body += f'<label>{e(f["label"])}<input name="{e(f["id"],quote=True)}" type="{itype}"{req}{minimum}></label>'
        for r in s["reports"]: body += f'<section class="report" data-report="{e(r["id"],quote=True)}"><h3>{e(r["label"])}</h3><p>Data dimuat melalui backend .cuk.</p></section>'
        for a in s["actions"]: body += f'<button class="action" data-action="{e(a["id"],quote=True)}">{e(a["label"])}</button>'
        screens.append(f'<section class="screen" id="screen-{e(s["id"],quote=True)}" data-screen="{e(s["id"],quote=True)}"><h1>{e(s["title"])}</h1>{body}<p class="status" aria-live="polite"></p></section>')
    config = json.dumps({"app":ui["app"],"theme":ui["theme"],"navigation":ui["navigation"]},ensure_ascii=True).replace("<","\\u003c")
    return f'''<!doctype html><html lang="id" data-theme="{e(ui["theme"],quote=True)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(ui["app"])}</title><style>
:root{{font-family:system-ui,sans-serif;color:#18352b;background:#f3f7f4;--panel:#fff;--ink:#18352b;--accent:#087b56}}[data-theme="dark"]{{color-scheme:dark;--panel:#17251f;--ink:#e7f5ec;background:#0d1712;--accent:#43bd8d}}*{{box-sizing:border-box}}body{{margin:0;color:var(--ink)}}header{{padding:18px 22px;background:var(--panel);border-bottom:1px solid #8a9b902b;font-weight:800}}.layout{{display:grid;grid-template-columns:200px minmax(0,1fr);min-height:calc(100vh - 60px)}}nav{{padding:12px;background:var(--panel);display:flex;flex-direction:column;gap:6px}}button,input{{font:inherit}}button{{cursor:pointer;border:1px solid #8a9b9044;border-radius:9px;padding:10px;background:var(--panel);color:var(--ink);text-align:left}}button:focus-visible,input:focus-visible{{outline:3px solid #21a477;outline-offset:2px}}.nav[aria-current="page"]{{background:var(--accent);color:white}}main{{padding:clamp(16px,4vw,36px);max-width:1000px;width:100%}}.screen{{display:none}}.screen.active{{display:block}}h1{{font-size:clamp(23px,4vw,32px)}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:20px 0}}article,.report{{background:var(--panel);border:1px solid #8a9b902b;border-radius:12px;padding:16px;margin:12px 0}}small,label{{display:block}}strong{{display:block;font-size:21px;margin-top:8px}}label{{margin:12px 0;font-weight:600}}input{{display:block;width:100%;padding:11px;border-radius:8px;border:1px solid #8a9b9070;background:var(--panel);color:var(--ink);margin-top:6px}}.action{{margin:5px;background:var(--accent);color:white}}.status{{min-height:1.5em;color:var(--accent)}}@media(max-width:600px){{.layout{{grid-template-columns:1fr}}nav{{position:sticky;top:0;z-index:2;flex-direction:row;overflow:auto}}nav button{{white-space:nowrap}}main{{padding:16px}}}}
</style></head><body><header>{e(ui["app"])}</header><div class="layout"><nav aria-label="Navigasi utama">{nav}<button id="theme-toggle" type="button">Ganti tema</button></nav><main>{''.join(screens)}</main></div><script>const CUK_UI={config};(()=>{{const nav=[...document.querySelectorAll('[data-route]')],screens=[...document.querySelectorAll('[data-screen]')];function go(id){{screens.forEach(s=>s.classList.toggle('active',s.dataset.screen===id));nav.forEach(b=>b.dataset.route===id?b.setAttribute('aria-current','page'):b.removeAttribute('aria-current'))}}nav.forEach(b=>b.addEventListener('click',()=>go(b.dataset.route)));document.querySelector('#theme-toggle').addEventListener('click',()=>{{const r=document.documentElement;r.dataset.theme=r.dataset.theme==='dark'?'light':'dark';try{{localStorage.setItem('cuk-ui-theme',r.dataset.theme)}}catch{{}}}});try{{const saved=localStorage.getItem('cuk-ui-theme');if(saved==='dark'||saved==='light')document.documentElement.dataset.theme=saved}}catch{{}}const drafts=new Map();async function request(operation,input){{if(!window.cukAccountBridge?.request)throw new Error('BRIDGE_UNAVAILABLE');const response=await window.cukAccountBridge.request({{contract_version:'cukaccount.platform.v1',request_id:crypto.randomUUID(),operation,input}});if(response.status!=='succeeded')throw new Error(response.diagnostic?.code||'BRIDGE_REJECTED');return response.result}}async function loadAccounts(){{try{{const result=await request('db.query_accounts',{{}});document.querySelectorAll('select[name=account],select[name=counter_account],select[name=account_id]').forEach(sel=>{{sel.replaceChildren(new Option('Pilih akun…',''));result.accounts.forEach(a=>{{if(a.active)sel.add(new Option(a.name+' ('+a.id+')',a.id))}})}})}}catch{{document.querySelectorAll('select').forEach(sel=>sel.replaceChildren(new Option('Bridge belum tersedia','')))}}}}document.querySelectorAll('.screen').forEach(s=>s.querySelectorAll('.action').forEach(b=>b.addEventListener('click',async()=>{{const fields=[...s.querySelectorAll('input,select')],missing=fields.find(i=>i.required&&!i.value.trim()),status=s.querySelector('.status');if(missing){{missing.focus();status.textContent='Lengkapi kolom '+missing.name;return}}try{{if(b.dataset.action==='validate'){{const d=Number(s.querySelector('[name=debit]')?.value||0),cr=Number(s.querySelector('[name=credit]')?.value||0);status.textContent=Number.isSafeInteger(d)&&Number.isSafeInteger(cr)&&d>0&&d===cr?'Nominal seimbang; validasi otoritatif dilakukan backend .cuk.':'Debit dan kredit wajib sama, integer Rupiah, dan lebih dari nol.';return}}if(b.dataset.action==='save_draft'){{const d=Number(s.querySelector('[name=debit]')?.value||0),cr=Number(s.querySelector('[name=credit]')?.value||0),a=s.querySelector('[name=account]')?.value,ca=s.querySelector('[name=counter_account]')?.value;if(!Number.isSafeInteger(d)||!Number.isSafeInteger(cr)||d<=0||d!==cr||!a||!ca||a===ca)throw new Error('JURNAL_INPUT_INVALID');const id=crypto.randomUUID();const result=await request('db.save_journal_draft',{{entry_id:id,date:s.querySelector('[name=date]').value,description:s.querySelector('[name=description]').value,lines:[{{account_id:a,description:'Debit',debit:d,credit:0}},{{account_id:ca,description:'Kredit',debit:0,credit:cr}}]}});drafts.set(id,result);s.dataset.draftId=id;status.textContent='Draft tersimpan: '+id+' — belum diposting.';return}}if(b.dataset.action==='post_journal'){{const id=s.dataset.draftId;if(!id)throw new Error('DRAFT_NOT_SAVED');const result=await request('db.post_journal',{{entry_id:id,idempotency_key:'ui-post-'+id}});status.textContent='Jurnal terposting. Debit '+result.total_debit+' / Kredit '+result.total_credit;return}}if(b.dataset.action==='preview_close'){{status.textContent='Penutupan periode memerlukan periode terpilih melalui bridge bertipe.';return}}status.textContent='Aksi belum tersedia: '+b.dataset.action}}catch(err){{status.textContent='Tidak berhasil: '+String(err.message||err).slice(0,180)}}}})));loadAccounts();if(screens.length)go(CUK_UI.navigation[0].id)}})();</script></body></html>'''

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("source",type=Path); p.add_argument("-o","--output",type=Path,required=True); a=p.parse_args()
    try:
        ui=parse_ui(a.source.read_text(encoding="utf-8")); output=render(ui); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(output,encoding="utf-8")
    except (OSError,UnicodeError,ValueError) as exc: p.error(str(exc))
    print(f"UI dirender: {a.output} ({len(ui['screens'])} layar)")
if __name__=="__main__": main()
