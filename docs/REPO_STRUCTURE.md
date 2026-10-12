# Peta Struktur Repository Pusingcuk

Dokumen ini menjelaskan fungsi direktori dan file utama agar kontributor baru dapat menemukan kode dengan cepat. Pusingcuk masih eksperimental; keberadaan file/backend tidak berarti seluruh fitur bahasa sudah didukung atau aman untuk kode tak tepercaya.

## Mulai dari sini

- `README.md`: gambaran proyek, status fitur, dan jalur menjalankan program.
- `docs/PEMULA.md`: tutorial langkah demi langkah untuk pemula.
- `SPEC.md`: sintaks dan perilaku bahasa yang dimaksudkan.
- `docs/COMPATIBILITY.md`: batas kompatibilitas antar-runtime.
- `docs/COMPILER_TARGETS.md`: target compiler dan cara menggunakannya.
- `CONTRIBUTING.md`: cara berkontribusi.
- `SECURITY.md`: pelaporan kerentanan dan batas keamanan.
- Status fitur harus diverifikasi pada dokumen target terkait; jangan menganggap roadmap atau nama folder sebagai bukti fitur sudah selesai.

## Implementasi inti bahasa

| Lokasi | Fungsi |
|---|---|
| `lexer.py` | Memecah kode sumber menjadi token dan mengenali kata kunci/alias. |
| `parser.py` | Mengubah token menjadi struktur sintaks. |
| `ast_nodes.py` | Definisi node AST yang digunakan pipeline modular. |
| `evaluator.py` | Mengevaluasi AST dan menjalankan operasi bahasa. |
| `interpreter.py` | Implementasi interpreter historis/modular; periksa jalur CLI yang digunakan sebelum mengubahnya. |
| `pusingcuk_new.py` | Entry point pipeline interpreter modular yang didokumentasikan. |
| `terminal.py` | Terminal interaktif untuk belajar dan menjalankan program. |
| `compiler_ir.py` | Representasi intermediate yang digunakan pipeline compiler tertentu. |
| `compiler/` | CLI compiler, IR, sistem tipe, bytecode/VM, dan backend C, JavaScript, serta Python. |
| `src/backends/` | Backend PVM terpisah, termasuk JavaScript dan Python. Periksa `docs/PVM_SPEC.md`; ekspresi memakai parser terbatas dan opcode jaringan ditolak, tetapi opcode file masih dapat mengakses file yang tersedia bagi proses. |
| `src/c-core/` | Implementasi runtime/inti native C. |
| `native/` | Build dan kode runtime native C. |
| `Makefile` | Target build, test, dan perintah pengembangan. |

## Tes dan kualitas

- `tests/test_*.py`: tes unit/integrasi lexer, parser, interpreter, compiler, VM, dan tooling.
- `tests/conformance/`: program fixture dan manifest perilaku yang dibandingkan antar-jalur eksekusi.
- `tests/native/`: fixture khusus runtime native, termasuk input batas dan kondisi error.
- `tests/*.cuk`: tes program bahasa yang dipakai skrip tes.
- `tests/test_all.sh`: runner tes shell.
- `.github/workflows/tests.yml`: pemeriksaan otomatis CI.
- `.github/workflows/pages.yml`: alur publikasi Pages.
- `.github/dependabot.yml`: pembaruan dependensi otomatis.

Saat mengubah perilaku bahasa, tambahkan atau perbarui fixture konformansi bila sesuai, lalu jalankan tes yang relevan. Jangan menganggap lulus satu backend berarti semua runtime setara.

## Dokumentasi berdasarkan fungsi

- **Belajar bahasa:** `docs/PEMULA.md`, `docs/GAYA_BAHASA.md`, `docs/KOSAKATA_GENZ.md`, `SPEC.md`.
- **Semantik dan kompatibilitas:** `docs/SEMANTIC_CONTRACT.md`, `docs/COMPATIBILITY.md`, `docs/CONFORMANCE_FIXTURES.md`.
- **Compiler dan target:** `docs/COMPILER_TARGETS.md`, `docs/COMPILER_INTEROP.md`, `docs/IR_V1.md`, `docs/C_BACKEND.md`, `docs/JS_BACKEND.md`, `docs/BYTECODE_VM.md`, `docs/PVM_SPEC.md`, `docs/compiler-type-system-and-stdlib.md`.
- **Native dan Termux:** `docs/NATIVE_RUNTIME.md`, `docs/NATIVE_TERMUX.md`, `docs/NATIVE_PARITY_AUDIT.md`, `docs/NATIVE_AUDIT_2026-10-11.md`, `docs/NATIVE_SECURE_ECOSYSTEM_ROADMAP.md`.
- **Aplikasi dan alat:** `docs/ANDROID_STUDIO.md`, `docs/WEB_WORKBENCH.md`, `docs/TERMUX_DASHBOARD.md`, `docs/TOOLING.md`.
- **Rencana lintas-repo/modul:** `docs/THREE_REPO_COMPILER_ROADMAP.md`, `docs/MODULE_SYSTEM.md`.

## Contoh, pustaka, aplikasi, dan situs

- `examples/`: contoh program untuk dipelajari dan dicoba.
- `library/`: contoh/pustaka Pusingcuk dan kosakata; `library/README.md` menjelaskan isi pustaka.
- `archive/legacy/`: kode/program lama untuk referensi historis, bukan entry point yang didukung. Jangan hapus otomatis; gunakan arsip ini untuk melacak perubahan kompatibilitas.
- `android-studio/`: proyek aplikasi Android Studio.
- `tools/web_workbench.py`: workbench web lokal yang menghubungkan editor dengan runtime native.
- `tools/termux_dashboard.sh`: dashboard/shortcut untuk alur kerja Termux.
- `site/` dan `web/`: aset antarmuka web dan contoh situs. Periksa konfigurasi publikasi sebelum menghapus atau memindahkan file.
- `scripts/`: skrip setup, build, atau pengembangan.
- `halo.pusingcuk`: contoh program di root.

## Status kemampuan lintas bahasa dan integrasi

Tujuan jangka panjang Pusingcuk adalah menjadi bahasa yang mudah dipelajari namun dapat berinteroperasi dengan ekosistem lain. **Tujuan bukan berarti fitur sudah tersedia.** Berdasarkan implementasi dan dokumentasi saat ini:

| Area | Status yang aman untuk diklaim |
|---|---|
| Sintaks ramah pemula/Indonesia | Sudah ada, dengan lexer/parser/interpreter dan panduan pemula; pengalaman internasional masih perlu dokumentasi/terjemahan yang konsisten. |
| Compiler Python/JavaScript/C dan bytecode VM | Backend/target eksperimental tersedia untuk subset bahasa; kompatibilitas penuh belum tercapai. |
| Frontend/browser | Ada halaman web/workbench dan target HTML eksperimental; bukan bundler frontend lengkap. |
| Backend/server dan API | Infrastruktur/alat di repositori perlu ditinjau per komponen; jangan mengklaim API framework produksi atau server aman tanpa tes dan dokumentasi khusus. |
| API key dan rahasia | Perlakukan sebagai konfigurasi eksternal; jangan menanamkan key di kode, contoh publik, frontend/browser, atau commit. Gunakan environment/secret manager pada sistem yang menjalankan aplikasi. |
| Database | Belum ada dasar untuk mengklaim konektor database standar yang lengkap hanya dari struktur repo. Perlu driver, kontrak koneksi, pengelolaan kredensial, migrasi, dan tes. |
| WebAssembly (WASM) | Belum ada backend WASM yang dinyatakan tersedia dalam dokumentasi target saat ini. |
| Blockchain | Belum ada dukungan blockchain produksi yang terverifikasi hanya dari keberadaan nama/file lokal. Perlu API/SDK, penandatanganan transaksi aman, pengujian jaringan, dan audit. |
| Sandbox keamanan | Belum tersedia sebagai jaminan umum. Backend PVM menolak opcode jaringan dan memakai parser ekspresi terbatas, tetapi operasi file belum dikurung oleh sandbox OS. Jangan menjalankan bytecode tak tepercaya; lihat `SECURITY.md` dan `docs/PVM_SPEC.md`. |

Untuk setiap integrasi baru, dokumentasikan statusnya sebagai **direncanakan**, **prototipe**, **eksperimental**, atau **stabil**, beserta platform, contoh kerja, tes, dan batas keamanan. Hindari mengiklankan target masa depan sebagai fitur selesai.

## File lokal yang tidak boleh dibersihkan sembarangan

Folder seperti `__pycache__/` dan hasil build seperti APK/binary dapat dibuat ulang dan sudah dicakup oleh `.gitignore`. Namun file seperti `db.json`, `db.txt`, `blockchain.log`, `kavling.json`, atau program bernama khusus mungkin berisi data/eksperimen lokal. Jangan hapus hanya berdasarkan nama; periksa `git status --short` dan cadangkan data terlebih dahulu.

Pada snapshot branch `main` yang diperiksa saat dokumen ini dibuat, file-file data lokal tersebut tidak tercatat sebagai file tracked. Jika ada di perangkat, perlakukan sebagai file lokal sampai status Git membuktikan sebaliknya.
