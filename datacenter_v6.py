# V6 - SATU-SATUNYA DATACENTER
import time, re, subprocess, random
from pathlib import Path
FALLBACK=["jedor","gebber","bacrit","nyalak","muncrat","semprot","senggol","berak","crot","koar2"]
print("[V6] HP=Datacenter+Adapter | Ollama=qwen2:0.5b | Engine=parser+eval")
while True:
    txt=Path("library/kosakata.json").read_text()
    used=set(re.findall(r'"([^"]+)"', re.search(r'"hedeh".*?"aliases"\s*:\s*\[(.*?)\]', txt, re.S).group(1)) if re.search(r'"hedeh".*?"aliases"', txt, re.S) else [])
    try:
        out=subprocess.run(["ollama","run","qwen2:0.5b","1 kata slang Indonesia untuk print, 1 kata saja"], capture_output=True, text=True, timeout=25).stdout
        kata=re.sub(r'[^a-z]','', out.strip().split()[-1].lower())[:12]
        line=f"tambah alias {kata} untuk hedeh" if kata and kata not in used and len(kata)>=3 else ""
    except: line=""
    if not line:
        cand=[x for x in FALLBACK if x not in used]
        kata=random.choice(cand) if cand else f"k{random.randint(100,999)}"
        line=f"tambah alias {kata} untuk hedeh"
    print(f"[V6] {line}")
    Path("next_prompt.txt").write_text(line)
    subprocess.run(["python3","V6_CLEAN.py"])
    subprocess.run(["git","add","library/kosakata.json","parser.py","app.cuk",".gitignore"])
    subprocess.run(["git","commit","-m",f"evolve v6: {line}"])
    subprocess.run(["git","push"])
    time.sleep(30)
