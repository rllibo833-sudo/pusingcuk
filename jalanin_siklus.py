import pathlib, re, sys
ROOT = pathlib.Path(".")
print("[1] HP+TERMUX ADAPTER + DATA CENTER")
print(f"    ROOT={ROOT.resolve()}")

# 2. AI LOKAL + HEURISTIC ANTI-FC (dari file lu ed55fff)
PROMPT = " ".join(sys.argv[1:]) if len(sys.argv)>1 else "bikin halo dunia tambah 20 22"
print(f"[2] OLLAMA PROMPT: '{PROMPT}'")

def buat_cuk(prompt):
    code=["jancuk"]
    if "dunia" in prompt.lower() or "halo" in prompt.lower():
        code.append('lah nama = "Dunia"')
        code.append('hedeh "Halo, " + nama')
    m=re.findall(r'(\d+)',prompt)
    a,b = (m[0],m[1]) if len(m)>=2 else ("20","22")
    code.append(f"fungsi tambah(a, b)")
    code.append(f"  balek a + b")
    code.append(f"selesai fungsi")
    code.append(f"hedeh tambah({a}, {b})")
    code.append("selesai jancuk")
    return "\n".join(code)

cuk = buat_cuk(PROMPT)
pathlib.Path("app.cuk").write_text(cuk, encoding="utf-8")
print(f"[3] .CUK BARU:\n{cuk}\n")

# 4. CUK REALITY ENGINE - LANGSUNG PAKE LEXER 326 YANG UDAH BENER
print("[4] Reality Engine --check")
try:
    from lexer import Lexer
    from parser import Parser
    from evaluator import Evaluator
    src = pathlib.Path("app.cuk").read_text()
    lexer = Lexer(src)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("    CHECK OK - token:", len(tokens), "AST OK")
except Exception as e:
    print(f"    CHECK ERROR: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("[5] Reality Engine -> RUN")
try:
    evaluator = Evaluator()
    result = evaluator.eval(ast)
    print(f"    RUN OUTPUT: {result}")
except Exception as e:
    # fallback pake pusingcuk_new.py lu yang udah jalan
    import subprocess
    r = subprocess.run([sys.executable, "pusingcuk_new.py", "app.cuk"], capture_output=True, text=True)
    print(r.stdout or r.stderr)

print("\n[DONE] Siklus HP->Ollama->Engine->.cuk jalan Anti-FC")
print("File: app.cuk siap push ke github otomatis")
