# FLOW: TERMUX -> OLLAMA -> CUK REALITY ENGINE -> GITHUB -> TERMUX
import json, pathlib, subprocess, sys, re, http.client
ROOT = pathlib.Path(__file__).resolve().parents[1]

def ollama_first(src, diag):
    # OLLAMA DULUAN - sesuai alur lu
    try:
        conn = http.client.HTTPConnection("127.0.0.1",11434,timeout=30)
        prompt = f"Fix PusingCuk code. Error: {diag}\nRule: 'lah' only once per var, no tampilkan/cetak, use 'lah _out = var'. Code:\n{src}\nOutput only fixed code jancuk..selesai jancuk"
        body=json.dumps({"model":"qwen2:0.5b","prompt":prompt,"stream":False})
        conn.request("POST","/api/generate",body,{"Content-Type":"application/json"})
        resp=json.loads(conn.getresponse().read()).get("response","")
        if "jancuk" in resp:
            return resp
    except: pass
    return None

def heuristic(src, diag):
    # fallback kalo Ollama lagi tidur / batre 30% lu tadi
    txt=src
    if "sudah dibuat" in (diag or ""):
        seen=set(); out=[]
        for l in txt.splitlines():
            m=re.search(r'^\s*lah\s+([a-z_]+)\s*=', l)
            if m and m.group(1) in seen:
                out.append(re.sub(r'^\s*lah\s+', '', l))
            else:
                out.append(l); 
                if m: seen.add(m.group(1))
        txt="\n".join(out)
    txt=re.sub(r'(std\.io\.tampilkan|tampilkan|cetak)\s*\(?([^\)]*)\)?', r'lah _out = \2', txt)
    txt=re.sub(r'tampilkan\s+([a-z_]+)', r'lah _out = \1', txt)
    return txt

def run(target):
    p=ROOT/target
    print(f"TERMUX -> OLLAMA -> CUK REALITY ENGINE: {target}")
    for i in range(3):
        # CUK REALITY ENGINE
        r=subprocess.run([sys.executable, str(ROOT/"tools/diagnostic_repair_loop.py"), str(p), "--json"], capture_output=True, text=True)
        rep=json.loads(r.stdout)
        if rep['status']=='passed':
            print(f"CUK REALITY ENGINE: PASSED -> siap push ke GITHUB")
            return True
        diag=rep.get('diagnostic') or ""
        src=rep.get('ai_handoff',{}).get('source','') or p.read_text()
        print(f"[{i+1}] {rep['status']}: {diag[:100]}")
        # OLLAMA DULUAN, baru heuristic
        new = ollama_first(src, diag) or heuristic(src, diag)
        p=ROOT/f"{p.stem}.proposal.cuk"
        p.write_text(new, encoding="utf-8")
    return False

if __name__=="__main__":
    run(sys.argv[1] if len(sys.argv)>1 else "contoh.cuk")
