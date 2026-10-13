#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
CC=clang
if [[ -n "${TMPDIR:-}" ]]; then
  TMP_BASE="$TMPDIR"
elif [[ -n "${PREFIX:-}" && -d "$PREFIX/tmp" ]]; then
  TMP_BASE="$PREFIX/tmp"
else
  TMP_BASE=/tmp
fi
TMP="$TMP_BASE/pusingcuk-pvm-test-$$"
RUN_DIR="$TMP/run"
mkdir -p "$RUN_DIR/tests"
trap 'rm -rf "$TMP"' EXIT

"$CC" -std=c11 -O2 -Wall -Wextra -Werror src/c-core/main.c -o "$TMP/pvmc"
command -v node >/dev/null || { echo "Node.js dibutuhkan untuk uji JS" >&2; exit 2; }
python3 --version >/dev/null
PYTHONPATH="$ROOT" python3 tests/test_python_importer.py
printf 'fixture file I/O\n' > "$RUN_DIR/tests/pusingcuk-pvm-test.txt"

# Keep pure-language samples as a Python/JS parity set. File I/O is tested
# separately because JS disables those opcodes and Python requires an explicit
# trusted-program capability flag.
for src in tests/0[1-6]_*.cuk; do
  [[ "$src" == "tests/05_file_io.cuk" ]] && continue
  name="$(basename "$src" .cuk)"
  "$TMP/pvmc" "$src" "$TMP/$name.pvm"
  node src/backends/js/compiler.js "$TMP/$name.pvm" "$TMP/$name.js"
  python3 src/backends/python/compiler.py "$TMP/$name.pvm" "$TMP/$name.py"
  (cd "$RUN_DIR" && node "$TMP/$name.js") > "$TMP/$name.js.out"
  (cd "$RUN_DIR" && python3 "$TMP/$name.py") > "$TMP/$name.py.out"
  diff -u "$TMP/$name.js.out" "$TMP/$name.py.out"
  echo "PASS: $name (JS/Python parity)"
done

"$TMP/pvmc" tests/05_file_io.cuk "$TMP/05_file_io.pvm"
node src/backends/js/compiler.js "$TMP/05_file_io.pvm" "$TMP/05_file_io.js"
python3 src/backends/python/compiler.py "$TMP/05_file_io.pvm" "$TMP/05_file_io.py"
if (cd "$RUN_DIR" && node "$TMP/05_file_io.js") >"$TMP/05_file_io.js.out" 2>"$TMP/05_file_io.js.err"; then
  echo "FAIL: JS PVM file opcodes should be disabled" >&2
  exit 1
fi
grep -Fq "menonaktifkan opcode file" "$TMP/05_file_io.js.err"
if (cd "$RUN_DIR" && python3 "$TMP/05_file_io.py") >"$TMP/05_file_io.default.out" 2>"$TMP/05_file_io.default.err"; then
  echo "FAIL: Python PVM file I/O should require explicit capability" >&2
  exit 1
fi
grep -Fq "dinonaktifkan" "$TMP/05_file_io.default.err"
(cd "$RUN_DIR" && python3 "$TMP/05_file_io.py" --allow-file-io) > "$TMP/05_file_io.python.out"
grep -Fq "fixture file I/O" "$TMP/05_file_io.python.out"
echo "PASS: PVM file operations default-deny/capability-gated"
