import time, json, subprocess, re, importlib, random
from pathlib import Path

KOS=Path("library/kosakata.json"); NEXT=Path("next_prompt.txt")
PARSER=Path("parser.py"); APP=Path("app.cuk")
ALL=["cetak","gas","tampilkan","sembur","omong","keluarin","print","spill","berisik","bacot","suarakan","teriak","gembor","koar"]

def log(m): print(m, flush=True)

def get_kos_raw():
    txt=KOS.read_text() if KOS.exists() else "{}"
    # coba parse JSON bener, kalo gagal ambil manual via regex
    try:
        j=json.loads(txt)
        # kalau list campur dict, cari hedeh
        if isinstance(j, dict) and "hedeh" in j and isinstance(j["hedeh"], list):
            return j
        if isinstance(j, dict):
            return j
    except: pass
    # fallback regex: cari "hedeh": ["spill",...]
    m=re.search(r'"hedeh"\s*:\s*\[(.*?)\]', txt, re.S)
    if m:
        items=re.findall(r'"([^"]+)"', m.group(1))
        return {"hedeh": items}
    return {"hedeh":[]}

def save_kos(kos):
    # simpan minimal hedeh doang biar gak ngerusak format kompleks lu
    existing={}
    try: existing=json.loads(KOS.read_text())
    except: existing={}
    if isinstance(existing, dict):
        existing["hedeh"]=kos.get("hedeh",[])
        KOS.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    else:
        KOS.write_text(json.dumps(kos, indent=2, ensure_ascii=False))

def patch_parser(nw,t="hedeh"):
    p=PARSER.read_text()
    if f'self.at("{nw}")' in p: return True
    if f'if self.at("{t}"): ' in p or f'if self.at("{t}"):' in p:
        p=p.replace(f'if self.at("{t}"): ', f'if self.at("{t}") or self.at("{nw}"): ',1).replace(f'if self.at("{t}"): ', f'if self.at("{t}") or self.at("{nw}"): ',1)
        # coba 2 varian
        if f'self.at("{nw}")' not in p:
            p=p.replace(f'if self.at("{t}"):', f'if self.at("{t}") or self.at("{nw}"):',1)
        PARSER.write_text(p)
        log(f"[PATCH] {t}+={nw}")
        return True
    return False

def test_cuk(code):
    APP.write_text(code)
    try:
        import parser; importlib.reload(parser)
        parser.parse(code)
        from evaluator import run; run(code)
        return True
    except Exception as e:
        log(f"[FAIL] {e}"); return False

def git_push(msg):
    if subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout.strip():
        subprocess.run(["git","add","-A"]); subprocess.run(["git","commit","-m",msg]); subprocess.run(["git","push"])
        log(f"[PUSHED] {msg}")

log("[DATACENTER V4.1] Filter duplikat + anti-loop")

while True:
    kos=get_kos_raw()
    used=set(kos.get("hedeh",[]))
    remain=[x for x in ALL if x not in used]
    
    prompt=NEXT.read_text().strip() if NEXT.exists() else ""
    if not prompt:
        if remain:
            # minta ollama tapi kasih tau yang sudah ada
            avoid=",".join(list(used)[:10])
            try:
                r=subprocess.run(["ollama","run","qwen2:0.5b",f"Berikan 1 alias baru untuk print selain {avoid}. Jawab format: tambah alias X untuk hedeh"], capture_output=True, text=True, timeout=25)
                cands=[l for l in r.stdout.splitlines() if "tambah alias" in l.lower()]
                prompt=cands[-1] if cands else f"tambah alias {random.choice(remain)} untuk hedeh"
            except:
                prompt=f"tambah alias {random.choice(remain)} untuk hedeh"
        else:
            log("[DONE] Semua kandidat hedeh habis! Reset kos atau tambah list ALL"); time.sleep(30); continue
        NEXT.write_text(prompt)
        log(f"[OLLAMA->PROMPT] {prompt}")

    log(f"[LOOP] {prompt} | used={used} | remain={remain}")
    m=re.search(r'tambah alias\s+["\']?(\w+)["\']?\s+untuk\s+["\']?(\w+)["\']?', prompt.lower())
    if m:
        nw,t=m.group(1),m.group(2)
        kos=get_kos_raw()
        kos.setdefault(t,[])
        if nw in kos[t]:
            log(f"[SKIP] {nw} sudah ada, generate baru...")
            NEXT.write_text("") # kosongin biar loop generate baru
            time.sleep(2)
            continue
        kos[t].append(nw)
        save_kos(kos)
        if patch_parser(nw,t):
            if test_cuk(f'jancuk\n{nw} "Evolusi {nw}->{t} OK"\nselesai jancuk'):
                git_push(f"evolve: {nw}->{t} v4.1")
    else:
        log("[PARSE FAIL]")

    NEXT.write_text("")
    time.sleep(10)
