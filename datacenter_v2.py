#!/usr/bin/env python3
import time, subprocess, json, os
from pathlib import Path
from parser import parse
from evaluator import run

print("[DATACENTER V3] Evolusi Bahasa Mandiri FIX")

while True:
    p_file = Path("next_prompt.txt")
    prompt = p_file.read_text().strip() if p_file.exists() else "bikin halo dunia"
    print(f"\n[LOOP] Prompt: {prompt}")

    # === EVOLUSI LANGSUNG TANPA AI DULU (BIAR KELIATAN MANDIRI) ===
    evolved = False
    if "tambah alias" in prompt.lower():
        # contoh prompt: tambah alias cetak untuk hedeh
        parts = prompt.lower().split()
        try:
            # cari kata setelah "alias"
            idx = parts.index("alias")
            new_word = parts[idx+1]
            target = parts[idx+3] if len(parts) > idx+3 else "hedeh"
            
            kos_path = Path("library/kosakata.json")
            kos = json.loads(kos_path.read_text()) if kos_path.exists() else {}
            if new_word not in kos:
                kos[new_word] = target
                kos_path.write_text(json.dumps(kos, indent=2, ensure_ascii=False))
                print(f"[EVOLUSI] Bahasa berkembang! {new_word} -> {target}")
                print(f"[EVOLUSI] Isi kosakata.json: {kos}")
                
                # bikin test file buat reality engine
                test_code = f'jancuk\n{new_word} "Tes {new_word} OK"\nselesai jancuk'
                Path("app.cuk").write_text(test_code)
                parse(test_code)  # test pake parser asli lu, bukan dummy
                run(test_code)
                evolved = True
            else:
                print(f"[EVOLUSI] Alias {new_word} sudah ada")
        except Exception as e:
            print(f"[EVOLUSI] Gagal parse prompt alias: {e}")

    if not evolved:
        # fallback halo dunia biasa
        r = subprocess.run(["python","pusingcuk_adapter.py",prompt], capture_output=True, text=True)
        Path("app.cuk").write_text(r.stdout.strip())
        try:
            parse(Path("app.cuk").read_text())
            run(Path("app.cuk").read_text())
            print("[ENGINE] OK")
        except Exception as e:
            print(f"[ENGINE] ERROR: {e}")

    # === PUSH HANYA KALO ADA PERUBAHAN (ANTI Everything up-to-date) ===
    status = subprocess.run(["git","status","--porcelain"], capture_output=True, text=True).stdout.strip()
    if status:
        print(f"[GIT] Ada perubahan:\n{status}")
        subprocess.run(["git","add","-A"])
        subprocess.run(["git","commit","-m",f"evolve: {prompt}"])
        subprocess.run(["git","push"])
        print("[GIT] Pushed -> cek Actions > android-studio-apk.yml buat download APK")
    else:
        print("[GIT] Skip push, gak ada perubahan (biar gak spam)")

    print("Tidur 10 detik... ganti next_prompt.txt kalo mau evolusi lain")
    time.sleep(10)
