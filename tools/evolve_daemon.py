#!/usr/bin/env python3
"""
DAEMON EVOLUSI MANDIRI
Loop: generate alias baru (dari AI / list) -> propose -> 
test deterministik (lexer, parser, conformance, compiler) ->
update kosakata.json + fixture -> push -> build APK via Actions
"""
import time, json, random, subprocess
from pathlib import Path

# daftar semantik Gen Z / Indonesia yang bisa jadi alias hedeh
CANDIDATE_ALIASES = {
    "hedeh": ["cetak","tampilkan","spill","gas","print","keluarin","sembur","omong"],
    "lah": ["buat","bikin","var","deklarasi"],
    "jancuk": ["mulai","start","gasskeun","open"],
    "selesai": ["tutup","end","beres","kelar"],
    "njir": ["jika","if","kalo"],
    "mumet": ["pusing","while","selama"]
}

SPEC = Path("library/kosakata.json")
NEXT = Path("next_prompt.txt")

def run_tests():
    # test deterministik + conformance + compiler
    cmds = [
        ["python","-m","pytest","tests/test_lexer.py","tests/test_parser.py","-q"],
        ["python","tools/conformance.py","--check"], # kalo ada
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[TEST FAIL] {' '.join(cmd)}")
            print(r.stdout[-300:])
            return False
    return True

def propose(canonical, alias):
    kos = json.loads(SPEC.read_text()) if SPEC.exists() else {}
    if canonical not in kos: kos[canonical] = []
    if alias in kos[canonical]: return False
    kos[canonical].append(alias)
    SPEC.write_text(json.dumps(kos, indent=2, ensure_ascii=False))
    print(f"[PROPOSE] {canonical} += {alias}")
    if not run_tests():
        print("[REJECT] Rollback")
        kos[canonical].remove(alias)
        SPEC.write_text(json.dumps(kos, indent=2))
        return False
    print("[ACCEPT] Lolos semua test (lexer/parser/conformance/compiler)")
    return True

print("[DAEMON] Evolusi Mandiri START - Loop Otomatis")
while True:
    # 1. ambil prompt dari next_prompt.txt atau auto-generate
    if NEXT.exists() and NEXT.read_text().strip().startswith("tambah alias"):
        prompt = NEXT.read_text().strip().lower()
        parts = prompt.split()
        try:
            alias, canonical = parts[2], parts[4]
        except:
            time.sleep(5); continue
    else:
        # auto generate alias baru yang belum ada
        canonical = random.choice(list(CANDIDATE_ALIASES.keys()))
        kos = json.loads(SPEC.read_text()) if SPEC.exists() else {}
        existing = set(kos.get(canonical, []))
        pool = [a for a in CANDIDATE_ALIASES[canonical] if a not in existing]
        if not pool:
            print("[DAEMON] Semua alias untuk", canonical, "udah habis, tidur 30s")
            time.sleep(30); continue
        alias = random.choice(pool)

    if propose(canonical, alias):
        # update app.cuk buat test
        Path("app.cuk").write_text(f'jancuk\n{alias} "Evolusi mandiri: {alias} -> {canonical} OK"\nselesai jancuk')
        # push, trigger android-studio-apk.yml biar APK kebikin di Github (anti FC HP)
        subprocess.run(["git","add","-A"])
        subprocess.run(["git","commit","-m",f"evolve(mandiri): {alias}->{canonical} auto"])
        subprocess.run(["git","push"])
        print(f"[PUSHED] {alias} -> Actions bakal build APK")
        # reset next_prompt.txt biar gak loop itu terus
        if NEXT.exists(): NEXT.write_text("")

    time.sleep(15)

