# Backend C eksperimental Pusingcuk

Status: proof-of-concept yang benar-benar menghasilkan source C11 untuk subset bahasa yang dibatasi. Bukan klaim bahwa semua program Pusingcuk dapat dikompilasi.

## Pakai

    python -m compiler.c_backend program.pusingcuk -o program.c
    cc -std=c11 -Wall -Wextra program.c -o program
    ./program

Source C juga dapat ditulis ke stdout dengan menghilangkan opsi -o.

## Fitur yang didukung

- Deklarasi variabel dan assignment variabel yang sudah ada.
- Literal integer nonnegatif sampai INT64_MAX; nilai negatif ditulis dengan unary minus pada literal yang didukung.
- Operasi integer tambah, kurang, kali, termasuk pemeriksaan overflow runtime.
- Output integer ke stdout dengan newline.
- Ekspresi bersarang yang terdiri dari fitur-fitur di atas.

## Ditolak secara eksplisit

String, boolean, float, list, dictionary, index, kondisi, loop, input, fungsi, operasi selain tambah/kurang/kali, dan fitur lain di luar daftar dukungan. Compiler mengeluarkan diagnostik dan exit code bukan nol. Penolakan ini disengaja agar hasil tidak tampak berhasil dengan semantik yang berbeda.

## Desain dan batas

- Front-end memakai parser Pusingcuk dan IR v1; backend tidak mengurai ulang alias slang.
- Nama variabel sumber dipetakan ke identifier internal C yang dibuat backend.
- Arithmetic overflow dideteksi agar operasi signed integer tidak memicu undefined behavior C.
- Hasil adalah source C11; pengguna masih memerlukan compiler C untuk membuat executable.
- Belum ada ABI/FFI, package/module system, garbage collector, debugging map C, atau backend WASM/JavaScript.
- Runtime hasil kompilasi bukan sandbox. Jangan menjalankan program tak tepercaya dengan hak istimewa.
- Semantik lintas target hanya dapat diklaim untuk fitur yang lulus fixture konformansi yang sama.
