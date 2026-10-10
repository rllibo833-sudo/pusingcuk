#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
cd "$HOME/pusingcuk"

SRC="native/pusingcuk.c"
BACKUPS="backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$BACKUPS/pusingcuk-pre-fungsi-$STAMP.c"
TMP="$(mktemp)"
TEST="$(mktemp)"
DONE=0

cleanup() {
  rm -f "$TMP" "$TEST"
}
trap cleanup EXIT

if [[ ! -f "$SRC" || ! -d "$BACKUPS" ]]; then
  echo "GAGAL: file runtime atau folder backup tidak ditemukan."
  exit 1
fi

if grep -q 'PC_FUNCTIONS_V1' "$SRC"; then
  echo "Patch fungsi sudah terpasang; tidak ada perubahan."
  exit 0
fi

if ! grep -q 'fail("fungsi belum didukung")' "$SRC"; then
  echo "GAGAL: struktur runtime berbeda dari yang diharapkan."
  exit 1
fi

cp -p "$SRC" "$BACKUP"
cp "$SRC" "$TMP"

echo "Backup: $BACKUP"
echo "Memeriksa struktur runtime..."

if ! grep -q 'static int run_range(int first,int last)' "$TMP"; then
  echo "GAGAL: fungsi run_range tidak ditemukan."
  exit 1
fi

echo "Patch belum diterapkan."
echo "Pemeriksaan aman selesai; runtime tidak diubah."
echo "Diperlukan implementasi yang sesuai dengan parser dan mekanisme blok saat ini."
