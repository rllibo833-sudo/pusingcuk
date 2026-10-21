# Self-hosting .cuk frontend

Folder ini menyimpan contoh bertahap untuk membangun toolchain PusingCuk dengan bahasa .cuk sendiri. Berkas compiler.cuk menjadi sumber lexer, parser program/ekspresi, AST, dan serializer IR v1.

## Jalur aktif

compiler/self_hosted_frontend.py menjalankan frontend .cuk melalui host pusingcuk_new.py, lalu memvalidasi dokumen IR v1. Jalur default compiler adalah:

source .cuk → lexer/parser .cuk → AST → IR v1 → bytecode → VM

Parser frontend menangani deklarasi, assignment variabel dan indeks, output, pemanggilan fungsi, fungsi/return, kondisi njir/kampret, loop mumet/untuk, literal list/dictionary, indexing, unary/binary expression, dan akses member sederhana. Semua hasil serializer melewati validator IR kanonis; hal ini tidak menjamin seluruh semantik runtime tersedia di semua backend.

## Perintah

    python -m compiler examples/hello.cuk --check
    python -m compiler examples/hello.cuk --emit-ir /tmp/hello.ir.json
    python -m compiler examples/hello.cuk --emit-bytecode /tmp/hello.bytecode.json
    python -m unittest tests.test_compiled_frontend_vm -v

parser.cuk, evaluator.cuk, interpreter.cuk, dan codegen.cuk tetap dipertahankan sebagai contoh mini tahap compiler; semuanya bukan implementasi compiler lengkap.

## Status self-hosting

Frontend .cuk kini memiliki tes yang mem-parsing sumber frontend-nya sendiri dan membandingkan AST IR dengan parser referensi. Eksekusi frontend masih di-host oleh interpreter Python pusingcuk_new.py; validasi IR dan kompilasi bytecode juga masih memakai implementasi Python. compiler/bootstrap.py saat ini hanya memverifikasi pengulangan build pada jalur host yang sama, bukan bootstrap mandiri dua tahap.

Jangan klaim .cuk self-hosted penuh sampai tahap pertama membangun compiler yang dapat dijalankan sebagai compiler tahap kedua, lalu compiler tahap kedua mengompilasi ulang sumber compiler dan menghasilkan artefak yang cocok tanpa Python mem-parsing atau mengompilasi program.
