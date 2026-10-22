# Self-hosting .cuk frontend

Folder ini menyimpan contoh bertahap untuk membangun toolchain PusingCuk dengan bahasa .cuk sendiri. Berkas compiler.cuk menjadi sumber lexer, parser program/ekspresi, AST, dan serializer IR v1.

## Jalur aktif

compiler/self_hosted_frontend.py menjalankan sumber compiler .cuk melalui class `Evaluator` di `evaluator.py`, lalu memvalidasi dokumen IR v1. Jalur default compiler adalah:

source .cuk → lexer/parser .cuk → AST → IR v1 → bytecode → VM

Parser frontend menangani deklarasi, assignment variabel dan indeks, output, pemanggilan fungsi, fungsi/return, kondisi njir/kampret, loop mumet/untuk, literal list/dictionary, indexing, unary/binary expression, dan akses member sederhana. Semua hasil serializer melewati validator IR kanonis; hal ini tidak menjamin seluruh semantik runtime tersedia di semua backend.

## Perintah

    python -m compiler examples/hello.cuk --check
    python -m compiler examples/hello.cuk --emit-ir /tmp/hello.ir.json
    python -m compiler examples/hello.cuk --emit-bytecode /tmp/hello.bytecode.json
    python -m unittest tests.test_compiled_frontend_vm -v

parser.cuk, evaluator.cuk, interpreter.cuk, dan codegen.cuk tetap dipertahankan sebagai contoh mini tahap compiler; semuanya bukan implementasi compiler lengkap.

## Menjalankan frontend `.cuk` dengan runtime native C

`compiler.cuk` menyediakan driver JSON pada stdin. Bangun runtime C dengan `make native`, lalu jalankan `./pusingcuk-native examples/self_hosting/compiler.cuk < payload.json`, dengan payload JSON yang memiliki `source_name` dan `source`. Jalur ini menjalankan lexer/parser/AST/IR yang ditulis dalam `.cuk` melalui runtime native C; Python tidak mem-parsing source target. Tes `test_checked_in_cuk_frontend_runs_on_native_c_runtime` membandingkan IR-nya dengan kontrak referensi.

## Status self-hosting

Frontend .cuk kini memiliki tes yang mem-parsing sumber frontend-nya sendiri dan membandingkan AST IR dengan parser referensi. Eksekusi frontend masih di-host oleh `Evaluator` Python di `evaluator.py` (runtime yang juga digunakan oleh `pusingcuk_new.py`); validasi IR dan kompilasi bytecode juga masih memakai implementasi Python. compiler/bootstrap.py saat ini hanya memverifikasi pengulangan build pada jalur host yang sama, bukan bootstrap mandiri dua tahap.

Jangan klaim .cuk self-hosted penuh sampai tahap pertama membangun compiler yang dapat dijalankan sebagai compiler tahap kedua, lalu compiler tahap kedua mengompilasi ulang sumber compiler dan menghasilkan artefak yang cocok tanpa Python mem-parsing atau mengompilasi program.


## Jalur kompilasi native tanpa Python

Setelah runtime native dibangun dengan make native, jalankan make native-compile FILE=program.cuk. Jalur ini meng-encode source melalui opsi native --json-quote, menjalankan compiler.cuk dan compiler_driver.cuk di runtime C untuk menghasilkan IR v1, menjalankan ir_codegen.cuk untuk menghasilkan bytecode, lalu mengeksekusinya dengan VM native. INPUT=berkas.txt dapat diberikan untuk stdin program hasil kompilasi. Tidak ada Python yang menjalankan parser, frontend, codegen, atau VM pada jalur ini.

Ini menghilangkan Python dari jalur kompilasi dan eksekusi program, tetapi belum membuktikan compiler mandiri penuh: runtime C masih menjadi seed tepercaya, dan bootstrap tahap 2/3 compiler belum dibuktikan.


Frontend `.cuk` memperlakukan pembungkus modul `jancuk` / `selesai jancuk` sebagai delimiter berkas, bukan statement di dalam program. Ini diperlukan agar source target yang normal bisa diproses lewat frontend native.
