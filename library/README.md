# Pustaka Pusingcuk

Direktori ini berisi referensi kosakata yang mudah dipakai ulang dan contoh program Pusingcuk.

- [kosakata.json](kosakata.json): glosarium mesin untuk kata kunci, alias, operator, arti, dan status dukungan runtime.
- [conditional_logic.pusingcuk](conditional_logic.pusingcuk): contoh perbandingan, boolean, short-circuit, dan kondisi yang kompatibel dengan subset backend C.
- [loops_functions_genz.pusingcuk](loops_functions_genz.pusingcuk): contoh loop, fungsi rekursif, dan alias Gen Z/Gen Alpha. Jalankan lewat interpreter modular karena contoh ini mencetak teks yang belum didukung backend C.

## Jalankan contoh dengan interpreter Python

Dari root repository:

    python pusingcuk_new.py library/conditional_logic.pusingcuk
    python pusingcuk_new.py library/loops_functions_genz.pusingcuk

## Kompilasi contoh menjadi C11

Dari root repository, dengan Python dan compiler C11 tersedia:

    python -m compiler.c_backend library/conditional_logic.pusingcuk -o /tmp/conditional_logic.c
    cc -std=c11 -Wall -Wextra -Werror /tmp/conditional_logic.c -o /tmp/conditional_logic
    /tmp/conditional_logic

Executable hasil kompilasi tidak memerlukan Python saat dijalankan. Python hanya dipakai oleh front-end compiler.

## Cara membaca status dukungan

- `native_runtime: tested` berarti kemampuan tercatat memiliki tes pada runtime C mandiri; periksa matriks runtime untuk batas detail.
- `c_backend: supported` berarti fitur berada di subset source-to-C yang diuji.
- `c_backend: unsupported` berarti jangan gunakan fitur itu dalam contoh untuk compiler C; compiler akan menolaknya secara eksplisit.

Glosarium adalah indeks praktis, bukan pengganti spesifikasi. Jika ada perbedaan, rujuk SPEC.md dan dokumen semantik.
