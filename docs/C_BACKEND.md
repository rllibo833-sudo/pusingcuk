# Backend C eksperimental Pusingcuk

Status: backend source C11 untuk subset bahasa yang dibatasi. Bukan klaim bahwa semua program Pusingcuk dapat dikompilasi.

## Pakai

    python -m compiler.c_backend program.pusingcuk -o program.c
    cc -std=c11 -Wall -Wextra -Werror program.c -o program
    ./program

Source C juga dapat ditulis ke stdout dengan menghilangkan opsi -o.

## Fitur yang didukung

- Deklarasi variabel dan assignment variabel yang sudah ada.
- Literal integer nonnegatif sampai INT64_MAX; nilai negatif ditulis dengan unary minus pada literal yang didukung.
- Operasi integer tambah, kurang, kali, pembagian bulat `//`, dan modulo `%`, termasuk pemeriksaan overflow untuk operasi yang dapat meluap.
- Semantik `//` mengikuti pembagian bulat Python (pembulatan ke bawah, termasuk operand negatif); semantik `%` mengikuti tanda divisor seperti Python.
- Pembagian dengan nol dan modulo dengan nol gagal saat program hasil kompilasi berjalan.
- Output integer ke stdout dengan newline.
- Ekspresi bersarang yang terdiri dari fitur-fitur di atas.

## Ditolak secara eksplisit

String, boolean, float, list, dictionary, index, kondisi, loop, input, fungsi, operasi selain tambah/kurang/kali/pembagian bulat/modulo, dan fitur lain di luar daftar dukungan. Compiler mengeluarkan diagnostik dan exit code bukan nol. Penolakan ini disengaja agar hasil tidak tampak berhasil dengan semantik yang berbeda.

## Desain dan batas

- Front-end memakai parser Pusingcuk dan IR v1; backend tidak mengurai ulang alias slang.
- Nama variabel sumber dipetakan ke identifier internal C yang dibuat backend.
- Arithmetic overflow dideteksi agar operasi signed integer tidak memicu undefined behavior C.
- Pembagian bulat memeriksa kasus INT64_MIN / -1; modulo menangani INT64_MIN % -1 secara eksplisit karena operasi modulo C tersebut tidak terdefinisi, sementara hasil matematisnya nol.
- Hasil adalah source C11; pengguna masih memerlukan compiler C untuk membuat executable.
- Belum ada ABI/FFI, package/module system, garbage collector, debugging map C, atau backend WASM/JavaScript.
- Runtime hasil kompilasi bukan sandbox. Jangan menjalankan program tak tepercaya dengan hak istimewa.
- Semantik lintas target hanya dapat diklaim untuk fitur yang lulus fixture konformansi yang sama.

## Matriks tes tahap ini

| Area | Kasus | Bukti yang diwajibkan |
|---|---|---|
| Kompilasi | Source hasil generate dikompilasi dengan C11, `-Wall -Wextra -Werror` | Build sukses |
| Eksekusi | Kombinasi tanda untuk `//` dan `%` | Output dibandingkan byte-for-byte dengan interpreter Python |
| Batas nilai | INT64_MAX dibagi dan dimodulo 2 | Hasil tepat, tanpa overflow |
| Error runtime | Pembagian nol dan modulo nol | Exit code bukan nol, stdout kosong, diagnostik di stderr |
| Regresi | Overflow tambah dan fitur belum didukung | Tetap ditolak/digagalkan |
| CI | Python 3.11 dan 3.12 | Seluruh unit tests berjalan pada kedua versi |

Perintah tes lokal:

    python -m unittest tests.test_c_backend -v

