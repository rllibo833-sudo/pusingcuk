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
FIXTURE="tests/pusingcuk-pvm-test.txt"
mkdir -p "$TMP"
cleanup() {
  rm -rf "$TMP"
  rm -f "$FIXTURE"
}
trap cleanup EXIT
"$CC" -std=c11 -O2 -Wall -Wextra -Werror src/c-core/main.c -o "$TMP/pvmc"
command -v node >/dev/null || { echo "Node.js dibutuhkan untuk uji JS" >&2; exit 2; }
python3 --version >/dev/null
printf 'fixture file I/O\n' > "$FIXTURE"
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
