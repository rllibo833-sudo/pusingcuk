#!/data/data/com.termux/files/usr/bin/bash
while true; do
  git pull origin main --rebase || true
  pgrep ollama || (ollama serve > ~/ollama.log 2>&1 & sleep 3)
  export OLLAMA_MODEL=llama3.2:1b
  
  # FIX: paksa pakai llama3.2:1b biar gak MODEL_NOT_FOUND lagi
  sed -i 's/qwen2:0.5b/llama3.2:1b/g; s/tinyllama:latest/llama3.2:1b/g' tools/evaluate_live_ai.py tools/local_ai_adapter.py 2>/dev/null || true

  echo "[ADAPTER] termux -> ollama"
  python tools/local_ai_adapter.py || true
  python tools/reality_engine.py || true
  echo "[DATACENTER] evaluate"
  python tools/evaluate_live_ai.py || true

  echo "[FIX DETERMINISTIK]"
  python tools/evolve_language.py hedeh koar2 || true
  python tools/force_approve.py || true
  python fix_parser_all.py || true
  python tools/generate_compatibility.py || true

  echo "[PUSH] github -> termux"
  git add .
  git commit -m "lingkaran full hedeh->koar2 $(date +%H:%M)" || true
  git push origin main
  sleep 120
done
