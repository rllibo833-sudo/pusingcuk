import json, re
from pathlib import Path

KOS = Path("library/kosakata.json")
PARSER = Path("parser.py")

txt = KOS.read_text()
# ambil semua alias hedeh dari 2 format
aliases = set()

# format 1: "hedeh": ["spill","print",...]
m = re.search(r'"hedeh"\s*:\s*\[(.*?)\]', txt, re.S)
if m:
    aliases.update(re.findall(r'"([^"]+)"', m.group(1)))

# format 2: "word":"hedeh", "aliases":[...]
for mm in re.finditer(r'"word"\s*:\s*"hedeh".*?"aliases"\s*:\s*\[(.*?)\]', txt, re.S):
    aliases.update(re.findall(r'"([^"]+)"', mm.group(1)))

aliases = sorted([a for a in aliases if a != "hedeh"])
print(f"[FOUND] hedeh aliases = {aliases}")

# patch parser.py: ganti line 162 jadi semua alias
p = PARSER.read_text()
# hapus patch lama biar bersih
p = re.sub(r'if self\.at\("hedeh"\)(?: or self\.at\("[^"]+"\)+)*:', 'if self.at("hedeh"):', p)

# bikin patch baru: if self.at("hedeh") or self.at("spill") or self.at("print") or ...
or_part = "".join([f' or self.at("{a}")' for a in aliases])
new_if = f'if self.at("hedeh"){or_part}:'

p = p.replace('if self.at("hedeh"):', new_if, 1)

PARSER.write_text(p)
print(f"[PATCHED] {new_if}")

# test
Path("app.cuk").write_text('jancuk\n' + '\n'.join([f'{a} "OK {a}"' for a in aliases]) + '\nselesai jancuk')
print(Path("app.cuk").read_text())

import importlib, parser
importlib.reload(parser)
try:
    parser.parse(Path("app.cuk").read_text())
    print("[ENGINE OK] Semua alias jalan!")
except Exception as e:
    print(f"[FAIL] {e}")
