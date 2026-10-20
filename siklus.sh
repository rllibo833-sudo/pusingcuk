#!/data/data/com.termux/files/usr/bin/bash
while true; do
  # PASTIKAN OLLAMA JALAN + MODEL KE-LOAD
  pgrep ollama || (ollama serve > ~/ollama.log 2>&1 & sleep 3)
  ollama list
  ollama run qwen2:0.5b "" || ollama run llama3.2:1b "" || echo "no model"

  echo "[1/6] reality_engine"
  python tools/reality_engine.py || true

  echo "[2/6] evaluate_live_ai"
  # set model yang ada
  export PUSINGCUK_MODEL=qwen2:0.5b
  export OLLAMA_MODEL=qwen2:0.5b
  python tools/evaluate_live_ai.py || true

  echo "[3/6] adapter"
  python tools/local_ai_adapter.py || true
  ls tools/ | grep -i compat
  python tools/generate_compatibility.py 2>/dev/null || python tools/compatibility_report.py 2>/dev/null || echo "compat skip"

  echo "[4/6] evolve - YANG BENER POSITIONAL"
  python tools/evolve_language.py hedeh koar2 || true
  python tools/evolve_daemon.py --canonical hedeh --alias koar2 || true

  echo "[5/6] datacenter"
  python datacenter_v6.py --canonical hedeh --alias koar2 || true
  sed -i 's/hedeh/hedeh | koar2/g' SPEC.md 2>/dev/null || true

  echo "[6/6] push"
  git add .
  git commit -m "auto evolve: $(date) hedeh->koar2" || echo "nothing"
  git push origin main || true

  sleep 300
done
