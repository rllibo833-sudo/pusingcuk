#!/data/data/com.termux/files/usr/bin/bash
set -eu

if [ -z "${PREFIX:-}" ] || [ ! -d "$PREFIX/bin" ]; then
    echo "Skrip ini ditujukan untuk Termux. PREFIX/bin tidak ditemukan." >&2
    echo "Pasang clang dan make terlebih dahulu: pkg install clang make" >&2
    exit 2
fi

if ! command -v clang >/dev/null 2>&1; then
    echo "Compiler clang belum tersedia. Jalankan: pkg install clang" >&2
    exit 2
fi
if ! command -v make >/dev/null 2>&1; then
    echo "make belum tersedia. Jalankan: pkg install make" >&2
    exit 2
fi

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
TARGET="$PREFIX/bin/pusingcuk-native"

echo "Membangun runtime C Pusingcuk..."
make -C "$ROOT" native CC=clang NATIVE_BIN="$TARGET"
echo
echo "Runtime native terpasang: $TARGET"
echo "Coba jalankan dari root repositori:"
echo "  pusingcuk-native examples/native/rekap_anggaran.pusingcuk"
echo "Catatan: runtime native mendukung subset bahasa; fungsi buatan pengguna dan modul belum tersedia."
