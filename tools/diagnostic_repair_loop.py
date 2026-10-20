import sys, pathlib
from lexer import Lexer
from parser import Parser
ROOT=pathlib.Path(__file__).parents[1]
p=pathlib.Path(sys.argv[1])
src=p.read_text()
try:
    toks=Lexer(src).tokenize()
    ast=Parser(toks).parse()
    print(f"CHECK OK - token: {len(toks)}")
    if "--json" in sys.argv:
        import json; print(json.dumps({"ok":True,"tokens":len(toks)}))
    sys.exit(0)
except Exception as e:
    print(f"CHECK ERROR: {e}")
    import json
    if "--json" in sys.argv:
        print(json.dumps({"ok":False,"error":str(e),"diag":str(e)}))
    sys.exit(1)
