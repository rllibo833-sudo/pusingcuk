import json, subprocess, sys
from pathlib import Path
SPEC=Path("library/kosakata.json")
def propose(canonical, new_alias):
    kos=json.loads(SPEC.read_text())
    if canonical not in kos: kos[canonical]=[]
    if new_alias in kos[canonical]:
        print(f"Alias {new_alias} sudah ada di {canonical}"); return False
    kos[canonical].append(new_alias)
    SPEC.write_text(json.dumps(kos, indent=2, ensure_ascii=False))
    print(f"[PROPOSE] {canonical} += {new_alias}")
    r=subprocess.run(["python","-m","pytest","tests/test_lexer.py","tests/test_parser.py","-q"], capture_output=True, text=True)
    if r.returncode!=0:
        print("[REJECT] Gagal test, rollback"); kos[canonical].remove(new_alias); SPEC.write_text(json.dumps(kos, indent=2)); print(r.stdout[-500:]); return False
    print("[ACCEPT] Lolos deterministik")
    return True
def main():
    txt=Path("next_prompt.txt").read_text() if Path("next_prompt.txt").exists() else ""
    prompt=(sys.argv[1] if len(sys.argv)>1 else txt).strip().lower()
    print(f"Prompt: {prompt}")
    if "tambah alias" in prompt:
        try:
            p=prompt.split(); new_alias=p[2].strip('"'); canonical=p[4].strip('"')
            if propose(canonical, new_alias):
                subprocess.run(["git","add","-A"]); subprocess.run(["git","commit","-m",f"evolve: {new_alias}->{canonical}"]); subprocess.run(["git","push"])
                print("[EVOLVED] Pushed")
        except Exception as e:
            print(f"Format: tambah alias tampilkan untuk hedeh | error {e}")
    else:
        print("Contoh: echo 'tambah alias cetak untuk hedeh' > next_prompt.txt")
if __name__=="__main__": main()
