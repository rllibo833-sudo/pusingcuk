# Self-hosting prototypes (.cuk)

Folder ini berisi prototipe bertahap yang ditulis dengan bahasa `.cuk` untuk menguji apakah bahasa ini bisa menjadi alat bagi pengembangan toolchain-nya sendiri.

**Penting:** ini belum merupakan compiler PusingCuk yang self-hosted. Lexer saat ini hanya mengklasifikasikan satu token yang sudah dipisahkan; parser hanya menerima bentuk aritmetika `nilai operator nilai`; evaluator hanya menghitung node biner kecil; dan code generator hanya menghasilkan teks C sebagai demonstrasi. Belum ada pemindaian source penuh, grammar bahasa `.cuk`, modul yang saling mengimpor, atau compiler mandiri.

## Contoh

| Berkas | Peran saat ini | Batasan utama |
|---|---|---|
| `lexer.cuk` | Mengklasifikasikan satu token operator | Belum memecah source menjadi token |
| `parser.cuk` | Membentuk node data dari tiga token | Hanya satu ekspresi aritmetika |
| `evaluator.cuk` | Mengevaluasi node aritmetika | Belum menjalankan AST bahasa `.cuk` |
| `interpreter.cuk` | Menghubungkan tahap mini lexer → parser → evaluator | Input masih daftar token yang sudah disiapkan |
| `codegen.cuk` | Menghasilkan satu baris teks mirip kode C | Tidak mengompilasi atau menjalankan C |
| `runtime_contract.cuk` | Menunjukkan cara melaporkan dukungan fitur secara eksplisit | Data ilustratif, bukan hasil pengujian runtime |

## Jalankan dari root repository

```sh
python pusingcuk_new.py examples/self_hosting/lexer.cuk
python pusingcuk_new.py examples/self_hosting/parser.cuk
python pusingcuk_new.py examples/self_hosting/evaluator.cuk
python pusingcuk_new.py examples/self_hosting/interpreter.cuk
python pusingcuk_new.py examples/self_hosting/codegen.cuk
python pusingcuk_new.py examples/self_hosting/runtime_contract.cuk
```

Tes otomatis di `tests/test_self_hosting_examples.py` memeriksa exit code dan output yang diharapkan. Lulus pada interpreter referensi hanya membuktikan prototipe berjalan di target itu; tidak berarti target native/browser mendukungnya.

## Jalur menuju self-hosting sungguhan

1. Stabilkan kontrak bahasa dan suite konformansi lintas runtime.
2. Tambahkan operasi string/karakter dan struktur data yang dibutuhkan lexer source penuh.
3. Bangun lexer dan parser `.cuk` yang membaca source bahasa `.cuk` itu sendiri.
4. Definisikan AST/IR versi stabil yang bisa dipakai interpreter dan compiler backend.
5. Implementasikan evaluator/VM dan code generator secara bertahap, masing-masing dengan fixture konformansi.
6. Buktikan bootstrap: compiler `.cuk` yang dibangun oleh toolchain lama mampu membangun ulang versi dirinya sendiri dengan hasil yang dapat dibandingkan.

Jangan menyebut PusingCuk self-hosted sebelum tahap bootstrap dapat diulang dan diverifikasi di CI.