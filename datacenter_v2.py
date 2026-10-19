#!/usr/bin/env python3
"""
DATACENTER EVOLUSI BAHASA MANDIRI
Siklus: next_prompt.txt -> adapter -> parser/evaluator asli -> 
        kalo OK, update library/kosakata.json -> git push -> 
        android-studio-apk.yml otomatis build APK
"""
import time, subprocess, json
from pathlib import Path
from parser import parse
from evaluator import run

print("[DATACENTER V2] Siklus Bahasa Mandiri START - terhubung ke engine asli")

while True:
    prompt_file = Path("next_prompt.txt")
    prompt = prompt_file.read_text().strip() if prompt_file.exists() else "bikin halo dunia"
    print(f"\n[LOOP] Prompt: {prompt}")
    
    # 1. ADAPTER (HP+Termux -> Ollama/Pusingcuk AI asli)
    r = subprocess.run(["python","pusingcuk_adapter.py",prompt], capture_output=True, text=True)
    cuk_code = r.stdout.strip()
    Path("app.cuk").write_text(cuk_code)
    
    # 2. REALITY ENGINE PAKAI ENGINE ASLI LU (tools/diagnostic_repair_loop.py logic)
    for attempt in range(3):
        try:
            parse(cuk_code)
            run(cuk_code)
            print(f"[ENGINE ASLI] OK percobaan {attempt+1}")
            
            # 3. JIKA MANDIRI: KEMBANGKAN KOSAKATA, BUKAN CUMA app.cuk
            if "tambah alias" in prompt.lower():
                kosakata_path = Path("library/kosakata.json")
                kosakata = json.loads(kosakata_path.read_text()) if kosakata_path.exists() else {}
                # contoh: "tambah alias cetak untuk hedeh"
                if "cetak" in prompt.lower():
                    kosakata["cetak"] = "hedeh"
                    kosakata_path.write_text(json.dumps(kosakata, indent=2))
                    print(f"[EVOLUSI] Bahasa berkembang: {kosakata}")

            # 4. PUSH - INI OTOMATIS TRIGGER .github/workflows/android-studio-apk.yml
            # JADI APK KEBIKIN DI GITHUB, BUKAN DI HP (ANTI FC)
            subprocess.run(["git","add","-A"])
            subprocess.run(["git","commit","-m",f"evolve: {prompt}"])
            subprocess.run(["git","push"])
            print("[GIT] Pushed -> cek Actions tab buat download APK")
            break
        except Exception as e:
            print(f"[ENGINE] ERROR: {e} -> balik ke AI perbaiki")
            fix = f"perbaiki error {e}: {cuk_code}"
            r2 = subprocess.run(["python","pusingcuk_adapter.py",fix], capture_output=True, text=True)
            cuk_code = r2.stdout.strip()
    
    print("Tidur 15 detik... ganti next_prompt.txt untuk evolusi baru")
    time.sleep(15)
