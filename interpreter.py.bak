import sys, re, json, pathlib
from parser import parse
from evaluator import run
KOS=pathlib.Path("library/kosakata.json")
def load_alias():
  try:
    d=json.loads(KOS.read_text()); m={}
    for canon, aliases in d.items():
      for a in aliases: m[a]=canon
    return m
  except: return {}
ALIAS=load_alias()
def normalize(src):
  for a,c in sorted(ALIAS.items(), key=lambda x: -len(x[0])):
    src=re.sub(rf'\b{re.escape(a)}\b', c, src)
  return src
src=pathlib.Path(sys.argv[1]).read_text(); src=normalize(src)
parse(src); run(src)
