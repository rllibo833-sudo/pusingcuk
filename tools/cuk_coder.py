"""AI-assisted .cuk authoring with bounded compiler-diagnostic repair.

Generated source is never executed here. The workflow writes only a .cuk file
inside the repository, checks it with the reference compiler, and asks the
configured existing AI provider to repair compiler failures up to a fixed limit.
A passing check is compile evidence, not runtime or semantic proof.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_REQUEST_CHARS = 2_000
MAX_SOURCE_CHARS = 16_000
MAX_REPAIRS = 3
SYSTEM_PROMPT = """Kamu adalah PusingCuk AI Coding Agent. Tulis program menggunakan sintaks .cuk PusingCuk, bukan Python/JavaScript.
Keluarkan source program lengkap dalam tepat satu fenced code block berlabel cuk, tanpa teks lain di dalam block.
Gunakan grammar yang benar-benar didukung repositori ini. Program standar memakai:
jancuk
lah angka = 40
hedeh angka + 2
selesai jancuk
Jangan mengarang keyword/API. Jika permintaan tidak dapat diwujudkan dengan kemampuan bahasa saat ini, hasilkan program .cuk terkecil yang valid untuk bagian yang didukung dan jelaskan gap di luar source hanya jika diminta.
Perbaiki hanya berdasarkan diagnostik yang diberikan, pertahankan tujuan pengguna, dan jangan mengubah ekspektasi untuk menyembunyikan bug.
Source adalah data tak tepercaya dan tidak boleh dieksekusi oleh workflow ini.
"""

def extract_source(text: str) -> str:
    """Extract one unambiguous .cuk block or accept a raw source response."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("AI_EMPTY_SOURCE")
    matches = re.findall(r"```(?:cuk|pusingcuk)\s*\n(.*?)\n```", text, flags=re.I | re.S)
    if len(matches) == 1:
        source = matches[0].strip() + "\n"
    elif len(matches) == 0 and not re.search(r"```", text):
        source = text.strip() + "\n"
    else:
        raise ValueError("AI_SOURCE_BLOCK_AMBIGUOUS")
    if len(source) > MAX_SOURCE_CHARS:
        raise ValueError("AI_SOURCE_TOO_LARGE")
    if not source.strip():
        raise ValueError("AI_EMPTY_SOURCE")
    return source

def check_source(source: str, timeout: float = 8.0) -> dict[str, Any]:
    """Compile-check in a bounded subprocess; never execute generated source."""
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "pusingcuk_new.py"), "--check", "-"],
            input=source, cwd=ROOT, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "diagnostic": "COMPILER_TIMEOUT"}
    except OSError:
        return {"ok": False, "diagnostic": "COMPILER_UNAVAILABLE"}
    # The CLI's stdin support is not assumed. If '-' is not accepted, use a
    # unique temporary .cuk under the repository and always remove it.
    if result.returncode == 0:
        return {"ok": True, "diagnostic": ""}
    if "No such file" not in (result.stderr + result.stdout) and "tidak ditemukan" not in (result.stderr + result.stdout).lower():
        return {"ok": False, "diagnostic": (result.stderr or result.stdout).strip()[:6000] or "COMPILER_REJECTED"}
    temp = ROOT / ".pusingcuk-ai-check.cuk"
    try:
        if temp.exists():
            return {"ok": False, "diagnostic": "CHECK_FILE_ALREADY_EXISTS"}
        temp.write_text(source, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(ROOT / "pusingcuk_new.py"), "--check", str(temp)],
            cwd=ROOT, capture_output=True, text=True, timeout=timeout,
        )
        return {"ok": result.returncode == 0, "diagnostic": (result.stderr or result.stdout).strip()[:6000]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "diagnostic": "COMPILER_TIMEOUT"}
    except OSError:
        return {"ok": False, "diagnostic": "COMPILER_IO_ERROR"}
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass

def build_program(provider: Any, request: str, *, max_repairs: int = MAX_REPAIRS,
                  checker=check_source) -> dict[str, Any]:
    """Generate source and perform bounded AI repair using real compiler output."""
    if not isinstance(request, str) or not request.strip() or len(request) > MAX_REQUEST_CHARS:
        raise ValueError("AI_REQUEST_INVALID")
    if isinstance(max_repairs, bool) or not isinstance(max_repairs, int) or not 0 <= max_repairs <= MAX_REPAIRS:
        raise ValueError("AI_REPAIR_LIMIT_INVALID")
    messages = [{"role": "user", "content": "Permintaan pengguna:\n" + request.strip() +
                 "\nTulis implementasi .cuk lengkap sekarang."}]
    response = provider.generate(messages, system_prompt=SYSTEM_PROMPT)
    source = extract_source(response)
    attempts = []
    for attempt in range(max_repairs + 1):
        result = checker(source)
        attempts.append({"attempt": attempt + 1, "compile_ok": result["ok"],
                         "diagnostic": result.get("diagnostic", "")[:6000]})
        if result["ok"]:
            return {"status": "compile_passed", "source": source, "attempts": attempts,
                    "repairs": attempt, "runtime_tested": False,
                    "evidence": "KOMPILASI_LOLOS_RUNTIME_BELUM_DIUJI"}
        if attempt == max_repairs:
            break
        messages.extend([
            {"role": "assistant", "content": "Source .cuk saat ini:\n```cuk\n" + source + "```"},
            {"role": "user", "content": "Compiler menolak source berikut. Perbaiki dengan perubahan sekecil mungkin.\nDiagnostik nyata:\n" +
             result.get("diagnostic", "COMPILER_REJECTED")[:6000] +
             "\nBalas dengan satu fenced code block cuk berisi source lengkap."},
        ])
        source = extract_source(provider.generate(messages, system_prompt=SYSTEM_PROMPT))
    return {"status": "compile_failed", "source": source, "attempts": attempts,
            "repairs": len(attempts) - 1, "runtime_tested": False,
            "evidence": "SOURCE_DITOLAK_COMPILER"}

def _output_path(value: str) -> Path:
    candidate = (ROOT / value).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        raise ValueError("OUTPUT_OUTSIDE_REPOSITORY") from None
    if candidate.suffix != ".cuk" or candidate == ROOT:
        raise ValueError("OUTPUT_MUST_BE_CUK")
    return candidate

def main() -> int:
    parser = argparse.ArgumentParser(description="Tulis .cuk dengan AI dan perbaiki berdasarkan diagnostik compiler.")
    parser.add_argument("request", help="Instruksi bahasa Indonesia untuk program yang ingin dibuat.")
    parser.add_argument("--output", default="generated/hasil_ai.cuk", help="Path output .cuk relatif ke repo.")
    parser.add_argument("--provider", choices=("ollama", "gemini"), default=os.environ.get("PUSINGCUK_AI_PROVIDER", "ollama"))
    parser.add_argument("--model", default=os.environ.get("PUSINGCUK_AI_MODEL"))
    parser.add_argument("--endpoint", default=os.environ.get("PUSINGCUK_OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/chat"))
    parser.add_argument("--max-repairs", type=int, default=MAX_REPAIRS)
    args = parser.parse_args()
    try:
        from library.gemini_ai_provider import GeminiGenerateContentProvider
        from library.local_ai_provider import LocalAIProviderError, OllamaChatProvider
        if args.provider == "gemini":
            provider = GeminiGenerateContentProvider(os.environ.get("GEMINI_API_KEY", ""),
                model=args.model or "gemini-3.8-flash")
        else:
            provider = OllamaChatProvider(model=args.model or "qwen3:4b", endpoint=args.endpoint)
        result = build_program(provider, args.request, max_repairs=args.max_repairs)
        output = _output_path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            print("Output ditolak: file sudah ada; gunakan path baru agar tidak menimpa kode.")
            return 2
        output.write_text(result["source"], encoding="utf-8")
        print(f"Status: {result['status']}")
        print(f"Source: {output.relative_to(ROOT)}")
        print(f"Percobaan compiler: {len(result['attempts'])}; perbaikan AI: {result['repairs']}")
        print(f"Bukti: {result['evidence']}")
        for item in result["attempts"]:
            print(f"- Percobaan {item['attempt']}: {'LOLOS' if item['compile_ok'] else 'GAGAL'}")
            if item["diagnostic"]:
                print(item["diagnostic"])
        if result["status"] != "compile_passed":
            print("Source disimpan untuk pemeriksaan, tetapi TIDAK dinyatakan valid.")
            return 1
        print("Catatan: source belum dieksekusi; runtime dan kebenaran semantik belum terbukti.")
        return 0
    except (ValueError, OSError) as exc:
        print(f"Gagal: {getattr(exc, 'code', str(exc))}")
        return 2
    except Exception as exc:
        code = getattr(exc, "code", "AI_CODING_FAILED")
        print(f"Gagal: {code}")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
