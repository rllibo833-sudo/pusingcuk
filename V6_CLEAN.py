import json, re
from pathlib import Path

# 1. Gabungin kosakata
p = Path("library/kosakata.json")
data = json.loads(p.read_text())
# ambil dari 2 tempat
all_alias = set()
if "hedeh" in data and isinstance(data["hedeh"], list):
    all_alias.update(data["hedeh"])
for k in data.get("keywords", []):
    if k.get("word")=="hedeh":
        all_alias.update(k.get("aliases",[]))

# tambah yang di git log terakhir yang belum masuk
all_alias.update(["nyalak","senggol","semprot","muncrat","berak","crot","senggol"])
all_alias = sorted([x for x in all_alias if x])

# tulis balik dengan 1 format doang yang bener
for k in data["keywords"]:
    if k["word"]=="hedeh":
        k["aliases"]=all_alias
# hapus format lama dobel
if "hedeh" in data: del data["hedeh"]
data["hedeh_legacy"]=all_alias # simpan buat kompatibilitas

p.write_text(json.dumps(data, indent=2))
print(f"[KOSAKATA FIX] hedeh = {all_alias} total {len(all_alias)}")

# 2. Patch parser sekali jadi
parser = Path("parser.py").read_text()
parser = re.sub(r'if self\.at\("hedeh"\)(?: or self\.at\("[^"]+"\)+)*:', 'if self.at("hedeh"):', parser)
or_part = "".join([f' or self.at("{a}")' for a in all_alias])
new_if = f'if self.at("hedeh"){or_part}:'
parser = parser.replace('if self.at("hedeh"):', new_if, 1)
Path("parser.py").write_text(parser)
print(f"[PARSER FIX] {new_if[:120]}...")

# 3. Fix app.cuk biar gak dibalikin adapter
Path("app.cuk").write_text('jancuk\nhedeh "Siklus V6 OK - "+ "HP jadi datacenter"\nselesai jancuk\n')
print("[APP.CUK FIX] locked")

