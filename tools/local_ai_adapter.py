"""Local Ollama proposal adapter for PusingCuk source diagnostics."""
from __future__ import annotations

import http.client
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.diagnostic_repair_loop import run_case
from tools.reality_engine import validate_deterministic


def ollama_first(src, diag):
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 11434, timeout=30)
        prompt = (
            f"Fix PusingCuk code. Error: {diag}\n"
            "Rule: 'lah' only once per var, no tampilkan/cetak, use 'lah _out = var'. "
            f"Code:\n{src}\nOutput only fixed code jancuk..selesai jancuk"
        )
        body = json.dumps({"model": os.environ.get("OLLAMA_MODEL", "llama3.2:1b"), "prompt": prompt, "stream": False})
        conn.request("POST", "/api/generate", body, {"Content-Type": "application/json"})
        response = json.loads(conn.getresponse().read()).get("response", "")
        if "jancuk" in response:
            return response
    except (OSError, ValueError, http.client.HTTPException):
        pass
    return None


def heuristic(src, diag):
    text = src
    if "sudah dibuat" in (diag or ""):
        seen = set()
        output = []
        for line in text.splitlines():
            match = re.search(r"^\s*lah\s+([a-z_]+)\s*=", line)
            if match and match.group(1) in seen:
                output.append(re.sub(r"^\s*lah\s+", "", line))
            else:
                output.append(line)
                if match:
                    seen.add(match.group(1))
        text = "\n".join(output)
    text = re.sub(r"(std\.io\.tampilkan|tampilkan|cetak)\s*\(?([^\)]*)\)?", r"lah _out = \2", text)
    text = re.sub(r"tampilkan\s+([a-z_]+)", r"lah _out = \1", text)
    return text


def _diagnostic_text(report):
    items = report.get("diagnostic", [])
    if isinstance(items, str):
        return items
    return "\n".join(
        f"Baris {item.get('line', 0)}: {item.get('msg', '')}"
        for item in items if isinstance(item, dict)
    )


def run(target):
    original = pathlib.Path(target)
    original = original if original.is_absolute() else ROOT / original
    original = original.resolve()
    proposal = original.with_name(f"{original.stem}.proposal.cuk")
    current = original

    for attempt in range(3):
        report = run_case(current)
        source = report.get("ai_handoff", {}).get("source", "")
        if report["status"] == "passed":
            if current == original:
                print("PusingCuk source syntax is valid; no repair proposal was accepted")
                return True
            gate = validate_deterministic(source=source)
            if not gate["accepted"]:
                details = "; ".join(item.get("msg", "") for item in gate.get("diagnostic", []))
                print(f"Reality Engine REJECTED proposal: {details}", file=sys.stderr)
                return False
            print("Reality Engine verified proposal against an existing canonical fixture; no new fixture was added")
            return True

        diagnostic = _diagnostic_text(report)
        source = report.get("ai_handoff", {}).get("source", "")
        if not source:
            try:
                source = current.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                return False
        print(f"[{attempt + 1}] {report['status']}: {diagnostic[:160]}", file=sys.stderr)
        proposed = ollama_first(source, diagnostic) or heuristic(source, diagnostic)
        proposal.write_text(proposed, encoding="utf-8")
        current = proposal

    return False


if __name__ == "__main__":
    raise SystemExit(0 if run(sys.argv[1] if len(sys.argv) > 1 else "halo.cuk") else 1)
