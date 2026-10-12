# Importer Python ke Pusingcuk (eksperimental)

Importer awal menerjemahkan **subset kecil Python** menjadi berkas sumber Pusingcuk. Ia membaca struktur sintaks Python melalui modul `ast`; bukan pencarian-dan-penggantian kata.

## Cara pakai

Dari folder utama repo:

```sh
python -m compiler.import_python contoh.py --output contoh.cuk
python -m compiler contoh.cuk --target js --output contoh.js
node contoh.js
```

Contoh `contoh.py`:

```python
angka = 3 + 4
print(angka)
```

Hasil impor yang diharapkan:

```pusingcuk
jancuk
lah angka = (3 + 4)
hedeh angka
selesai jancuk
```

## Cakupan awal

- Variabel, assignment sederhana, dan operator matematika dasar.
- `print(x)` dengan tepat satu argumen.
- `input()` dengan nol atau satu prompt posisional.
- `if/else`, `while`, dan `for nama in koleksi`.
- `range()` menjadi `rentang()` (1–3 argumen), `len()` menjadi `panjang()`.
- Builtin numerik: `abs(x)` → `mutlak(x)`, `round(x)` → `bulatkan(x)`, `min(a, b)` → `minimum(a, b)`, dan `max(a, b)` → `maksimum(a, b)`.
- Fungsi dengan parameter posisi biasa tanpa nilai default, `return`, daftar, kamus, dan indeks.
- Boolean, perbandingan sederhana, `if/elif/else`, serta operator `and/or/not`.

## Hubungan dengan pustaka standar Pusingcuk

Pemetaan hanya memakai fungsi yang sudah didukung backend JS/Python/VM dan didokumentasikan: `panjang`, `rentang`, `mutlak`, `minimum`, `maksimum`, dan `bulatkan`. Untuk menjaga arti tetap dekat dengan Python, `min` dan `max` dibatasi menjadi tepat dua argumen dan dimaksudkan untuk angka. `round` hanya menerima satu argumen; pembulatan Pusingcuk mengikuti aturan ties-to-even.

Walaupun registri pustaka juga mencatat `teks`, `bilangan`, `desimal`, dan `logika`, dokumentasi proyek menyatakan konversi itu belum diaktifkan secara konsisten di semua backend. Karena itu importer **belum** memetakannya. Import seperti `import os`, `import requests`, atau modul pihak ketiga tetap ditolak; nama modul tidak otomatis membuat API tersebut tersedia di Pusingcuk.

## Batasan penting

Ini **belum menerjemahkan semua Python**. Import modul (selain pemetaan builtin eksplisit di atas), kelas, exception handling, comprehension, slicing, decorator, parameter default, argumen bernama, chained comparison, format string f-string, dan banyak fitur lain ditolak dengan pesan yang menjelaskan batasnya. `import os` atau `import requests` tidak otomatis menjadi kemampuan Pusingcuk; modul dan dependensinya memerlukan integrasi terpisah. Beberapa perbedaan perilaku Python dan Pusingcuk mungkin tetap ada, sehingga hasil harus diuji dengan program asli.

Importer tidak mengeksekusi kode Python sumber. Namun, hasil Pusingcuk tetap harus diperlakukan sebagai kode biasa dan jangan menjalankan sumber yang tidak dipercaya dengan hak akses penting.

## Status

Tahap pertama ini menyediakan jalur eksperimen yang dapat diuji dan dikembangkan. Jangan menyebutnya kompatibel penuh dengan Python. Perluasan berikutnya harus menambah fitur sedikit demi sedikit disertai tes semantik, khususnya untuk scope variabel, nilai kebenaran, koleksi, dan perilaku error.
