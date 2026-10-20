import subprocess, time
from pathlib import Path
while True:
  if not Path("next_prompt.txt").read_text().strip():
    # minta AI bikin alias baru
    r=subprocess.run(["ollama","run","qwen2:0.5b","sebutkan 1 alias gaul untuk kata print/cetak, hanya jawab: tambah alias X untuk hedeh"], capture_output=True, text=True)
    prompt=r.stdout.strip().splitlines()[-1]
    Path("next_prompt.txt").write_text(prompt)
    print(f"[OLLAMA] {prompt}")
  time.sleep(5)
