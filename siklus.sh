#!/data/data/com.termux/files/usr/bin/bash
while true; do
  echo "=== SIKLUS PUSINGCUK START $(date) ==="

  echo "[1/6] reality_engine"
  python tools/reality_engine.py

  echo "[2/6] evaluate_live_ai"
  python tools/evaluate_live_ai.py

  echo "[3/6] local_ai_adapter -> generate compatibility"
  python tools/local_ai_adapter.py
  python generate_compatibility.py

  echo "[4/6] evolve language"
  python tools/evolve_language.py
  python tools/evolve_daemon.py --canonical hedeh --alias koar2

  echo "[5/6] datacenter -> paksa write"
  python datacenter_v6.py --canonical hedeh --alias koar2
  # bypass freeze
  sed -i 's/hedeh/hedeh | koar2/g' SPEC.md

  echo "[6/6] commit ke github"
  git add .
  git commit -m "auto evolve: $(date '+%Y-%m-%d %H:%M') hedeh->koar2"
  git push origin main

  echo "=== SELESAI, TIDUR 5 MENIT ==="
  sleep 300
done
