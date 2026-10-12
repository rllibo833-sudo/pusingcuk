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
- Modul standar `math` dengan daftar izin eksplisit: `sqrt`, `floor`, `ceil`, `fabs`, `pow`, `sin`, `cos`, serta konstanta `pi` dan `e`. Bentuk `import math as m`, `from math import sqrt`, dan alias nama yang diimpor didukung.
- Fungsi dengan parameter posisi biasa tanpa nilai default, `return`, daftar, kamus, dan indeks.
- Boolean, perbandingan sederhana, `if/elif/else`, serta operator `and/or/not`.

## Hubungan dengan pustaka standar Pusingcuk

Pemetaan builtin umum memakai `panjang`, `rentang`, `mutlak`, `minimum`, `maksimum`, dan `bulatkan`. Integrasi `math` menambahkan builtin lintas backend JS/Python `akar`, `bawah`, `atas`, `pangkat`, `sinus`, dan `kosinus`; target HTML memakai backend JavaScript yang sama. Untuk menjaga arti tetap dekat dengan Python, `min` dan `max` dibatasi menjadi tepat dua argumen dan dimaksudkan untuk angka. `round` hanya menerima satu argumen; pembulatan Pusingcuk mengikuti aturan ties-to-even.

Konversi `teks`, `bilangan`, `desimal`, dan `logika` belum dipetakan karena implementasinya belum konsisten di seluruh backend. Modul lain seperti `os`, `sys`, `json`, `requests`, dan modul pihak ketiga tetap ditolak sampai tersedia adapter nyata. Import seperti `import os`, `import requests`, atau modul pihak ketiga tetap ditolak; nama modul tidak otomatis membuat API tersebut tersedia di Pusingcuk.

## Batasan penting

Ini **belum menerjemahkan semua Python**. Import modul (selain pemetaan builtin eksplisit di atas), kelas, exception handling, comprehension, slicing, decorator, parameter default, argumen bernama, chained comparison, format string f-string, dan banyak fitur lain ditolak dengan pesan yang menjelaskan batasnya. `import os` atau `import requests` tidak otomatis menjadi kemampuan Pusingcuk; modul dan dependensinya memerlukan integrasi terpisah. Beberapa perbedaan perilaku Python dan Pusingcuk mungkin tetap ada, sehingga hasil harus diuji dengan program asli.

Integrasi `math` sengaja dibatasi pada daftar fungsi/konstanta di atas; API seperti `math.log`, `math.exp`, `math.tan`, `math.isnan`, dan wildcard import tetap ditolak. Tes konformansi menjalankan contoh yang sama pada JavaScript dan HTML yang dihasilkan. Hasil lintas target tetap perlu diuji untuk domain/error numerik di program nyata.

Importer tidak mengeksekusi kode Python sumber. Namun, hasil Pusingcuk tetap harus diperlakukan sebagai kode biasa dan jangan menjalankan sumber yang tidak dipercaya dengan hak akses penting.

## Status

Tahap pertama ini menyediakan jalur eksperimen yang dapat diuji dan dikembangkan. Jangan menyebutnya kompatibel penuh dengan Python. Perluasan berikutnya harus menambah fitur sedikit demi sedikit disertai tes semantik, khususnya untuk scope variabel, nilai kebenaran, koleksi, dan perilaku error.


## Subset modul standar `statistics`

Importer secara eksplisit memetakan `statistics.mean` → `rata_rata` dan `statistics.median` → `median`. Bentuk `import statistics as stats`, `from statistics import mean`, dan alias impor didukung. Kedua fungsi menerima tepat satu daftar Pusingcuk nonkosong berisi angka finite; boolean dan nilai nonnumerik ditolak. Implementasinya diuji untuk target JavaScript, HTML (runtime JavaScript yang sama), dan Python.

Ini bukan kompatibilitas penuh modul Python `statistics`: `variance`, `stdev`, `pvariance`, `quantiles`, wildcard import, dan API lain ditolak secara eksplisit. VM dan runtime native C belum mendukung builtin ini.


## Sumber pemetaan dan batas kompatibilitas

`library/builtin_contract.json` adalah sumber metadata untuk pemetaan `math`, `statistics`, builtin Python umum, aritas, dan status target. Kode importer tetap bertanggung jawab menerjemahkan struktur AST dan menolak sintaks yang belum didukung; kontrak tidak menambahkan kemampuan host Python secara otomatis. Perubahan pemetaan harus disertai tes positif dan negatif, lalu diperiksa pada target yang ditandai `supported`.
