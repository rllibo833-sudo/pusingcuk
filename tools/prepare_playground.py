#!/usr/bin/env python3
"""Bundle the repository's actual reference interpreter modules for the Pyodide playground."""
from __future__ import annotations
import json
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
RUNTIME = SITE / "runtime"
RUNTIME_FILES = ("pusingcuk_new.py", "evaluator.py", "parser.py", "lexer.py", "ast_nodes.py", "library/stdlib.py", "library/builtin_contract.py", "library/builtin_contract.json")
def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for relative in RUNTIME_FILES:
        source, destination = ROOT / relative, RUNTIME / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    (RUNTIME / "library" / "__init__.py").write_text('"""Bundled PusingCuk runtime package."""\n', encoding="utf-8")
    examples_dir = SITE / "examples" / "playground"
    entries = [{"title": source.stem.replace("_", " ").replace("-", " ").title(), "file": source.name, "url": "examples/playground/" + source.name} for source in sorted(examples_dir.glob("*.pusingcuk"))]
    if not 5 <= len(entries) <= 10:
        raise SystemExit(f"Galeri harus berisi 5-10 contoh .pusingcuk; ditemukan {len(entries)}")
    manifest = RUNTIME / "playground-examples.json"
    manifest.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    # builtin_contract.py reads this adjacent JSON file at import time. Missing
    # it makes every browser example fail before user code can execute.
    contract = RUNTIME / "library" / "builtin_contract.json"
    if not contract.is_file():
        raise SystemExit("Missing bundled library/builtin_contract.json")
    try:
        contract_data = json.loads(contract.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Invalid bundled builtin contract: {exc}") from exc
    if contract_data.get("schema_version") != 1 or not contract_data.get("builtins"):
        raise SystemExit("Bundled builtin contract failed its schema smoke check")
    for entry in entries:
        if not (SITE / entry["url"]).is_file():
            raise SystemExit(f"Missing gallery source: {entry['url']}")
        if not (SITE / "examples" / "playground" / Path(entry["file"]).with_suffix(".expected.txt").name).is_file():
            raise SystemExit(f"Missing expected output for {entry['file']}")
    print(f"Bundled {len(RUNTIME_FILES)} interpreter runtime files and {len(entries)} examples; builtin contract verified.")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
