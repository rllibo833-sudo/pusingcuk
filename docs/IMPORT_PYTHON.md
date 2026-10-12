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
- `range()` menjadi `rentang()`, `len()` menjadi `panjang()`.
- Fungsi dengan parameter posisi biasa, `return`, daftar, kamus, dan indeks.
- Boolean, perbandingan sederhana, serta operator `and/or/not`.

## Batasan penting

Ini **belum menerjemahkan semua Python**. Import modul, kelas, exception handling, comprehension, slicing, decorator, parameter default, argumen bernama, chained comparison, serta banyak fitur lain ditolak dengan pesan yang menjelaskan batasnya. `import os` atau `import requests` tidak otomatis menjadi kemampuan Pusingcuk; modul dan dependensinya memerlukan integrasi terpisah. Beberapa perbedaan perilaku Python dan Pusingcuk mungkin tetap ada, sehingga hasil harus diuji dengan program asli.

Importer tidak mengeksekusi kode Python sumber. Namun, hasil Pusingcuk tetap harus diperlakukan sebagai kode biasa dan jangan menjalankan sumber yang tidak dipercaya dengan hak akses penting.

## Status

Tahap pertama ini menyediakan jalur eksperimen yang dapat diuji dan dikembangkan. Jangan menyebutnya kompatibel penuh dengan Python. Perluasan berikutnya harus menambah fitur sedikit demi sedikit disertai tes semantik, khususnya untuk scope variabel, nilai kebenaran, koleksi, dan perilaku error.
