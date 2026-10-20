#!/data/data/com.termux/files/usr/bin/bash
while true; do
  echo "=== SIKLUS FULL CUK BARU $(date) ==="
  git pull origin main --rebase || true
  pgrep ollama || (ollama serve > adapter.log 2>&1 & sleep 4)
  export OLLAMA_MODEL=llama3.2:1b
  sed -i 's/qwen2:0.5b/llama3.2:1b/g; s/tinyllama:latest/llama3.2:1b/g' tools/local_ai_adapter.py tools/evaluate_live_ai.py 2>/dev/null || true

  # [1] TERMUX+HP ADAPTER & DATACENTER
  echo "[1] ADAPTER"
  python tools/local_ai_adapter.py || true
  python datacenter_v6.py || true
  python tools/reality_engine.py || true

  # [2] FIX DETERMINISTIK - BAHASA .CUK BARU, COMPILER, MANIFEST, KOSAKATA, NATIVE, C, VPM
  echo "[2] FIX SEMUA FILE WAJIB"
  python - << 'PY'
import pathlib, json, re
canon, alias = "hedeh", "koar2"

# --- 1. SPEC.md + README + docs ---
for p in list(pathlib.Path(".").rglob("SPEC.md")) + [pathlib.Path("README.md")]:
    if p.exists() and p.is_file():
        t=p.read_text()
        if canon in t and alias not in t:
            p.write_text(t.replace(canon, f"{canon}, {alias}"))
            print(f"[FIX] {p}")

# --- 2. LEXER, PARSER, COMPILER_IR, INTERPRETER ---
for name in ["lexer.py","parser.py","compiler_ir.py","interpreter.py","ast_nodes.py","compiler/*.py"]:
    for p in pathlib.Path(".").rglob(name):
        t=p.read_text()
        if canon in t and alias not in t:
            t=t.replace(f'"{canon}"', f'"{canon}", "{alias}"').replace(f"'{canon}'", f"'{canon}', '{alias}'").replace(canon, f"{canon}, {alias}")
            p.write_text(t)
            print(f"[FIX] {p}")

# --- 3. KOSAKATA JSON + MANIFEST JSON ---
for p in list(pathlib.Path(".").rglob("*kosakata*.json")) + list(pathlib.Path(".").rglob("*vocab*.json")) + list(pathlib.Path(".").rglob("manifest*.json")) + list(pathlib.Path(".").rglob("pusingcuk.json")) + [pathlib.Path("library/manifest.json"), pathlib.Path("src/manifest.json")]:
    if p.exists() and p.is_file():
        try:
            txt=p.read_text()
            if canon in txt and alias not in txt:
                # coba json
                try:
                    data=json.loads(txt)
                    # update kosakata dict/list
                    s=json.dumps(data)
                    s=s.replace(canon, f"{canon}")
                    # tambah alias jika list
                    if isinstance(data, dict):
                        if canon in data:
                            data[alias]=data[canon]
                    # jika ada keywords
                    j=json.dumps(data, indent=2, ensure_ascii=False)
                    if alias not in j:
                        j=j.replace(canon, f'{canon}", "{alias}"') if f'"{canon}"' in j else j
                    p.write_text(j)
                except:
                    p.write_text(txt.replace(canon, f"{canon}, {alias}"))
                print(f"[FIX] JSON {p}")
        except Exception as e:
            print(f"skip {p} {e}")

# --- 4. NATIVE + C ---
for p in list(pathlib.Path("native").rglob("*.c")) + list(pathlib.Path("native").rglob("*.h")) + list(pathlib.Path("native").rglob("*.rs")) if pathlib.Path("native").exists() else []:
    t=p.read_text()
    if canon in t and alias not in t:
        p.write_text(t.replace(canon, f"{canon}, {alias}"))
        print(f"[FIX] NATIVE {p}")

# --- 5. VPM (package manager) ---
for p in list(pathlib.Path(".").rglob("vpm*.json")) + list(pathlib.Path(".").rglob("vpm.toml")):
    if p.exists():
        t=p.read_text()
        if canon in t and alias not in t:
            p.write_text(t.replace(canon, f"{canon}, {alias}"))
            print(f"[FIX] VPM {p}")

# --- 6. FIXTURES ---
pathlib.Path("tests/fixtures").mkdir(parents=True, exist_ok=True)
pathlib.Path(f"tests/fixtures/{alias}.cuk").write_text(f"{alias}\n")
print("[FIX] fixture")

PY

  python tools/evolve_language.py hedeh koar2 || true
  python tools/force_approve.py || true
  python fix_parser_all.py || true
  python tools/generate_compatibility.py || true
  
  echo "[3] BUILD NATIVE + C"
  [ -f native/build.sh ] && bash native/build.sh || true
  [ -f Makefile ] && make || true

  echo "[4] PUSH BALIK KE TERMUX"
  git add .
  git commit -m "full evolve: manifest,kosakata,native,c,vpm,compiler hedeh->koar2 $(date +%H:%M)" || true
  git push origin main
  git pull origin main --rebase || true
  sleep 60
done
