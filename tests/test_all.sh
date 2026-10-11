#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
CC=clang
TMP="/tmp/pusingcuk-pvm-test-$$"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT
"$CC" -std=c11 -O2 -Wall -Wextra -Werror src/c-core/main.c -o "$TMP/pvmc"
command -v node >/dev/null || { echo "Node.js dibutuhkan untuk uji JS" >&2; exit 2; }
python3 --version >/dev/null
printf 'fixture file I/O\n' > /tmp/pusingcuk-pvm-test.txt
for src in tests/0[1-6]_*.cuk; do
  name="$(basename "$src" .cuk)"
  "$TMP/pvmc" "$src" "$TMP/$name.pvm"
  node src/backends/js/compiler.js "$TMP/$name.pvm" "$TMP/$name.js"
  python3 src/backends/python/compiler.py "$TMP/$name.pvm" "$TMP/$name.py"
  node "$TMP/$name.js" > "$TMP/$name.js.out"
  python3 "$TMP/$name.py" > "$TMP/$name.py.out"
  diff -u "$TMP/$name.js.out" "$TMP/$name.py.out"
  echo "PASS: $name"
done
