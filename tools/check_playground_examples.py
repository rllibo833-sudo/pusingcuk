#!/usr/bin/env python3
"""Verify every browser gallery example with the reference interpreter and reject unsafe capabilities."""
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "site" / "examples" / "playground"
INTERPRETER = ROOT / "pusingcuk_new.py"
FORBIDDEN = re.compile(r"\b(tanya|tulis|baca|angkut|tulis_json|baca_json|jadi_json|jadi_teks|json_teks|json_baca|kepo_internet|kirim_api|kirim_gosip|gas_api|stalking)\b|\b(?:json|web|tabel)\s*\.", re.I)
def main() -> int:
    files = sorted(EXAMPLES.glob("*.pusingcuk"))
    if not 5 <= len(files) <= 10:
        print(f"Expected 5-10 gallery examples, got {len(files)}", file=sys.stderr); return 1
    for source in files:
        text = source.read_text(encoding="utf-8")
        if FORBIDDEN.search(text) or re.search(r"^\s*tanya\s+", text, re.M):
            print(f"Unsupported file/network/JSON/interactive-input operation in {source.relative_to(ROOT)}", file=sys.stderr); return 1
        expected_path = source.with_suffix(".expected.txt")
        if not expected_path.is_file():
            print(f"Missing expected output: {expected_path.name}", file=sys.stderr); return 1
        expected = expected_path.read_text(encoding="utf-8")
        result = subprocess.run([sys.executable, str(INTERPRETER), str(source)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, check=False)
        if result.returncode != 0 or result.stderr or result.stdout != expected:
            print(f"Reference interpreter mismatch: {source.name}\nexpected={expected!r}\nstdout={result.stdout!r}\nstderr={result.stderr!r}\nexit={result.returncode}", file=sys.stderr); return 1
        print(f"PASS {source.name}")
    print(f"PASS: {len(files)} browser examples match the reference interpreter."); return 0
if __name__ == "__main__":
    raise SystemExit(main())
