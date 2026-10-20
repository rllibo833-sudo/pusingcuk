import subprocess, time
from pathlib import Path
import random

CANDIDATES = ["cetak","gas","spill","tampilkan","sembur","omong","keluarin","print"]
print("[OLLAMA AUTO] qwen2:0.5b -> next_prompt.txt")

while True:
    # cuma isi kalau kosong (biar gak tabrakan sama datacenter_final.py)
    if not Path("next_prompt.txt").read_text().strip():
        # coba tanya Ollama, kalau gagal pake random
        try:
            r = subprocess.run(
                ["ollama","run","qwen2:0.5b","Jawab hanya 1 baris: tambah alias <kata gaul> untuk hedeh. Contoh: tambah alias gas untuk hedeh"],
                capture_output=True, text=True, timeout=20
            )
            line = [l for l in r.stdout.strip().splitlines() if "tambah alias" in l.lower()][-1]
        except:
            line = f"tambah alias {random.choice(CANDIDATES)} untuk hedeh"
        
        Path("next_prompt.txt").write_text(line)
        print(f"[PROMPT BARU] {line}")
    time.sleep(8)
