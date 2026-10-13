# Compiler multi-target PusingCuk

**Versi bahasa:** `0.4-dev`. Target compiler tetap eksperimental dan tidak mewarisi dukungan hanya karena interpreter reference memilikinya.

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

## Arti target keluar

- **js**: source JavaScript yang dapat dijalankan Node.js; input terminal memakai stdin dan di browser memakai prompt.
- **python**: source Python mandiri untuk subset bahasa yang didukung backend Python.
- **html**: halaman browser dengan JavaScript tersemat dan panel output. Ini bukan framework frontend dan belum menyediakan DOM bindings PusingCuk.
- **json**: serialisasi IR v1 yang tervalidasi. JSON IR adalah format pertukaran compiler, bukan program yang dapat dieksekusi langsung.
- **vm**: bytecode stack versi 1 yang dijalankan oleh VM referensi melalui `python -m compiler.vm`.

## Menerjemahkan Python masuk

Eksperimen awal Python → Pusingcuk tersedia melalui:

```sh
python -m compiler.import_python program.py --output program.cuk
python -m compiler program.cuk --target js --output program.js
node program.js
```

Importer menggunakan struktur sintaks Python, lalu menghasilkan sumber Pusingcuk. Cakupan mencakup variabel, fungsi dasar, koleksi, kondisi termasuk `elif`, loop, builtin numerik `abs/round/min/max`, dan subset modul standar `math`: `sqrt/floor/ceil/fabs/pow/sin/cos` serta `pi/e`. Builtin math tambahan diuji pada backend JavaScript dan HTML (HTML menyematkan runtime JavaScript yang sama). Ini **hanya subset**, bukan kompatibilitas penuh Python; modul eksternal, API math yang tidak terdaftar, kelas, exception handling, comprehension, dan sejumlah konstruksi lain ditolak dengan pesan jelas. Lihat [cakupan dan batas importer](IMPORT_PYTHON.md).

Backend menolak konstruksi yang belum dikenali alih-alih diam-diam menerjemahkannya secara keliru. Target yang berbeda belum menjamin kesetaraan penuh semua semantik; cakupan tiap backend harus diperluas lewat tes konformansi.

## Jalur pengembangan

`PusingCuk → parser/IR → backend`

Untuk bahasa yang masuk, jalurnya dimulai dari parser khusus bahasa sumber, diterjemahkan ke bentuk yang didukung Pusingcuk, lalu divalidasi dan diuji. IR dirancang sebagai titik integrasi untuk backend baru, language server, formatter, editor, alat AI, dan pipeline build. Target berikutnya adalah memperluas interoperabilitas modul dan package, browser APIs, WebAssembly, server/API, database adapters, serta blockchain SDK. Semua itu memerlukan backend atau pustaka integrasi khusus; tidak otomatis tersedia hanya karena target JS/Python/HTML ada.

## Builtin lintas target

Target JavaScript, Python, dan VM mendukung builtin numerik `mutlak(angka)`,
`minimum(a, b)`, `maksimum(a, b)`, dan `bulatkan(angka)`. Input harus berupa
angka finite; boolean ditolak. Pembulatan `.5` menggunakan aturan ties-to-even
agar hasil konsisten antartarget. Builtin konversi lain yang tercatat di
[model tipe dan pustaka standar](compiler-type-system-and-stdlib.md) belum
diaktifkan di semua backend.


## Statistics builtins and compatibility

The importer supports `statistics.mean` and `statistics.median`, mapped to `rata_rata(daftar)` and `median(daftar)`. These are implemented and tested on JavaScript, Python, and HTML (which embeds the JS runtime). Inputs must be a non-empty list of finite numbers; booleans are rejected. The VM and native C runtime do not claim support. The presence of these builtins does not mean the full Python `statistics` module is compatible.


## Kontrak builtin bersama

Metadata nama builtin, jumlah argumen, pemetaan importer Python, helper backend, dan status kompatibilitas bersumber dari [`library/builtin_contract.json`](../library/builtin_contract.json). Registry referensi, importer, backend JS/Python, dan pemeriksaan konformansi membaca kontrak yang sama. Implementasi runtime tetap terpisah karena operasi Python, JavaScript, VM, dan native C tidak identik secara otomatis.

Status `supported` hanya boleh dipakai jika implementasi dan tes target tersedia. `unsupported` berarti target diketahui belum memiliki implementasi; `not-claimed` berarti kompatibilitas belum diverifikasi. HTML berbagi runtime JavaScript, bukan runtime browser terpisah. Database, server, Web3, blockchain, dan API browser bukan bagian dari builtin core.
