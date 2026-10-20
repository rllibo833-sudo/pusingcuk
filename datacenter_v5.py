import re, subprocess, time, random
from pathlib import Path

FALLBACK = ["jedor","senggol","muncrat","gebber","bacrit","nyalak","berak","semprot","crot","koar2"]

def get_used():
    txt=Path("library/kosakata.json").read_text()
    m=re.search(r'"hedeh"\s*:\s*\[(.*?)\]', txt, re.S)
    return set(re.findall(r'"([^"]+)"', m.group(1))) if m else set()

print("[V5.1] HP -> Ollama (fast) -> Parser -> GitHub")
while True:
    used=get_used()
    print(f"[USED {len(used)}] coba ollama...")
    line=""
    try:
        # prompt super pendek biar cepet
        p = subprocess.run(["ollama","run","qwen2:0.5b","1 kata slang untuk print, contoh: jedor. Jawab 1 kata saja!"], capture_output=True, text=True, timeout=25)
        out = p.stdout.strip().split()
        if out:
            kata = re.sub(r'[^a-z0-9]','',out[-1].lower())[:12]
            if kata and kata not in used and len(kata)>=3:
                line = f"tambah alias {kata} untuk hedeh"
                print(f"[OLLAMA RAW] {p.stdout[:80]} -> {line}")
    except Exception as e:
        print(f"[OLLAMA TIMEOUT/ERR] {e}")

    if not line:
        # fallback random biar tetep evolusi
        remain=[x for x in FALLBACK if x not in used]
        if not remain:
            remain=[f"kata{random.randint(100,999)}"]
        kata=random.choice(remain)
        line=f"tambah alias {kata} untuk hedeh"
        print(f"[FALLBACK] {line}")

    Path("next_prompt.txt").write_text(line)
    subprocess.run(["python3","fix_parser_all.py"])
    subprocess.run(["git","add","-A"])
    subprocess.run(["git","commit","-m",f"evolve v5.1: {line}"])
    subprocess.run(["git","push"])
    print(f"[PUSHED] {line}\n")
    time.sleep(15)
