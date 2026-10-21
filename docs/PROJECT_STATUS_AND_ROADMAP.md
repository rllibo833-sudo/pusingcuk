# Status dan roadmap kanonis PusingCuk

Dokumen ini adalah **satu-satunya roadmap aktif**. README menjelaskan proyek; SPEC mendefinisikan bahasa; kontrak mesin dan manifest mendefinisikan dukungan; dokumen audit bertanggal adalah catatan historis, bukan status terbaru.

**Status rilis: experimental / development.** Jangan mengubah README atau deskripsi repositori menjadi stable sebelum acceptance criteria rilis pada Fase 3 lulus di commit yang sama.

## Sumber kebenaran

| Pertanyaan | Sumber kanonis |
|---|---|
| Apa semantik dan sintaks bahasa? | [SPEC.md](../SPEC.md), [kontrak semantik](SEMANTIC_CONTRACT.md) |
| Built-in apa yang tersedia dan tipe/arity-nya? | [Kontrak built-in](../library/builtin_contract.json) |
| Fixture apa yang wajib diuji? | [Manifest konformansi](../tests/conformance/manifest.json) |
| Hasil fixture dan status target? | [Matriks kompatibilitas](COMPATIBILITY.md), baseline di `tests/conformance/baseline_summary.json`, serta artefak CI untuk commit yang sama |
| Bagaimana cara kerja compiler dan AI? | [Compiler targets](COMPILER_TARGETS.md), [AI readiness](AI_ENGINE_READINESS.md) |
| Roadmap apa yang aktif? | Dokumen ini saja |

Jangan menyalin tabel jumlah fixture ke banyak dokumen. Ringkasan yang dibuat generator harus tetap berada di marker generatornya; angka manual yang bertentangan tidak boleh ditambahkan.

## Status yang sudah dibuktikan

Run core terbaru yang telah selesai dan diverifikasi adalah [PusingCuk core #39533938497](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39533938497), sukses pada commit `c498bd9d82fbf9ef82ae2d95e92d511bb009f9a3`. Pada commit tersebut, kedua job Python (3.11 dan 3.12) serta native GCC dan Clang lulus; Python menjalankan 565 tes dan konformansi reference/native menghasilkan 158 PASS, 0 FAIL, 0 UNSUPPORTED (79 fixture pada dua runtime).

Baseline matriks multi-target yang tersimpan menyatakan reference, native C, JavaScript, Python transpiler, dan VM lulus 79/79, sedangkan HTML compiler masih unsupported untuk seluruh fixture. Baseline tersimpan dan run historis bukan pengganti run matriks pada HEAD saat ini; klaim untuk JS, Python transpiler, VM, atau HTML harus tetap menyebut sumber serta commit yang benar-benar diuji. CI hijau juga hanya membuktikan job yang berjalan, bukan seluruh fitur bahasa atau kesiapan produksi.

## Fase menuju v1.0

### Fase 1 — Kontrak inti dan runtime native
- [x] Implementasikan JSON parse/serialize, HTML escaping, dan CSV quoting pada native C; kontraknya tercakup dalam suite native/reference aktif.
- [x] Tambahkan tes unit untuk nilai valid/invalid, nested list/dictionary, escaping, arity, dan batas ukuran.
- [x] Manifest kanonis saat ini mewajibkan native/reference untuk seluruh 79 fixture aktif; jangan mengubah status tanpa bukti.
- [x] Core CI terbaru menjalankan differential test reference/native pada commit yang sama: 158 PASS, 0 FAIL, 0 UNSUPPORTED. Matriks seluruh backend tetap harus diverifikasi pada commit rilis.
- [x] Jalur evolusi/data center tetap dry-run/review-only; tidak melakukan auto-commit atau auto-push ke `main`.

### Fase 2 — Browser dan perluasan target
- [ ] Playground GitHub Pages menjalankan subset .cuk yang didukung melalui backend JS/browser yang nyata, bukan sekadar menampilkan kode atau mengandalkan terminal Python eksternal tanpa diagnostik.
- [ ] Browser tests membuktikan output, error, dan contoh yang ditampilkan; kegagalan runtime tidak boleh tampil sebagai traceback mentah.
- [ ] Tentukan kontrak lintas target dari fixture bersama sebelum menambah backend C++, Kotlin/JVM, atau target lain.
- [ ] Target yang belum menjalankan fixture dilaporkan `unsupported/not yet verified`, bukan hijau secara implisit.

### Fase 3 — Release v1.0
- [ ] Bekukan spesifikasi dan kontrak semantik yang didukung.
- [ ] Manifest konformansi menjadi acceptance suite wajib dan dapat direproduksi.
- [ ] Setiap target yang diklaim stabil lulus suite wajib pada commit rilis yang sama; pengecualian didokumentasikan per fitur.
- [ ] Dokumentasi pengguna, quickstart, built-ins, compiler targets, website, package metadata, dan release notes konsisten.
- [ ] CI wajib hijau untuk semua workflow rilis yang relevan; tidak ada run wajib yang masih berjalan atau dilewati.

## Prioritas aktif — frontend mandiri dan bootstrap

Komponen ekosistem yang sudah ada tidak boleh dihitung ulang sebagai pekerjaan baru. Fokus berikutnya adalah menghubungkan prototipe self-hosting dengan toolchain yang ada:

1. Perluas `examples/self_hosting/source_lexer.cuk` dari parser ekspresi ke grammar program secara bertahap. Cakupan saat ini mencakup deklarasi, assignment, alias output, ekspresi integer, serta literal string dan escape dasar; kontrol alur, fungsi, angka pecahan, dan diagnostik lengkap masih terbuka.
2. Jaga pemetaan AST self-hosted ke IR v1 yang sudah ada dan gunakan backend yang sama. Saat ini `compiler/self_hosted_frontend.py` masih menjadi adapter yang menjalankan program `.cuk`, menerima AST JSON, membentuk envelope IR v1, dan memvalidasinya; ini belum frontend mandiri tanpa Python.
3. Perluas parity test antara frontend self-hosted dan referensi Python, termasuk literal string ber-escape, lalu jalankan CI pada commit yang sama. Jangan mengklaim kesetaraan di luar fixture yang benar-benar lulus.
4. Implementasikan compiler dalam .cuk secara bertahap dan tambahkan job bootstrap: toolchain lama membangun compiler .cuk, lalu compiler baru membangun ulang dirinya; hasil build dan suite tes harus cocok.
5. Setelah pipeline tersebut teruji, migrasikan bagian Reality Engine, formatter/test runner, dan tooling AI ke jalur .cuk. Ollama tetap opsional dan tidak boleh menjadi syarat tes inti.

**Batas saat ini:** dukungan unary minus dan modulo pada prototipe ekspresi merupakan kemajuan lokal yang terukur, bukan bukti bahwa frontend penuh atau bootstrap sudah selesai. Python masih menjadi implementasi referensi dan penggerak compiler CLI saat ini.

## Aturan perubahan

1. Satu perubahan bahasa harus menyentuh implementasi, kontrak, fixture, dokumentasi relevan, dan generator yang terkait dalam satu perubahan terulas.
2. Jangan ubah baseline agar CI hijau; baseline hanya diperbarui dari hasil runner yang sukses dan ditinjau.
3. Jangan pakai penggantian teks global, `|| true` untuk tes wajib, atau loop otomatis yang commit/push ke `main`.
4. Jangan menambah dokumen status duplikat. Audit bertanggal tetap sebagai sejarah; update dokumen ini dan sumber kanonis.
5. CI hijau membuktikan job yang benar-benar berjalan pada commit tersebut saja—bukan semua fitur atau target.


### Batas operasional lokal yang wajib dipertahankan

Perangkat Android pengguna dengan Termux adalah adapter dan data center lokal bagi PusingCuk AI serta Cuk Reality Engine. Semua pekerjaan lanjutan harus mempertahankan konfigurasi matrix, endpoint loopback, dan data lokal yang sudah diperbaiki; tidak boleh melakukan reset, migrasi destruktif, atau mengubah alamat/provider diam-diam. Ollama bersifat opsional untuk core CI, tidak ada fallback cloud diam-diam, dan tooling evolusi tetap menghasilkan proposal untuk review—bukan auto-commit/push.


### Self-hosted codegen increment (2026-10-21)

`examples/self_hosting/codegen.cuk` recursively serializes a limited integer/binary AST into a nested C expression and rejects unsupported operators. Runtime tests cover nested expressions and rejection. This is an isolated generator slice, not yet cross-language compilation: it still consumes a hand-built AST and is not connected to the canonical parser, IR v1, bytecode VM, or backend registry.


### CI correction for nested codegen (2026-10-21)

The first core run after the nested C-expression generator failed because `tests/test_self_hosting_examples.py` still expected the old flat expression (`7 + 35`). The fixture now expects the nested output and unsupported-operator signal. This is a test expectation correction, not evidence of cross-language parity or self-hosting; wait for the corrected commit's complete CI result.


### Target Rust tahap awal (2026-10-21)

CLI kini menerima `--target rust`, yang menerjemahkan IR v1 kanonis menjadi source Rust mandiri untuk subset numerik: deklarasi/assignment variabel, output, unary minus, dan operasi `+ - * / // %`. Konstruksi di luar subset ditolak secara eksplisit. Target ini menambah satu backend bahasa nyata, tetapi tidak dihitung sebagai parity penuh atau sebagai bukti target 10; hasil eksekusi harus diverifikasi dengan `rustc` bila tersedia.


### Frontend self-hosted terhubung ke IR v1 (2026-10-21)

`compiler/self_hosted_frontend.py` mengeksekusi lexer/parser dalam `examples/self_hosting/source_lexer.cuk`, mengubah AST subset tersebut menjadi envelope IR v1 yang divalidasi, dan mengirim IR yang sama ke backend existing melalui opsi `--frontend selfhosted`. Tes memeriksa kesamaan AST dengan frontend kanonis dan penolakan sintaks malformed. Cakupan masih terbatas pada deklarasi, assignment, output, serta ekspresi integer; ini bukan pengganti parser kanonis penuh. **Bootstrap berulang belum terbukti** karena implementasi compiler lengkap belum ditulis dalam `.cuk`.
