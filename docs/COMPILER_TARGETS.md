# Compiler multi-target PusingCuk

Compiler CLI mengubah satu sumber PusingCuk melalui parser dan IR v1 menjadi artefak target.

## Perintah

```sh
# JavaScript untuk Node.js
python -m compiler program.pusingcuk --target js --output program.js
node program.js

# Python
python -m compiler program.pusingcuk --target python --output program.py
python program.py

# HTML mandiri untuk browser; JavaScript disematkan
python -m compiler program.pusingcuk --target html --output program.html

# JSON IR untuk tooling, editor, dan integrasi AI
python -m compiler program.pusingcuk --target json --output program.ir.json

# Bytecode VM portabel
python -m compiler program.pusingcuk --target vm --output program.pbc.json
python -m compiler.vm program.pbc.json
```

Target default adalah `js`. Tanpa `--output`, hasil ditulis ke stdout.

## Arti target

- **js**: source JavaScript yang dapat dijalankan Node.js; input terminal memakai stdin dan di browser memakai prompt.
- **python**: source Python mandiri untuk subset bahasa yang didukung backend Python.
- **html**: halaman browser dengan JavaScript tersemat dan panel output. Ini bukan framework frontend dan belum menyediakan DOM bindings PusingCuk.
- **json**: serialisasi IR v1 yang tervalidasi. JSON IR adalah format pertukaran compiler, bukan program yang dapat dieksekusi langsung.
- **vm**: bytecode stack versi 1 yang dijalankan oleh VM referensi melalui `python -m compiler.vm`.

Backend menolak konstruksi yang belum dikenali alih-alih diam-diam menerjemahkannya secara keliru. Target yang berbeda belum menjamin kesetaraan penuh semua semantik; cakupan tiap backend harus diperluas lewat tes konformansi.

## Jalur pengembangan

`PusingCuk → parser/IR → backend`

IR dirancang sebagai titik integrasi untuk backend baru, language server, formatter, editor, alat AI, dan pipeline build. Target berikutnya adalah memperluas interoperabilitas modul dan package, browser APIs, WebAssembly, server/API, database adapters, serta blockchain SDK. Semua itu memerlukan backend atau pustaka integrasi khusus; tidak otomatis tersedia hanya karena target JS/Python/HTML ada.


## Builtin lintas target

Target JavaScript, Python, dan VM mendukung builtin numerik `mutlak(angka)`,
`minimum(a, b)`, `maksimum(a, b)`, dan `bulatkan(angka)`. Input harus berupa
angka finite; boolean ditolak. Pembulatan `.5` menggunakan aturan ties-to-even
agar hasil konsisten antartarget. Builtin konversi lain yang tercatat di
[model tipe dan pustaka standar](compiler-type-system-and-stdlib.md) belum
diaktifkan di semua backend.
