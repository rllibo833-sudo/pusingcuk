import time, json, subprocess, re, importlib
from pathlib import Path

ROOT = Path(".")
KOS = ROOT/"library/kosakata.json"
NEXT = ROOT/"next_prompt.txt"
PARSER = ROOT/"parser.py"
APP = ROOT/"app.cuk"

def log(m): print(m, flush=True)

def patch_parser(new_word, target="hedeh"):
    p = PARSER.read_text()
    if f'self.at("{new_word}")' in p: return True
    old = f'if self.at("{target}"):'
    new = f'if self.at("{target}") or self.at("{new_word}"):'
    if old in p:
        PARSER.write_text(p.replace(old, new, 1))
        log(f"[PATCH] parser.py: {target} +={new_word}")
        return True
    log(f"[PATCH FAIL] target {target} gak ketemu di parser.py")
    return False

def test_cuk(code):
    APP.write_text(code)
    try:
        import parser
        importlib.reload(parser)
        ast = parser.parse(code)
        from evaluator import run
        run(code)
        log(f"[ENGINE OK] {code[:60]}")
        return True
    except Exception as e:
        log(f"[ENGINE FAIL] {e}")
        return False

def git_push(msg):
    s = subprocess.run(["git","status","--porcelain"], capture_output=True, text=True).stdout
    if not s.strip(): 
        log("[GIT] skip")
        return
    subprocess.run(["git","add","-A"])
    subprocess.run(["git","commit","-m",msg])
    subprocess.run(["git","push"])
    log(f"[PUSHED] {msg}")

if KOS.exists():
    try: kos = json.loads(KOS.read_text())
    except: kos = {}
else:
    kos = {}

log("[DATACENTER FINAL] HP + Ollama + Reality Engine + GitHub Actions")

while True:
    prompt = NEXT.read_text().strip() if NEXT.exists() else ""
    if not prompt:
        time.sleep(5)
        continue
    
    log(f"\n[LOOP] Prompt: {prompt}")
    
    if "tambah alias" in prompt.lower():
        m = re.search(r'tambah alias\s+["\']?(\w+)["\']?\s+untuk\s+["\']?(\w+)["\']?', prompt.lower())
        if m:
            new_word, target = m.group(1), m.group(2)
            if target not in kos or isinstance(kos.get(target), str):
                new_kos = {}
                for k,v in kos.items():
                    if isinstance(v, str):
                        new_kos.setdefault(v, []).append(k)
                    elif isinstance(v, list):
                        new_kos[k]=v
                kos = new_kos
            
            kos.setdefault(target, [])
            if new_word not in kos[target]:
                kos[target].append(new_word)
                KOS.write_text(json.dumps(kos, indent=2, ensure_ascii=False))
                if patch_parser(new_word, target):
                    if test_cuk(f'jancuk\n{new_word} "Evolusi {new_word}->{target} OK"\nselesai jancuk'):
                        git_push(f"evolve: {new_word}->{target} spill")
                        NEXT.write_text("")
            else:
                log(f"[SKIP] {new_word} sudah ada")
                NEXT.write_text("")
        else:
            log("[PARSE FAIL] format harus: tambah alias spill untuk hedeh")
            NEXT.write_text("")
    else:
        subprocess.run(["python3","jalanin_siklus.py",prompt])
        NEXT.write_text("")

    time.sleep(10)
