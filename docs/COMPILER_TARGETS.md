# Compiler multi-target PusingCuk

**Versi bahasa:** `0.6-dev`. Target compiler tetap eksperimental dan tidak mewarisi dukungan hanya karena interpreter reference memilikinya.

Compiler CLI mengubah satu sumber PusingCuk melalui parser dan IR v1 menjadi artefak target.

## Perintah

```sh
# C11 native untuk kompilasi menjadi executable tanpa interpreter Python saat runtime
python -m compiler program.cuk --target c --output program.c
cc -std=c11 -O2 -Wall -Wextra -Werror program.c -lm -o program
./program

# C++17 untuk executable mandiri
python -m compiler program.cuk --target cpp --output program.cpp
g++ -std=c++17 -O2 program.cpp -o program
./program

# JavaScript untuk Node.js
python -m compiler program.pusingcuk --target js --output program.js
node program.js

# Python
python -m compiler program.pusingcuk --target python --output program.py
python program.py

# HTML mandiri untuk browser; JavaScript disematkan
python -m compiler program.pusingcuk --target html --output program.html


# Rust untuk subset numerik mandiri
python -m compiler program.cuk --target rust --output program.rs
rustc program.rs -o program
./program

# JSON IR untuk tooling, editor, dan integrasi AI
python -m compiler program.pusingcuk --target json --output program.ir.json

# Bytecode VM portabel
python -m compiler program.pusingcuk --target vm --output program.pbc.json
python -m compiler.vm program.pbc.json
```

Target default adalah `js`. Tanpa `--output`, hasil ditulis ke stdout.

## Arti target keluar

- **cpp**: source C++17 mandiri dengan runtime nilai PusingCuk tertanam; subset awal diuji terhadap 55 fixture konformansi. `Input`, `Try`, JSON/HTML/CSV, impor, dan fitur di luar manifest C++ belum diklaim kompatibel. Compile-time berjalan melalui Python; executable hasil C++ berjalan tanpa interpreter Python.
- **c**: source C11 untuk subset yang didukung backend native. Compiler saat build masih dijalankan dengan Python; setelah source C dikompilasi menjadi executable, program hasilnya tidak membutuhkan interpreter Python. Fitur di luar subset C ditolak dengan diagnostik, bukan dijalankan lewat fallback Python.
- **js**: source JavaScript yang dapat dijalankan Node.js; input terminal memakai stdin dan di browser memakai prompt.
- **python**: source Python mandiri untuk subset bahasa yang didukung backend Python.
- **rust**: source Rust mandiri untuk subset numerik terbatas: literal angka, variabel, assignment, output, unary minus, dan `+ - * / // %`. Gunakan `rustc` untuk membangun executable. Fitur lain ditolak saat kompilasi; ini belum kompatibilitas penuh Rust.
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

Blok `coba ... ketangkep ... akhirnya ... selesai coba` saat ini diterjemahkan oleh target JavaScript dan Python untuk penanganan exception runtime; variabel `ketangkep` berisi pesan error dan `akhirnya` dijalankan ketika blok selesai maupun saat error diteruskan. Backend C native tetap tidak mendukung `Try`, sesuai batas subset yang dinyatakan pada SPEC. Tes target tidak menyatakan semua diagnostik runtime identik byte-per-byte.

Backend menolak konstruksi yang belum dikenali alih-alih diam-diam menerjemahkannya secara keliru. Target yang berbeda belum menjamin kesetaraan penuh semua semantik; cakupan tiap backend harus diperluas lewat tes konformansi.

## Jalur pengembangan

`PusingCuk → parser/IR → backend`

Untuk bahasa yang masuk, jalurnya dimulai dari parser khusus bahasa sumber, diterjemahkan ke bentuk yang didukung Pusingcuk, lalu divalidasi dan diuji. IR dirancang sebagai titik integrasi untuk backend baru, language server, formatter, editor, alat AI, dan pipeline build. Target berikutnya adalah memperluas cakupan C++ lalu menambahkan backend Kotlin mandiri; setelah itu interoperabilitas modul dan package, browser APIs, WebAssembly, server/API, database adapters, serta blockchain SDK. Semua itu memerlukan backend atau pustaka integrasi khusus; tidak otomatis tersedia hanya karena target JS/Python/HTML ada.

## Builtin lintas target

Target C++17, JavaScript, Python, dan VM mendukung builtin numerik `mutlak(angka)`,
`minimum(a, b)`, `maksimum(a, b)`, dan `bulatkan(angka)`. Input harus berupa
angka finite; boolean ditolak. Pembulatan `.5` menggunakan aturan ties-to-even
agar hasil konsisten antartarget. Builtin konversi lain yang tercatat di
[model tipe dan pustaka standar](compiler-type-system-and-stdlib.md) belum
diaktifkan di semua backend.


## Statistics builtins and compatibility

The importer supports `statistics.mean` and `statistics.median`, mapped to `rata_rata(daftar)` and `median(daftar)`. These are implemented and tested on JavaScript, Python, and HTML (which embeds the JS runtime). Inputs must be a non-empty list of finite numbers; booleans are rejected. The VM and native C runtime do not claim support. C++17 support is limited to the explicitly selected compiler fixture manifest. The presence of these builtins does not mean the full Python `statistics` module is compatible.


## Kontrak builtin bersama

Metadata nama builtin, jumlah argumen, pemetaan importer Python, helper backend, dan status kompatibilitas bersumber dari [`library/builtin_contract.json`](../library/builtin_contract.json). Registry referensi, importer, backend JS/Python, dan pemeriksaan konformansi membaca kontrak yang sama. Implementasi runtime tetap terpisah karena operasi Python, JavaScript, VM, dan native C tidak identik secara otomatis.

Status `supported` hanya boleh dipakai jika implementasi dan tes target tersedia. `unsupported` berarti target diketahui belum memiliki implementasi; `not-claimed` berarti kompatibilitas belum diverifikasi. HTML berbagi runtime JavaScript, bukan runtime browser terpisah. Database, server, Web3, blockchain, dan API browser bukan bagian dari builtin core.
