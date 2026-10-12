# Pusingcuk Termux Control Dashboard

Dashboard terminal untuk membuka repo Pusingcuk, melihat status Git, branch, Pull Requests, GitHub Actions, menjalankan tes, dan mengedit program.

## Instalasi di Termux

Dari root repo:

```sh
pkg update
pkg install git gh nano clang make python nodejs -y
gh auth login
chmod +x tools/termux_dashboard.sh
```

Pilih login GitHub via HTTPS ketika diminta. Pastikan `gh auth status` berhasil.

## Menjalankan dashboard

```sh
bash tools/termux_dashboard.sh
```

Jika repo disimpan bukan di `$HOME/pusingcuk`, atur lokasi:

```sh
export PUSINGCUK_REPO="$HOME/path/ke/pusingcuk"
bash "$PUSINGCUK_REPO/tools/termux_dashboard.sh"
```

## Otomatis tampil saat Termux dibuka

Tambahkan ke akhir `~/.bashrc`:

```sh
# Buka dashboard otomatis hanya untuk shell interaktif
if [[ $- == *i* && -f "$HOME/pusingcuk/tools/termux_dashboard.sh" && -z "${PUSINGCUK_NO_DASHBOARD:-}" ]]; then
  bash "$HOME/pusingcuk/tools/termux_dashboard.sh"
fi
```

Simpan lalu jalankan `source ~/.bashrc` atau tutup dan buka Termux lagi.

Untuk membuka shell tanpa dashboard sekali waktu:

```sh
PUSINGCUK_NO_DASHBOARD=1 bash
```

## Tentang sinkronisasi

Menu sinkronisasi akan meminta konfirmasi, lalu melakukan commit (jika ada perubahan), `git pull --rebase`, dan `git push` pada branch aktif. Ini mengotomatisasi langkah Git, tetapi bukan sinkronisasi langsung tanpa Git: perubahan lokal baru terlihat di GitHub setelah berhasil dikirim melalui jaringan.

Jangan menaruh token, kata sandi, kunci privat, atau data rahasia di repo. Jika terjadi konflik rebase, dashboard menghentikan proses sebelum push agar perubahan tidak tertimpa. Periksa `git status` dan selesaikan konflik secara manual.

## Batasan

- Dashboard membutuhkan repo lokal yang sudah di-clone.
- Menu Actions dan PR memerlukan GitHub CLI (`gh`) yang sudah login.
- Tes tertentu memerlukan toolchain yang sesuai (Clang, Node.js, Python, Make).
- Dashboard tidak menampilkan seluruh UI web GitHub; ia menyediakan ringkasan terminal dan shortcut.
