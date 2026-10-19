#!/usr/bin/env python3
import sys, re
from pathlib import Path
from evaluator import run as eval_run
from parser import parse as parse_source
PROMPT = " ".join(sys.argv[1:]) if len(sys.argv)>1 else ""
print(f"[1] HP -> Pusingcuk AI Lite: '{PROMPT}'")
code=["jancuk"]
if "dunia" in PROMPT.lower() or "halo" in PROMPT.lower():
    code.append('lah nama = "Dunia"')
    code.append('hedeh "Halo, " + nama')
m=re.findall(r'(\d+)',PROMPT)
if len(m)>=2:
    a,b=m[0],m[1]
    code.append(f'fungsi tambah(a, b)')
    code.append(f'    balek a + b')
    code.append(f'selesai fungsi')
    code.append(f'hedeh tambah({a}, {b})')
else:
    code.append('fungsi tambah(a, b)')
    code.append('    balek a + b')
    code.append('selesai fungsi')
    code.append('hedeh tambah(20, 22)')
code.append('selesai jancuk')
cuk_code="\n".join(code)
Path("app.cuk").write_text(cuk_code,encoding="utf-8")
print(f"[2] .cuk baru:\n{cuk_code}\n")
print("[3] Reality Engine --check")
try:
    src=Path("app.cuk").read_text(encoding="utf-8")
    parse_source(src)
    print("  CHECK OK")
except Exception as e:
    print(f"  CHECK ERROR: {e}"); sys.exit(1)
print("[5] Reality Engine -> RUN")
eval_run(src)
print("\n[DONE] Anti FC")
