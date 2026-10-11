# Backend C eksperimental Pusingcuk

Status: backend source C11 untuk subset integer, boolean, ekspresi perbandingan/logika, dan kondisi. Ini bukan klaim bahwa semua program Pusingcuk dapat dikompilasi.

## Pakai

    python -m compiler.c_backend program.pusingcuk -o program.c
    cc -std=c11 -Wall -Wextra -Werror program.c -o program
    ./program

Source C juga dapat ditulis ke stdout dengan menghilangkan opsi -o. Python diperlukan untuk menjalankan front-end compiler; executable C hasil kompilasi tidak memerlukan Python.

## Fitur yang didukung

- Deklarasi dan assignment variabel yang sudah ada.
- Literal integer nonnegatif sampai INT64_MAX serta boolean benar dan salah.
- Operasi integer +, -, *, pembagian bulat //, dan modulo %.
- Perbandingan ==, !=, <, <=, >, >=.
- Negasi logika bukan, operator dan dan atau dengan short-circuit.
- Kondisi njir ... kampret ... selesai njir, termasuk kondisi bertingkat.
- Output integer dan boolean (okelah / tidak).
- Pembagian bulat Python-style untuk operand negatif, modulo dengan tanda divisor, pemeriksaan overflow integer, serta error runtime untuk pembagian/modulo nol.
- Ekspresi bersarang yang terdiri dari fitur-fitur di atas.

## Batas subset yang disengaja

- String, float, list, dictionary, indeks, input, loop, fungsi, dan fitur lain yang tidak tercantum di atas ditolak saat kompilasi.
- Untuk menghindari perbedaan semantik diam-diam, assignment yang mengubah tipe variabel dari integer ke boolean atau sebaliknya ditolak oleh backend ini. Interpreter modular dapat mendukung program yang lebih luas.
- Deklarasi yang berada di dalam cabang kondisi hanya tersedia di cabang itu pada subset backend ini. Jangan memakai variabel yang dideklarasikan di cabang setelah blok selesai.
- Literal negatif ditulis dengan unary minus. Batas literal dan operasi integer tetap mengikuti batas int64 backend.
- Fitur yang ditolak harus tetap ditandai unsupported; penolakan bukan kegagalan konformansi untuk fitur yang memang berada di luar subset.

## Desain dan batas

- Front-end memakai parser Pusingcuk dan IR v1; backend tidak mengurai ulang alias slang.
- Nilai integer dan boolean direpresentasikan sebagai int64_t dengan metadata tipe saat code generation. Boolean dicetak sebagai okelah atau tidak.
- Kesetaraan integer dan boolean menjaga aturan bahasa: benar == 1 menghasilkan tidak, meskipun representasi runtime keduanya memakai 1.
- Operator logika menggunakan short-circuit. Ekspresi kanan tidak dieksekusi jika hasil sudah ditentukan.
- Nama variabel sumber dipetakan ke identifier internal C yang dibuat backend.
- Arithmetic overflow dideteksi agar operasi signed integer tidak memicu undefined behavior C.
- Pembagian bulat memeriksa kasus INT64_MIN / -1; modulo menangani INT64_MIN % -1 secara eksplisit.
- Hasil adalah source C11; pengguna masih memerlukan compiler C untuk membuat executable.
- Belum ada ABI/FFI, package/module system, garbage collector, debugging map C, atau backend WASM/JavaScript.
- Runtime hasil kompilasi bukan sandbox. Jangan menjalankan program tak tepercaya dengan hak istimewa.

## Matriks tes

| Area | Kasus | Bukti |
|---|---|---|
| Kompilasi | C11, -Wall -Wextra -Werror | Build sukses |
| Aritmetika | + - * // %, kombinasi tanda, batas INT64 | Hasil tepat dan overflow terkendali |
| Boolean | benar, salah, bukan | Output sesuai kontrak |
| Perbandingan | enam operator, kesetaraan boolean vs angka | Output dibandingkan dengan interpreter |
| Short-circuit | operand kanan berisi pembagian nol | Program tidak gagal jika operand dilewati |
| Kondisi | cabang benar/salah dan kondisi gabungan | Output dan exit code sama dengan interpreter |
| Error | pembagian nol, fitur unsupported, perubahan tipe | Kegagalan eksplisit, tanpa klaim dukungan palsu |
| CI | Python 3.11/3.12, GCC, Clang | Tes wajib lulus |

Perintah tes lokal:

    python -m unittest tests.test_c_backend -v
