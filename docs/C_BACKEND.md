# Backend C eksperimental Pusingcuk

Status: backend source C11 untuk subset integer, boolean, perbandingan/logika, kondisi, loop mumet, dan fungsi pengguna integer. Ini masih subset; bukan semua program Pusingcuk dapat dikompilasi.

## Pakai

    python -m compiler.c_backend program.pusingcuk -o program.c
    cc -std=c11 -Wall -Wextra -Werror program.c -o program
    ./program

Python dibutuhkan untuk front-end compiler saat menghasilkan C. Executable C hasil kompilasi berjalan tanpa Python.

## Fitur yang didukung

- Deklarasi dan assignment variabel yang sudah ada.
- Literal integer nonnegatif sampai INT64_MAX serta boolean benar/salah (termasuk alias valid/zonk).
- Aritmetika integer +, -, *, //, %, pemeriksaan overflow, pembagian nol, dan semantik floor division/modulo Python-style.
- Perbandingan ==, !=, <, <=, >, >=; logika bukan, dan, atau dengan short-circuit.
- Kondisi njir ... kampret ... selesai njir termasuk bersarang.
- Loop mumet kondisi ... selesai mumet dengan batas 10.000 iterasi per loop.
- Fungsi tingkat atas dengan parameter integer, pemanggilan fungsi sebelum definisi, fungsi rekursif, dan balek dengan nilai integer.
- Batas kedalaman pemanggilan fungsi 100.
- Output integer dan boolean (okelah/tidak); alias spill juga dikenali.

## Contoh: loop dan fungsi

Berkas library/loops_functions_genz.pusingcuk adalah contoh panduan yang memakai alias Gen Z/Gen Alpha. Contoh itu juga mencetak teks, sehingga jalankan lewat interpreter modular untuk melihat seluruh output:

    python pusingcuk_new.py library/loops_functions_genz.pusingcuk

Untuk mengetes backend C, gunakan contoh integer-only:

    python -m compiler.c_backend library/conditional_logic.pusingcuk -o /tmp/conditional_logic.c
    cc -std=c11 -Wall -Wextra -Werror /tmp/conditional_logic.c -o /tmp/conditional_logic
    /tmp/conditional_logic

## Batas subset yang disengaja

- String, float, list, dictionary, indeks, input, loop untuk, dan fitur lain yang tidak tercantum di atas ditolak saat kompilasi.
- Parameter dan nilai balek fungsi hanya integer. Fungsi yang berakhir tanpa balek nilai integer menghasilkan error runtime; argumen boolean ditolak.
- Deklarasi lah di dalam loop ditolak. Deklarasikan variabel sebelum loop, lalu ubah nilainya dengan assignment.
- Fungsi hanya boleh didefinisikan di tingkat teratas; balek hanya boleh dipakai di dalam fungsi.
- Assignment yang mengubah tipe variabel dari integer ke boolean atau sebaliknya ditolak agar semantik tidak berubah diam-diam.
- Deklarasi dalam cabang kondisi hanya tersedia dalam cabang tersebut pada subset backend ini. Jangan gunakan variabel yang dibuat di dalam cabang setelah blok selesai.

Tes backend:

    python -m unittest tests.test_c_backend -v

Backend ini tetap eksperimental. Periksa kesetaraan terhadap interpreter modular dan tunggu seluruh pemeriksaan CI hijau sebelum merge.
