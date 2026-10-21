"""Multi-target command line interface for PusingCuk compilers."""
import argparse
import json
import sys
from pathlib import Path

from compiler.ir import from_source
from library.module_system import expand_file


def compile_source(source, source_name, target):
    ir = from_source(source, source_name)
    if target == "json":
        return json.dumps(ir, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if target == "vm":
        from compiler.bytecode import compile_ir
        return json.dumps(compile_ir(ir), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if target == "android":
        from compiler.android_backend import generate
        return generate(ir)
    if target == "c":
        from compiler.c_backend import generate
        return generate(ir)
    if target == "cpp":
        from compiler.cpp_backend import generate
        return generate(ir)
    if target == "js":
        from compiler.js_backend import generate
        return generate(ir)
    if target == "python":
        from compiler.python_backend import generate
        return generate(ir)
    if target == "go":
        from compiler.go_backend import generate
        return generate(ir)
    if target == "html":
        from compiler.js_backend import generate
        js = generate(ir)
        # Prevent source strings from terminating the enclosing script element.
        js = js.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")
        return """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PusingCuk Web</title>
<style>
body{font:16px system-ui,sans-serif;max-width:850px;margin:2rem auto;padding:0 1rem;background:#f5f8ff;color:#14213d}
h1{color:#174ea6}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#101828;color:#e6edf3;padding:1rem;border-radius:12px;min-height:8rem}
small{color:#475569}
</style>
</head>
<body>
<h1>PusingCuk Web</h1>
<p>Program PusingCuk yang dikompilasi menjadi JavaScript.</p>
<small>Output program:</small><pre id="pc-output"></pre>
<script>
const pcOutput = document.getElementById("pc-output");
console.log = (...values) => { pcOutput.textContent += values.join(" ") + "\\n"; };
""" + js + """
</script>
</body>
</html>
"""
    raise ValueError("target tidak dikenal")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compiler multi-target PusingCuk")
    parser.add_argument("file", help="file sumber .pusingcuk")
    parser.add_argument("-t", "--target", choices=("js", "python", "c", "cpp", "go", "rust", "json", "html", "vm", "android"), default="js")
    parser.add_argument("-o", "--output", help="file keluaran; default stdout")
    args = parser.parse_args(argv)
    source_path = Path(args.file)
    if not source_path.is_file():
        print(f"berkas tidak ditemukan: {source_path}", file=sys.stderr)
        return 2
    try:
        # Expand only explicit, local, project-root-confined .pusingcuk imports.
        source = expand_file(source_path)
        result = compile_source(source, source_path.name, args.target)
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            sys.stdout.write(result)
    except (SyntaxError, ValueError, TypeError, OSError) as exc:
        print(f"kompilasi gagal: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
