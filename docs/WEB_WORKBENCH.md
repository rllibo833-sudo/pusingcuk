# Pusingcuk Studio (workbench HTML lokal)

Pusingcuk Studio menyediakan editor kode di browser dan terminal keluaran yang menjalankan executable native C Pusingcuk. Browser tidak berpura-pura menjalankan bahasa: tombol Jalankan mengirim kode ke bridge lokal, yang menulis file sementara dan memanggil binary native dengan argumen tetap tanpa shell.

## Prasyarat
- Python 3 untuk server bridge lokal saja.
- Compiler C11: clang atau gcc.
- make tidak diperlukan; bridge mengompilasi sumber native langsung ke direktori sementara.

Python bukan runtime bahasa Pusingcuk di Studio. Program .pusingcuk dieksekusi oleh executable native C; Python hanya menyediakan HTTP lokal untuk menghubungkan browser dengan executable. Untuk menjalankan program tanpa Python sama sekali, gunakan CLI native di NATIVE_TERMUX.md.

## Jalankan di Termux atau Linux

Dari direktori root repo, pilih perintah sesuai sistem operasi.

Termux:

    pkg install python clang -y
    python tools/web_workbench.py

Debian/Ubuntu:

    sudo apt update
    sudo apt install python3 clang
    python3 tools/web_workbench.py

Buka browser pada perangkat yang sama ke http://127.0.0.1:8765. Hentikan dengan Ctrl+C. Studio mengompilasi runtime ke direktori sementara dan membersihkannya saat server berhenti. Setiap program juga disimpan di direktori sementara terpisah yang dihapus setelah selesai.

## Fitur MVP
- Editor teks untuk file .pusingcuk.
- Buka dan simpan file lokal melalui browser.
- Menjalankan kode dengan runtime native C.
- Menyediakan stdin untuk perintah tanya.
- Menampilkan stdout, stderr, status keluar, dan timeout.
- Tidak memakai CDN, analytics, atau layanan cloud.

## Batas keamanan
- Server hanya bind ke 127.0.0.1; jangan ubah ke 0.0.0.0 untuk penggunaan umum.
- Bridge tidak menyediakan endpoint shell, path file arbitrer, atau unggah file untuk dieksekusi dari disk pengguna.
- Request kode dibatasi 64 KiB, stdin 16 KiB, dan eksekusi 3 detik.
- Permintaan lintas-origin ditolak jika header Origin ada dan tidak cocok dengan origin lokal.
- Runtime native bukan sandbox. Batas waktu dan batas langkah bukan isolasi OS; jangan menjalankan kode dari orang tak dikenal atau mengekspos bridge ke jaringan.
- MVP belum memiliki debugger, language server, syntax highlighting, multi-file/module support, atau validasi perangkat Android nyata.

## Tes
Jalankan python -m unittest discover -s tests -v untuk tes bridge dan tes proyek. make test-native tetap menjadi validasi runtime native utama.
