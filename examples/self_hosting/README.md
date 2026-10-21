# Self-hosting prototypes (.cuk)

Folder ini berisi prototipe bertahap yang ditulis dengan bahasa `.cuk` untuk menguji apakah bahasa ini bisa menjadi alat bagi pengembangan toolchain-nya sendiri.

**Penting:** ini belum merupakan compiler PusingCuk yang self-hosted. `source_lexer.cuk` menjalankan jalur teks sumber → token → recursive-descent parser → AST → evaluator untuk ekspresi integer (`+`, `-`, `*`, `/`, `%`, unary minus, prioritas operator, dan tanda kurung) serta literal string dengan escape dasar (`\\n`, `\\t`, `\\r`, kutip, dan backslash). Parser program terbatas pada deklarasi `lah nama = ekspresi`, assignment `nama = ekspresi`, dan alias output yang tercantum di parser (tidak termasuk `gas`, yang merupakan alias pembuka program pada lexer kanonis). `compiler/self_hosted_frontend.py` mengubah AST subset tersebut menjadi IR v1 kanonis yang divalidasi dan dipakai backend yang sudah ada; tes membandingkan hasilnya dengan frontend Python termasuk literal string ber-escape. Kontrol alur, fungsi, angka pecahan, diagnostik sumber lengkap, dan frontend mandiri tanpa adapter Python belum didukung. Ini belum parser/compiler `.cuk` penuh. `codegen.cuk` belum menjalankan compiler.

## Contoh

| Berkas | Peran saat ini | Batasan utama |
|---|---|---|
| `lexer.cuk` | Mengklasifikasikan satu token operator | Demo kecil, bukan scanner |
| `source_lexer.cuk` | Lexer, parser precedence, AST/evaluator ekspresi integer dan string, program terbatas | Deklarasi/assignment/output dan ekspresi integer/string; belum ada kontrol alur, angka pecahan, floor division, diagnostik sumber lengkap, atau compiler mandiri |
| `parser.cuk` | Membentuk node aritmetika dari token sederhana atau token terstruktur | Satu ekspresi `INTEGER OP INTEGER EOF`; belum ada prioritas operator atau tanda kurung |
| `evaluator.cuk` | Mengevaluasi node aritmetika | Belum menjalankan AST bahasa `.cuk` |
| `interpreter.cuk` | Menghubungkan tahap mini lexer → parser → evaluator | Input masih daftar token yang sudah disiapkan |
| `codegen.cuk` | Menghasilkan ekspresi C bersarang dari AST integer/biner buatan tangan | Bukan compiler source-to-source; operator yang belum didukung ditolak |
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

Tes otomatis di `tests/test_self_hosting_examples.py` memeriksa exit code dan output yang diharapkan, termasuk batas newline dan komentar pada lexer, prioritas `2 + 3 * 4`, tanda kurung `(2 + 3) * 4`, modulo `17 % 5`, unary minus `-3 * 4`, serta penolakan `7 %` yang tidak lengkap dan parsing struktur program multi-baris terbatas. Lulus pada interpreter referensi hanya membuktikan prototipe berjalan di target itu; tidak berarti target native/browser mendukungnya.

## Jalur menuju self-hosting sungguhan

1. Stabilkan kontrak bahasa dan suite konformansi lintas runtime.
2. Tambahkan operasi string/karakter dan struktur data yang dibutuhkan lexer source penuh.
3. Bangun lexer dan parser `.cuk` yang membaca source bahasa `.cuk` itu sendiri.
4. Definisikan AST/IR versi stabil yang bisa dipakai interpreter dan compiler backend.
5. Implementasikan evaluator/VM dan code generator secara bertahap, masing-masing dengan fixture konformansi.
6. Buktikan bootstrap: compiler `.cuk` yang dibangun oleh toolchain lama mampu membangun ulang versi dirinya sendiri dengan hasil yang dapat dibandingkan.

Jangan menyebut PusingCuk self-hosted sebelum tahap bootstrap dapat diulang dan diverifikasi di CI.


Code generation kini menguji serialisasi rekursif AST aritmetika bersarang ke ekspresi C dan menolak operator yang belum didukung. Ini tetap generator ekspresi, bukan compiler lintas bahasa penuh: inputnya belum source program umum dan belum terhubung ke IR v1/manifest backend.


## Jalur frontend self-hosted ke toolchain kanonis

`compiler/self_hosted_frontend.py` menjalankan lexer/parser yang ditulis di `.cuk`, menerima AST hasil parse, lalu membungkusnya menjadi IR v1 kanonis yang divalidasi dan digunakan backend yang sudah ada. Ini jalur eksperimen terbatas untuk deklarasi, assignment, output, dan ekspresi numerik; belum menggantikan parser referensi untuk semua sintaks.

```sh
python -m compiler program.cuk --frontend selfhosted --target json
python -m compiler program.cuk --frontend selfhosted --target js
python -m compiler program.cuk --frontend selfhosted --target vm
```

Tes membandingkan AST IR frontend self-hosted dengan frontend kanonis untuk subset yang sama dan memeriksa penolakan sintaks malformed. Parser `.cuk` juga mengenali seluruh alias output yang dipetakan di grammar kanonis; tes parity menjalankan semua alias dalam satu program. Dukungan kontrol alur dan input belum dipetakan di bridge ini. Ini bukti integrasi frontend-ke-IR/backend untuk subset tersebut, **bukan** bukti bootstrap compiler mandiri. Bootstrap baru terbukti saat compiler yang diimplementasikan dalam `.cuk` dapat membangun ulang dirinya sendiri berulang kali.
