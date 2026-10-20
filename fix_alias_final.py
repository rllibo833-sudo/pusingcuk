import pathlib, json, re
ROOT=pathlib.Path(".")
spec= (ROOT/"SPEC.md").read_text(encoding="utf-8")
section = spec[spec.index("## 16. Alias kosakata"):spec.index("## 17.")]
core_section, api_section = section.split("### Alias API tambahan", 1)

def parse_spec_aliases(text):
    aliases={}
    for line in text.splitlines():
        if line.startswith("- `") and "` → `" in line:
            alias=line.split("`",2)[1]
            canonical=line.split("` → `",1)[1].split("`",1)[0]
            aliases[alias]=canonical
    return aliases

core_aliases=parse_spec_aliases(core_section)
all_aliases={**core_aliases, **parse_spec_aliases(api_section)}
print(f"SPEC: all={len(all_aliases)} core={len(core_aliases)}")
print("all:", all_aliases)
print("core:", core_aliases)
assert len(all_aliases)==23 and len(core_aliases)==12, f"spec lu beda! cek SPEC.md"

# 1. Fix native/pusingcuk.c
nc_path=ROOT/"native"/"pusingcuk.c"
txt=nc_path.read_text(encoding="utf-8")
# cari block aliases[] = { ... };
m=re.search(r'static const struct \{ const char \*alias, \*canonical; \} aliases\[\] = \{.*?\n    \};', txt, flags=re.DOTALL)
if not m:
    print("gak nemu block aliases di native/pusingcuk.c")
else:
    lines=[f'        {{"{k}", "{v}"}},' for k,v in sorted(core_aliases.items())]
    new_block='static const struct { const char *alias, *canonical; } aliases[] = {\n' + "\n".join(lines) + "\n    };"
    txt=txt[:m.start()]+new_block+txt[m.end():]
    nc_path.write_text(txt, encoding="utf-8")
    print("fixed native/pusingcuk.c ->", len(core_aliases), "entries")

# 2. Fix library/kosakata.json
kj_path=ROOT/"library"/"kosakata.json"
data=json.loads(kj_path.read_text(encoding="utf-8"))
# group by canonical
from collections import defaultdict
group=defaultdict(list)
for alias, canon in all_aliases.items():
    group[canon].append(alias)

keywords=[]
for canon in sorted(group.keys()):
    keywords.append({"word": canon, "aliases": sorted(group[canon])})

data["keywords"]=keywords
# pastikan version keys ada
import tomllib
pkg=tomllib.loads((ROOT/"pyproject.toml").read_text(encoding="utf-8"))
data["package_version"]=pkg["project"]["version"]
data["language_version"]=pkg["tool"]["pusingcuk"]["language-version"]
kj_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"fixed kosakata.json -> {len(keywords)} keywords, {len(all_aliases)} alias total")

# 3. Pastikan lexer.py sudah literal (yang kemarin)
# kalau belum, regen lagi
lex_path=ROOT/"lexer.py"
if 'KEYWORD_ALIASES = {**' in lex_path.read_text():
    print("lexer.py masih pakai **, regen...")
    import subprocess, sys
    subprocess.run([sys.executable, "lexer_fix.py"])
