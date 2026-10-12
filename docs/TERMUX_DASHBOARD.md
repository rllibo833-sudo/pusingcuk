# Pusingcuk Termux Control Dashboard

Dashboard terminal untuk membuka repo Pusingcuk, melihat status Git, branch, Pull Requests, GitHub Actions, menjalankan tes, dan mengedit program.

## Instalasi di Termux

Dari root repo:

```sh
pkg update
pkg install git nano clang make python nodejs -y
chmod +x tools/termux_dashboard.sh
```

GitHub CLI (`gh`) tidak diperlukan untuk menu branch, Actions, dan Pull Requests. Menu Actions dan PR membuka halaman GitHub di browser. Melihat branch lokal/remote memakai Git; pembaruan referensi remote memakai `git fetch origin --prune`, yang untuk repo publik biasanya tidak membutuhkan login.

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

Jangan menaruh token, kata sandi, kunci privat, atau data rahasia di repo. Menu sinkronisasi saat ini menggunakan `git add -A`, jadi periksa `git status --short` dan pastikan tidak ada file rahasia sebelum menggunakannya. Jika terjadi konflik rebase, dashboard menghentikan proses sebelum push agar perubahan tidak tertimpa.

## Batasan

- Dashboard membutuhkan repo lokal yang sudah di-clone.
- Menu 2 menampilkan branch yang tersimpan secara lokal, mencoba memperbaruinya dengan Git, lalu membuka daftar branch lengkap di browser.
- Menu 3 membuka GitHub Actions di browser, tanpa memerlukan `gh auth login`.
- Menu 4 membuka Pull Requests di browser, tanpa memerlukan `gh auth login`.
- Tes tertentu memerlukan toolchain yang sesuai (Clang, Node.js, Python, Make).
- Dashboard tidak menampilkan seluruh UI web GitHub di dalam terminal; shortcut membuka browser Android.
