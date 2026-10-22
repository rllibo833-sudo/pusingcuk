# Status self-hosting .cuk — sumber kebenaran

**Diperbarui:** 22 Oktober 2026. Dokumen ini adalah status aktif self-hosting; milestone lama di roadmap dan audit bertanggal merupakan riwayat, bukan status terbaru.

## Status yang sudah dicapai

Frontend compiler `.cuk` kini memiliki jalur bootstrap dua generasi yang menggunakan runtime native C sebagai seed, tanpa Python menjalankan parser, codegen, atau VM pada jalur tersebut. Gerbang utama adalah:

`make native-selfhost-bootstrap2`

Alurnya:
1. Menggabungkan `examples/self_hosting/compiler.cuk` dan `compiler_driver.cuk` sebagai sumber frontend/driver.
2. Runtime native C menjalankan frontend sumber untuk menghasilkan IR v1 tahap awal.
3. `examples/self_hosting/ir_codegen.cuk` mengubah IR tersebut menjadi bytecode frontend tahap 1.
4. Frontend tahap 1 dijalankan untuk mengompilasi ulang sumber frontend yang sama. IR yang dihasilkan dibandingkan byte-for-byte dengan IR tahap awal.
5. Codegen `.cuk` mengubah IR hasil tahap 1 menjadi bytecode frontend tahap 2. Kedua generasi kemudian memproses probe yang sama; hasil IR dibandingkan memakai `cmp` dan SHA-256.

**Makna bukti:** dua generasi frontend memberi keluaran IR identik untuk probe yang sama. Gerbang hanya dianggap lulus jika perintah tersebut sukses pada commit yang sama dengan hasil CI; keberadaan skrip atau dua hash dari commit berbeda bukan bukti CI.

## Bedakan jalur-jalur ini

- **Native bootstrap:** `tools/native-selfhost-bootstrap2.sh` dan target Make `native-selfhost-bootstrap2`. Inilah gerbang bootstrap native dua generasi.
- **Kompilasi program native:** `make native-compile FILE=program.cuk`. Jalur ini memakai frontend dan codegen `.cuk`, lalu bytecode VM pada runtime C; Python tidak menjalankan langkah kompilasi atau program tersebut.
- **Harness parity Python:** `compiler/bootstrap.py` membandingkan frontend yang berjalan melalui Python Evaluator dengan frontend dalam VM Python. Ini masih berguna sebagai tes pembanding, tetapi **bukan** bukti bootstrap native tanpa Python.
- **Validator IR kanonis:** `compiler/ir.py` tetap menjadi validator skema IR penuh pada toolchain Python. Pemeriksaan envelope di jalur `.cuk` bukan klaim bahwa seluruh validator skema sudah ditulis ulang dalam `.cuk`.

## Sumber aktif

| Berkas | Peran |
|---|---|
| `examples/self_hosting/compiler.cuk` | Lexer, parser, AST sementara, dan serialisasi AST ke IR v1 |
| `examples/self_hosting/compiler_driver.cuk` | Driver JSON untuk menjalankan frontend dari stdin |
| `examples/self_hosting/ir_codegen.cuk` | Codegen IR v1 ke bytecode PusingCuk v1 |
| `native/pusingcuk.c` | Runtime/VM native C yang menjadi seed bootstrap tepercaya |
| `tools/native-selfhost-bootstrap2.sh` | Menguji pembentukan generasi 1 dan 2 serta identitas keluaran probe |
| `tools/cukc-native.sh` | Jalur kompilasi native end-to-end |
| `compiler/bootstrap.py` | Harness parity Python yang terpisah, bukan bootstrap native |

`source_lexer.cuk`, `parser.cuk`, `evaluator.cuk`, `interpreter.cuk`, dan `codegen.cuk` adalah contoh/milestone mini; jangan menganggap semuanya sebagai jalur compiler kanonis.

## Gate dan perintah verifikasi

```sh
make native
make native-selfhost-bootstrap2
make native-compile FILE=examples/hello.cuk
python -m unittest tests.test_native_bootstrap_pipeline -v
```

Workflow `.github/workflows/tests.yml` menjalankan tes native dan `make native-selfhost-bootstrap2`. Workflow contoh juga memeriksa sintaks semua berkas `.cuk` di `examples/`; kegagalan pada contoh harus diperbaiki, bukan diabaikan. Untuk klaim hasil terkini, cek workflow yang menyebut SHA commit yang sama.

## Batas klaim

- Bootstrap ini membuktikan loop frontend/codegen native pada subset yang diuji, bukan kesetaraan semua fitur bahasa di seluruh backend.
- Runtime C tetap menjadi seed tepercaya. Ini tidak berarti runtime, VM, atau seluruh compiler ditulis dalam `.cuk`.
- Tool pengembangan, interpreter referensi, paket Python, dan validator IR kanonis masih memakai Python. Yang bebas Python adalah jalur native compile/run yang didokumentasikan, bukan seluruh repositori.
- Bootstrap dan tes konformansi bukan sandbox sistem operasi. Jangan jalankan program tak tepercaya dengan asumsi terisolasi.
- Status rilis tetap eksperimental; bootstrap yang lulus tidak membuat semua backend setara atau perangkat lunak otomatis siap produksi.
