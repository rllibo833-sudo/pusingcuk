# Self-hosting prototypes (.cuk)

Folder ini berisi prototipe bertahap yang ditulis dengan bahasa `.cuk` untuk menguji apakah bahasa ini bisa menjadi alat bagi pengembangan toolchain-nya sendiri.

**Penting:** ini belum merupakan compiler PusingCuk yang self-hosted. `source_lexer.cuk` kini menjalankan jalur teks sumber → token → recursive-descent parser → AST → evaluator untuk ekspresi integer dengan `+`, `-`, `*`, `/`, `%`, unary minus, prioritas operator, dan tanda kurung. Contoh menguji `2 + 3 * 4 = 14`, `(2 + 3) * 4 = 20`, `17 % 5 = 2`, `-3 * 4 = -12`, serta penolakan ekspresi `%` yang tidak lengkap. Ini masih grammar ekspresi kecil, bukan parser program `.cuk` penuh. `codegen.cuk` belum menjalankan compiler.

## Contoh

| Berkas | Peran saat ini | Batasan utama |
|---|---|---|
| `lexer.cuk` | Mengklasifikasikan satu token operator | Demo kecil, bukan scanner |
| `source_lexer.cuk` | Lexer, parser precedence, AST, evaluator ekspresi integer | Grammar ekspresi; belum mem-parse pernyataan/program penuh, alias keyword, angka pecahan, floor division, atau decoding escape |
| `parser.cuk` | Membentuk node aritmetika dari token sederhana atau token terstruktur | Satu ekspresi `INTEGER OP INTEGER EOF`; belum ada prioritas operator atau tanda kurung |
| `evaluator.cuk` | Mengevaluasi node aritmetika | Belum menjalankan AST bahasa `.cuk` |
| `interpreter.cuk` | Menghubungkan tahap mini lexer → parser → evaluator | Input masih daftar token yang sudah disiapkan |
| `codegen.cuk` | Menghasilkan satu baris teks mirip kode C | Tidak mengompilasi atau menjalankan C |
| `runtime_contract.cuk` | Menunjukkan cara melaporkan dukungan fitur secara eksplisit | Data ilustratif, bukan hasil pengujian runtime |

## Jalankan dari root repository

```sh
python pusingcuk_new.py examples/self_hosting/lexer.cuk
python pusingcuk_new.py examples/self_hosting/source_lexer.cuk
python pusingcuk_new.py examples/self_hosting/parser.cuk
python pusingcuk_new.py examples/self_hosting/evaluator.cuk
python pusingcuk_new.py examples/self_hosting/interpreter.cuk
python pusingcuk_new.py examples/self_hosting/codegen.cuk
python pusingcuk_new.py examples/self_hosting/runtime_contract.cuk
```

Tes otomatis di `tests/test_self_hosting_examples.py` memeriksa exit code dan output yang diharapkan, termasuk batas newline dan komentar pada lexer, prioritas `2 + 3 * 4`, tanda kurung `(2 + 3) * 4`, modulo `17 % 5`, unary minus `-3 * 4`, serta penolakan `7 %` yang tidak lengkap. Lulus pada interpreter referensi hanya membuktikan prototipe berjalan di target itu; tidak berarti target native/browser mendukungnya.

## Jalur menuju self-hosting sungguhan

1. Stabilkan kontrak bahasa dan suite konformansi lintas runtime.
2. Tambahkan operasi string/karakter dan struktur data yang dibutuhkan lexer source penuh.
3. Bangun lexer dan parser `.cuk` yang membaca source bahasa `.cuk` itu sendiri.
4. Definisikan AST/IR versi stabil yang bisa dipakai interpreter dan compiler backend.
5. Implementasikan evaluator/VM dan code generator secara bertahap, masing-masing dengan fixture konformansi.
6. Buktikan bootstrap: compiler `.cuk` yang dibangun oleh toolchain lama mampu membangun ulang versi dirinya sendiri dengan hasil yang dapat dibandingkan.

Jangan menyebut PusingCuk self-hosted sebelum tahap bootstrap dapat diulang dan diverifikasi di CI.
