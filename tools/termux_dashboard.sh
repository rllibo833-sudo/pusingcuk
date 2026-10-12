#!/data/data/com.termux/files/usr/bin/bash
# Pusingcuk Termux Control Dashboard
set -u

ROOT="${PUSINGCUK_REPO:-$HOME/pusingcuk}"
REPO_URL="https://github.com/rllibo833-sudo/pusingcuk"

if ! command -v git >/dev/null 2>&1; then
  printf 'Git belum terpasang. Jalankan: pkg install git\n'
  exit 1
fi

if [ ! -d "$ROOT/.git" ]; then
  printf 'Repo tidak ditemukan di: %s\n' "$ROOT"
  printf 'Clone repo dengan:\n  git clone %s "$ROOT"\n' "$REPO_URL"
  exit 1
fi

cd "$ROOT" || exit 1

pause() { printf '\nTekan Enter untuk kembali...'; read -r _; }
line() { printf '%s\n' '------------------------------------------------------------'; }

open_page() {
  url="$1"
  if command -v termux-open-url >/dev/null 2>&1; then
    termux-open-url "$url"
  else
    printf '\nBuka URL ini di browser: %s\n' "$url"
  fi
}

show_status() {
  line
  printf 'REPO: %s\n' "$ROOT"
  printf 'BRANCH: '; git branch --show-current
  printf '\nSTATUS GIT:\n'
  git status --short --branch
  printf '\nCOMMIT TERAKHIR:\n'
  git log -1 --oneline --decorate
  line
}

show_branches() {
  printf '\nBRANCH LOKAL + REMOTE YANG TERSIMPAN DI TERMUX\n'
  git branch -avv
  printf '\nMembuka daftar semua branch GitHub di browser...\n'
  open_page "$REPO_URL/branches"
  pause
}

show_actions() {
  printf '\nMembuka GitHub Actions di browser (tanpa gh auth)...\n'
  open_page "$REPO_URL/actions"
  pause
}

show_prs() {
  printf '\nMembuka Pull Requests di browser (tanpa gh auth)...\n'
  open_page "$REPO_URL/pulls"
  pause
}

run_tests() {
  printf 'Pilih tes:\n'
  printf '1) Tes bytecode lintas backend (tests/test_all.sh)\n'
  printf '2) Tes runtime native (make test-native)\n'
  printf '3) Tes Python (unittest)\n'
  printf '4) Tes konformansi (tools/conformance.py)\n'
  printf '0) Batal\n> '
  read -r choice
  case "$choice" in
    1) bash tests/test_all.sh ;;
    2) make test-native ;;
    3) python -m unittest discover -s tests -v ;;
    4) python tools/conformance.py ;;
    0) return ;;
    *) printf 'Pilihan tidak dikenal.\n' ;;
  esac
  pause
}

edit_program() {
  printf 'Masukkan path file relatif dari root repo (contoh: examples/halo.pusingcuk)\n> '
  read -r path
  case "$path" in
    /*|*..*) printf 'Path ditolak. Gunakan path relatif tanpa ..\n'; pause; return ;;
  esac
  if [ -z "$path" ]; then return; fi
  if command -v nano >/dev/null 2>&1; then
    nano "$path"
  elif command -v vim >/dev/null 2>&1; then
    vim "$path"
  else
    printf 'Editor belum terpasang. Jalankan: pkg install nano\n'
    pause
  fi
}

sync_repo() {
  printf '\nPERINGATAN: sinkronisasi memakai Git di belakang layar.\n'
  printf 'Perubahan lokal akan di-commit dan dikirim ke GitHub pada branch aktif.\n'
  printf 'Branch aktif: '; git branch --show-current
  git status --short
  printf '\nLanjutkan? Ketik YA untuk setuju: '
  read -r confirm
  [ "$confirm" = "YA" ] || { printf 'Dibatalkan.\n'; pause; return; }

  if [ -n "$(git status --porcelain)" ]; then
    printf 'Pesan commit: '
    read -r message
    [ -n "$message" ] || message="chore: sync Termux changes"
    git add -A && git commit -m "$message" || { printf 'Commit gagal; periksa status Git.\n'; pause; return; }
  fi

  branch="$(git branch --show-current)"
  git pull --rebase origin "$branch" || {
    printf '\nPull/rebase gagal atau konflik. Tidak ada push dilakukan.\n'
    printf 'Periksa: git status\n'
    pause
    return
  }
  git push origin "$branch" || {
    printf '\nPush gagal. Periksa autentikasi dan status branch.\n'
    pause
    return
  }
  printf '\nSinkronisasi selesai untuk branch %s.\n' "$branch"
  pause
}

while true; do
  clear 2>/dev/null || true
  printf '\n'
  printf '============================================================\n'
  printf '          PUSINGCUK :: TERMUX CONTROL CENTER\n'
  printf '============================================================\n'
  printf 'Repo   : rllibo833-sudo/pusingcuk\n'
  printf 'Branch : '; git branch --show-current
  printf 'Status : '
  if [ -z "$(git status --porcelain)" ]; then printf 'bersih\n'; else printf 'ada perubahan lokal\n'; fi
  printf '\n'
  printf '  1. Ringkasan status repo\n'
  printf '  2. Lihat branch lokal dan remote\n'
  printf '  3. Lihat GitHub Actions terbaru\n'
  printf '  4. Lihat Pull Requests terbuka\n'
  printf '  5. Jalankan tes proyek\n'
  printf '  6. Buat/edit program Pusingcuk\n'
  printf '  7. Sinkronkan branch aktif ke GitHub\n'
  printf '  8. Buka repo GitHub di browser\n'
  printf '  9. Masuk ke shell repo biasa\n'
  printf '  0. Keluar dari dashboard\n'
  printf '> '
  read -r choice
  case "$choice" in
    1) show_status; pause ;;
    2) show_branches ;;
    3) show_actions ;;
    4) show_prs ;;
    5) run_tests ;;
    6) edit_program ;;
    7) sync_repo ;;
    8) if command -v termux-open-url >/dev/null 2>&1; then termux-open-url "$REPO_URL"; else printf '%s\n' "$REPO_URL"; pause; fi ;;
    9) exec "${SHELL:-/data/data/com.termux/files/usr/bin/bash}" -i ;;
    0) printf 'Dashboard ditutup.\n'; exit 0 ;;
    *) printf 'Pilihan tidak dikenal.\n'; sleep 1 ;;
  esac
done
