#!/usr/bin/env bash
# Device-side integration check. Run this on a real Termux ARM64 device from repo root.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TMP_BASE="${TMPDIR:-$PREFIX/tmp}"
TMP="$TMP_BASE/pusingcuk-termux-check-$$"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing command: $1" >&2; exit 2; }; }
need python
need clang
need make

echo "[1/6] Python interpreter and syntax check"
python --version
python pusingcuk_new.py --check examples/halo_dunia.cuk

echo "[2/6] Interactive Python CLI examples"
halo_output="$(printf 'Ayu\n' | python pusingcuk_new.py examples/halo_dunia.cuk)"
printf '%s\n' "$halo_output"
grep -Fq "Halo, Ayu!" <<<"$halo_output"
calc_output="$(printf '20\n+\n22\n' | python pusingcuk_new.py examples/kalkulator.cuk)"
printf '%s\n' "$calc_output"
grep -Fq "Hasil: 42" <<<"$calc_output"
zero_output="$(printf '10\n/\n0\n' | python pusingcuk_new.py examples/kalkulator.cuk)"
grep -Fq "pembagian dengan nol" <<<"$zero_output"

echo "[3/6] Install the Python CLI and validate executable permissions/shebang"
python -m venv "$TMP/venv"
"$TMP/venv/bin/python" -m pip install --no-deps .
cp examples/halo_dunia.cuk "$TMP/halo-device.cuk"
chmod 755 "$TMP/halo-device.cuk"
test -x "$TMP/halo-device.cuk"
cli_output="$(printf 'Termux\n' | env PATH="$TMP/venv/bin:$PATH" "$TMP/halo-device.cuk")"
printf '%s\n' "$cli_output"
grep -Fq "Halo, Termux!" <<<"$cli_output"

echo "[4/6] Native C build, executable bit, version, and sample"
make native NATIVE_BIN="$TMP/pusingcuk-native"
test -x "$TMP/pusingcuk-native"
native_version="$("$TMP/pusingcuk-native" --version)"
printf '%s\n' "$native_version"
grep -Fq "0.7.2" <<<"$native_version"
native_output="$("$TMP/pusingcuk-native" examples/native/rekap_anggaran.pusingcuk)"
printf '%s\n' "$native_output"
grep -Fq "1200000" <<<"$native_output"
grep -Fq "1300000" <<<"$native_output"

echo "[5/6] Source path, syntax/runtime failure, and exit-code contract"
if python pusingcuk_new.py "$TMP/source-yang-tidak-ada.cuk" >"$TMP/missing.out" 2>"$TMP/missing.err"; then
  echo "Expected missing source to fail" >&2; exit 1
else
  code=$?
  test "$code" -eq 3 || { echo "Expected exit 3 for missing source, got $code" >&2; exit 1; }
fi
cat >"$TMP/syntax-error.cuk" <<'CUK'
jancuk
lah = 3
selesai jancuk
CUK
if python pusingcuk_new.py --check "$TMP/syntax-error.cuk" >"$TMP/syntax.out" 2>"$TMP/syntax.err"; then
  echo "Expected syntax error to fail" >&2; exit 1
else
  code=$?
  test "$code" -eq 2 || { echo "Expected exit 2 for syntax error, got $code" >&2; exit 1; }
fi
cat >"$TMP/runtime-error.cuk" <<'CUK'
jancuk
hedeh variabel_yang_tidak_ada
selesai jancuk
CUK
if python pusingcuk_new.py "$TMP/runtime-error.cuk" >"$TMP/runtime.out" 2>"$TMP/runtime.err"; then
  echo "Expected runtime error to fail" >&2; exit 1
else
  code=$?
  test "$code" -eq 1 || { echo "Expected exit 1 for runtime error, got $code" >&2; exit 1; }
fi

echo "[6/6] Native runtime's explicit unsupported boundary"
if "$TMP/pusingcuk-native" examples/kalkulator.cuk >"$TMP/native-calculator.out" 2>"$TMP/native-calculator.err"; then
  echo "Unexpectedly accepted reference-only calculator in native runtime" >&2
  exit 1
fi
echo "PASS: Termux integration checks completed."
echo "Record device model, Android/API level, Termux package versions, architecture, and output when reporting results."
