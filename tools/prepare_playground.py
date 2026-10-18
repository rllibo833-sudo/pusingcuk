#!/usr/bin/env python3
"""Bundle the repository's actual reference interpreter modules for the Pyodide playground."""
from __future__ import annotations
import json
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
RUNTIME = SITE / "runtime"
MODULES = ("pusingcuk_new.py", "evaluator.py", "parser.py", "lexer.py", "ast_nodes.py", "library/stdlib.py", "library/builtin_contract.py")
def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for relative in MODULES:
        source, destination = ROOT / relative, RUNTIME / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    (RUNTIME / "library" / "__init__.py").write_text('"""Bundled PusingCuk runtime package."""\n', encoding="utf-8")
    examples_dir = SITE / "examples" / "playground"
    entries = [{"title": source.stem.replace("_", " ").replace("-", " ").title(), "file": source.name, "url": "examples/playground/" + source.name} for source in sorted(examples_dir.glob("*.pusingcuk"))]
    if not 5 <= len(entries) <= 10:
        raise SystemExit(f"Galeri harus berisi 5-10 contoh .pusingcuk; ditemukan {len(entries)}")
    (RUNTIME / "playground-examples.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Bundled {len(MODULES)} interpreter modules and {len(entries)} examples.")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
