#!/data/data/com.termux/files/usr/bin/bash
while true; do
  git pull origin main --rebase || true
  pgrep ollama || (ollama serve > ~/ollama.log 2>&1 & sleep 3)
  
  python tools/local_ai_adapter.py || echo "[SKIP] adapter gagal, lanjut"
  python tools/reality_engine.py || true
  python tools/evaluate_live_ai.py || echo "[SKIP] evaluate gagal, lanjut fix"

  echo "[FIX DETERMINISTIK 5 FILE]"
  python tools/force_approve.py || true
  python fix_parser_all.py || true
  python tools/generate_compatibility.py || true

  git add .
  git commit -m "lingkaran hedeh->koar2 $(date +%H:%M)" || true
  git push origin main
  sleep 90
done
