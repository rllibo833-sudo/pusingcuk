# Self-hosting frontend

Folder ini berisi sumber dan gerbang aktif untuk bootstrap frontend PusingCuk menggunakan `.cuk`. Untuk status terkini dan batas klaim, gunakan [status self-hosting kanonis](../../docs/SELF_HOSTING_STATE.md); catatan mini yang lebih lama di folder ini bukan jalur utama compiler.

## Jalur kanonis

- `compiler.cuk`: lexer, parser program/ekspresi, AST sementara, dan serialisasi ke IR v1.
- `compiler_driver.cuk`: driver JSON yang memproses `source_name` dan `source`.
- `ir_codegen.cuk`: codegen `.cuk` yang menerjemahkan IR v1 ke bytecode PusingCuk v1.
- `native/pusingcuk.c`: runtime/VM C yang menjadi seed bootstrap tepercaya.
- `tools/native-selfhost-bootstrap2.sh`: gerbang dua generasi native tanpa Python.

## Membuat IR atau bytecode melalui toolchain referensi

```sh
python -m compiler examples/hello.cuk --check
python -m compiler examples/hello.cuk --emit-ir /tmp/hello.ir.json
python -m compiler examples/hello.cuk --emit-bytecode /tmp/hello.bytecode.json
python -m unittest tests.test_compiled_frontend_vm -v
```

Perintah Python di atas merupakan jalur pengembangan/referensi. Jangan samakan dengan bukti jalur native bebas Python.

## Jalur native compile/run

Bangun runtime, lalu kompilasi dan jalankan program melalui native frontend dan bytecode VM:

```sh
make native
make native-compile FILE=examples/hello.cuk
make native-selfhost-bootstrap2
```

Target `native-compile` menjalankan frontend dan codegen `.cuk` di runtime C; Python tidak menjalankan parser atau VM pada jalur tersebut. Target bootstrap menjalankan frontend generasi 1 dan 2 pada input probe yang sama, memeriksa IR identik dan menampilkan SHA-256 untuk kedua keluaran. Hasil hanya berlaku jika target selesai sukses pada commit yang sama dengan run CI.

## Apa arti keberhasilan bootstrap?

Bootstrap membuktikan generasi frontend/codegen yang diuji mampu membangun dan menjalankan generasi berikutnya dengan keluaran probe identik. **Runtime C masih merupakan seed**. Ini bukan klaim bahwa runtime C telah diganti dengan `.cuk`, semua semantik bahasa sudah ada di codegen native, seluruh backend setara, atau seluruh repositori bebas Python.

Validator IR kanonis penuh tetap tersedia di `compiler/ir.py` dalam jalur Python. Runtime native memeriksa envelope dan fitur yang diperlukan oleh codegen subsetnya. Bootstrap bukan sandbox sistem operasi; jangan menjalankan source tak tepercaya dengan asumsi isolasi.

## Contoh mini/historis

`parser.cuk`, `evaluator.cuk`, `interpreter.cuk`, `codegen.cuk`, dan prototipe `source_lexer.cuk` dipertahankan untuk pembelajaran/evolusi bertahap. Berkas tersebut bukan pengganti jalur kanonis `compiler.cuk` + `compiler_driver.cuk` + `ir_codegen.cuk`.
