import time, subprocess, json, re
from pathlib import Path
from parser import parse
from evaluator import run

def patch_parser(new_word, target):
    p = Path("parser.py").read_text()
    # cari if self.at("hedeh"):  ->  if self.at("hedeh") or self.at("cetak"):
    pattern = f'self.at("{target}")'
    if f'self.at("{new_word}")' in p:
        return False
    # ganti baris pertama yang ada target nya
    new_p = p.replace(f'if self.at("{target}"):',
                      f'if self.at("{target}") or self.at("{new_word}"): ', 1)
    if new_p != p:
        Path("parser.py").write_text(new_p)
        print(f"[PATCH] parser.py: {target} sekarang juga menerima '{new_word}'")
        return True
    return False

print("[DATACENTER V3] Patch Parser + Evolusi")

while True:
    prompt = Path("next_prompt.txt").read_text().strip()
    print(f"\n[LOOP] Prompt: {prompt}")

    if "tambah alias" in prompt.lower():
        parts = prompt.lower().split()
        idx = parts.index("alias")
        new_word = parts[idx+1].strip('"')
        target = parts[idx+3].strip('"') if len(parts)>idx+3 else "hedeh"

        kos_path = Path("library/kosakata.json")
        kos = json.loads(kos_path.read_text()) if kos_path.exists() else {}
        
        if new_word not in kos:
            kos[new_word] = target
            kos_path.write_text(json.dumps(kos, indent=2, ensure_ascii=False))
            patch_parser(new_word, target)
            
            test_code = f'jancuk\n{new_word} "Tes {new_word} OK"\nselesai jancuk'
            Path("app.cuk").write_text(test_code)
            try:
                # reload parser biar patch kepake
                import importlib, parser
                importlib.reload(parser)
                parser.parse(test_code)
                run(test_code)
                print(f"[ENGINE] OK! Bahasa baru '{new_word}' jalan!")
            except Exception as e:
                print(f"[ENGINE] Masih error: {e}")
        else:
            print(f"[EVOLUSI] Alias {new_word} sudah ada, skip")

    status = subprocess.run(["git","status","--porcelain"], capture_output=True, text=True).stdout
    if status.strip():
        subprocess.run(["git","add","-A"])
        subprocess.run(["git","commit","-m",f"evolve: {prompt}"])
        subprocess.run(["git","push"])
        print("[GIT] Pushed -> Actions bakal build APK otomatis")
    else:
        print("[GIT] Skip push")

    time.sleep(10)
