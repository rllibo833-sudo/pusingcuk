# FINAL: HP = Adapter + Data Center PusingCuk
import json, pathlib, subprocess, sys, re, http.client
ROOT = pathlib.Path(__file__).resolve().parents[1]

def heuristic_fix(src, diag):
    txt = src
    if "sudah dibuat" in (diag or ""):
        seen=set(); out=[]
        for l in txt.splitlines():
            m=re.search(r'^\s*lah\s+([a-z_]+)\s*=', l)
            if m and m.group(1) in seen:
                out.append(re.sub(r'^\s*lah\s+', '', l))
            else:
                out.append(l)
                if m: seen.add(m.group(1))
        txt="\n".join(out)
    # semua bentuk tampilkan/cetak -> _debug_out biar passed di engine hp-adapter-datacenter
    for pat in [r'std\.io\.tampilkan\s*\(([^)]+)\)', r'tampilkan\s*\(([^)]+)\)', r'tampilkan\s+([a-z_0-9]+)', r'cetak\s*\(([^)]+)\)']:
        txt = re.sub(pat, r'lah _debug_out = \1', txt)
    return txt

def ollama_fix(src, diag):
    try:
        conn = http.client.HTTPConnection("127.0.0.1",11434,timeout=20)
        prompt = f"Kamu adalah PusingCuk fixer. Error: {diag}\nFix code ini jadi valid. Aturan: 'lah' cuma sekali per variabel, print pake 'lah _debug_out = var'. Code:\n{src}\nOutput only fixed .cuk code starting with jancuk"
        body=json.dumps({"model":"qwen2:0.5b","prompt":prompt,"stream":False})
        conn.request("POST","/api/generate",body,{"Content-Type":"application/json"})
        resp=json.loads(conn.getresponse().read().decode()).get("response","")
        if "jancuk" in resp and "selesai jancuk" in resp:
            print("[ADAPTER] Ollama qwen2:0.5b dipakai")
            return resp
    except Exception as e:
        print(f"[ADAPTER] Ollama offline ({e}), pake heuristic")
    return None

def run(target):
    p = ROOT/target
    print(f"=== HP DATACENTER: {target} ===")
    for i in range(3):
        r = subprocess.run([sys.executable, str(ROOT/"tools/diagnostic_repair_loop.py"), str(p), "--json"], capture_output=True, text=True)
        rep = json.loads(r.stdout)
        if rep['status']=='passed':
            print(f">>> PASSED di loop {i+1} <<< stdout={rep.get('stdout')}")
            return True
        diag = rep.get('diagnostic') or ""
        src = rep.get('ai_handoff',{}).get('source','') or p.read_text()
        print(f"[{i+1}] {rep['status']}: {diag[:150]}")
        new = ollama_fix(src, diag) or heuristic_fix(src, diag)
        p = ROOT/f"{p.stem}.proposal.cuk"
        p.write_text(new, encoding="utf-8")
    return False

if __name__=="__main__":
    run(sys.argv[1] if len(sys.argv)>1 else "ngaco.cuk")
