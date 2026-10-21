# Kompatibilitas Pusingcuk

Dokumen ini menetapkan batas kompatibilitas yang boleh diklaim, bukan janji bahwa semua sasaran sudah tercapai. PusingCuk masih eksperimental: fixture aktif menunjukkan kesetaraan pada suite terukur untuk reference, native C, JavaScript, Python transpiler, dan VM. **Target HTML compiler** masih belum menjalankan matriks fixture lintas-runtime; ini berbeda dari **Browser Playground**, yang memiliki interpreter AST JavaScript terpisah untuk subset .cuk terbatas dan suite integrasinya sendiri (`node tests/test_browser_runtime.js` dan `node tests/test_browser_playground.js`). Playground bukan bukti paritas penuh atau pengganti fixture HTML compiler.

**Versi bahasa kanonis:** `0.6-dev`. Versi paket pengembangan `0.8.0.dev0` adalah versi distribusi, bukan versi bahasa. Kontrak memuat 25 built-in. Pada matriks terbaru berisi 79 fixture, reference, native C, JavaScript, Python transpiler, dan VM lulus 79/79; target HTML compiler belum menjalankan fixture. Browser Playground diuji terpisah pada contoh galeri, kontrol editor, dan subset konformansi diferensial terhadap interpreter referensi; daftar kasus ada di `tests/conformance/browser_manifest.json`. Status per built-in tetap ditentukan oleh `library/builtin_contract.json`.

**Baseline yang dipelihara:** Python modular adalah referensi. Pada run [39465123558](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39465123558), reference, native C, JavaScript, Python transpiler, dan VM lulus 79/79; reference/native mencatat 79 perbandingan, 0 mismatch, 0 incomplete, dan 0 unsupported. Ini bukti untuk fixture yang diukur, bukan bukti kesetaraan semua program atau semua sistem operasi. Target HTML compiler tetap unsupported pada matriks konformansi umum. Browser Playground tersedia sebagai target terpisah dengan subset dan batas eksplisit; lihat [Browser Playground Runtime](BROWSER_PLAYGROUND.md).

## Sasaran desain

Pusingcuk harus mudah dimulai oleh pemula, tetap dapat dipakai untuk proyek serius, dan tidak mengunci pengguna pada satu sistem operasi atau satu implementasi runtime.

1. **Sumber yang portabel.** Berkas program menggunakan UTF-8 dan ekstensi kanonis `.cuk`, seperti `.py` untuk Python. Ekstensi `.pusingcuk` tetap diterima sebagai ekstensi kompatibilitas. Program yang hanya memakai fitur bahasa inti dan API standar yang terdokumentasi seharusnya tidak bergantung pada lokasi instalasi atau OS tertentu.
2. **Kontrak bahasa yang stabil.** Sintaks, nilai, operator, aturan scope, perilaku error, dan semantik built-in ditentukan oleh spesifikasi dan tes konformansi, bukan oleh kebetulan implementasi.
3. **Runtime yang dapat dipilih.** Interpreter referensi Python membantu pengembangan; runtime native C memungkinkan eksekusi tanpa Python setelah dibangun. Fitur hanya portabel lintas runtime jika kedua implementasi telah lulus tes yang sama.
4. **CLI yang konsisten.** Program sukses mengembalikan `0`, kesalahan runtime `1`, kesalahan sintaks `2`, dan sumber tidak ditemukan `3`. Pesan error ada di stderr; kelas kesalahan dan nomor baris merupakan kontrak konformansi, sedangkan rincian kalimat boleh berbeda.
5. **Dependensi eksplisit.** File, jaringan, database, lingkungan proses, dan kemampuan OS harus disediakan lewat API yang terdokumentasi. Jangan mengandalkan akses implisit atau efek samping khusus OS.
6. **Kompatibilitas ke depan.** Perubahan yang mematahkan sintaks atau semantik perlu dicatat dalam changelog dan versi; alias lama tidak boleh dihapus tanpa kebijakan deprekasi yang jelas.

## Semantik tipe dan data

Type model di `compiler/typesystem.py` kini dapat merepresentasikan tipe opsional, `Hasil<Sukses, Gagal>`, struktur bernama, dan enum, termasuk aturan assignability dasar. Ini **belum berarti sintaks sumber `T?`, `mungkin`, `coba/tangkap`, `tipe`, atau deklarasi enum sudah didukung**: model ini belum terhubung ke parser, pemeriksaan semantik, IR, interpreter, C, JavaScript, atau VM. Fitur tersebut tidak boleh diklaim sebagai kemampuan bahasa yang sudah dapat digunakan sampai sintaks, nilai runtime, dan fixture lintas target tersedia.

| Fitur bahasa | Interpreter Python | C native | JavaScript | VM | Status kontrak |
|---|---|---|---|---|---|
| Nilai opsional sebagai sintaks bahasa | [X] belum ada kontrak | [X] belum ada kontrak | [X] belum ada kontrak | [X] belum ada kontrak | Model tipe saja |
| Hasil sukses/gagal bertipe | [X] belum ada kontrak | [X] belum ada kontrak | [X] belum ada kontrak | [X] belum ada kontrak | Model tipe saja |
| Struktur bernama dan enum di kode sumber | [X] belum ada kontrak | [X] belum ada kontrak | [X] belum ada kontrak | [X] belum ada kontrak | Model tipe saja |
| `pakai ... sebagai` + `ekspor fungsi` | [X] bukan jalur interpreter | [X] belum diintegrasikan | [!] melalui compiler multi-target, bukan semantik runtime langsung | [!] bergantung pada pipeline compiler | Ekspansi modul compiler awal |
| `angkut("file.cuk")` | [!] modul dinamis pada evaluator referensi | [X] belum setara | [X] tidak otomatis tersedia | [X] tidak otomatis tersedia | API modul belum lintas-target |
| Paket eksternal berversi | [X] belum ada package manager | [X] belum ada package manager | [X] belum ada package manager | [X] belum ada package manager | Belum tersedia |

Status di atas sengaja memisahkan fondasi internal dari sintaks yang dapat digunakan pengguna. Built-in dan namespace harus mengikuti status per-target dalam `library/builtin_contract.json`; fixture hanya membuktikan kasus yang benar-benar dijalankan, bukan seluruh kombinasi input.

## Status kompatibilitas saat ini

**Historical evidence (20 October 2026):** run [39426734065](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39426734065) recorded the earlier 77-fixture baseline before the native format built-ins were completed. The current measured result is recorded above; older score records remain historical snapshots. Compile-time rejection is accepted only for a fixture that expects failure and whose pinned source line matches. Runtime diagnostics and source-line matching remain part of the conformance contract.

The host adapters under `library/adapters/` remain Python host-side primitives. Database, server HTTP, DOM, Web3, and stable FFI are still **not** first-class `.cuk` APIs available across reference and native C. The intended device workflow is local Android/Termux with Ollama on loopback; device-specific support requires `bash scripts/test-termux-device.sh` on the actual device.


| Contoh Reality Engine | Status |
|---|---|
| Python reference | The current 77-fixture manifest has no Reality Engine-specific fixture. Dedicated rule-boundary coverage is not established by the general baseline alone. |
| JavaScript target | `examples/reality_engine.cuk` is not present on `main`; the earlier source-level parity claim is unverified until the source and test are checked in and CI passes. |
| Native C | No checked-in Reality Engine source is available on `main` to verify backend parity. Do not infer Reality Engine compatibility from the general fixture score. |


| Area | Status sekarang | Makna praktis |
|---|---|---|
| Linux dengan compiler C11 | Jalur native diuji di CI Ubuntu GCC/Clang | Bukan bukti otomatis untuk semua distro |
| Android melalui Termux | Ada skrip instalasi dan panduan | Pengujian perangkat fisik masih perlu dilakukan |
| Windows / macOS | Belum menjadi target native yang terverifikasi | Jangan menjanjikan kompatibilitas native sebelum ada CI dan tes platform |
| Interpreter Python | Unit test berjalan pada Python 3.11 dan 3.12 di CI; 25 built-in terkontrak tersedia di interpreter referensi | Ini jalur referensi pengembangan, bukan runtime mandiri |
| Runtime native C | Fixture mencakup 25 nama built-in, konkatenasi list, dan pembacaan indeks rentang pada subset yang diuji; konversi scalar tetap dibatasi sesuai [panduan runtime native](NATIVE_RUNTIME.md) | `teks()` tidak memformat koleksi; list dibatasi 256 item; runtime bukan sandbox dan modul/file/jaringan belum tersedia |
| Modul dan paket | Belum tersedia penuh pada native | Impor modul bukan kontrak portabel saat ini |
| UTF-8 | Berkas sumber dibaca sebagai teks UTF-8 pada CLI Python; native menangani sebagian operasi UTF-8 | Validasi UTF-8 penuh, normalisasi, dan semantik Unicode lintas runtime belum dijamin |
| File, jaringan, database | Belum ada pustaka standar lintas runtime yang lengkap | Gunakan hanya API yang secara eksplisit tersedia pada runtime target |
| Keamanan kode tak tepercaya | Tidak ada sandbox yang dijamin | Jangan menjalankan program tak tepercaya dengan hak akses penting |
| Operasi file PVM | JavaScript: dinonaktifkan; Python: ditolak secara default, kapabilitas eksplisit dan POSIX descriptor-relative no-follow bila tersedia | Tetap bukan sandbox OS; tidak ada dukungan untuk program/bytecode tak tepercaya |

## Compiler dan interoperabilitas

Pusingcuk dirancang agar dapat memiliki beberapa backend tanpa mengubah semantik bahasa. Lihat [arsitektur compiler dan interoperabilitas](COMPILER_INTEROP.md) untuk pipeline front-end → AST → analisis semantik → IR berversi → backend, serta batas rancangan ABI/FFI. Lihat [kontrak fixture konformansi](CONFORMANCE_FIXTURES.md) untuk format tes yang akan dipakai lintas runtime.

IR v1 tersedia sebagai format AST-preserving yang tervalidasi, tetapi bukan ABI stabil. CLI compiler memiliki target eksperimental JavaScript, Python, HTML, JSON IR, dan VM JSON; cakupan tiap target berbeda dan belum menjamin kesetaraan penuh. Backend C terpisah hanya mendukung subset integer yang terdokumentasi. Backend WebAssembly dan ABI/FFI stabil **belum tersedia**. Backend baru hanya dapat diklaim kompatibel setelah lulus fixture yang sama untuk fitur yang dinyatakan didukung.

## Tingkat kompatibilitas fitur

- **Inti teruji lintas runtime:** boleh disebut portabel hanya jika fixture yang sama lulus pada interpreter referensi dan runtime native.
- **Native teruji:** boleh digunakan pada native sesuai matriks, tetapi belum tentu tersedia pada interpreter referensi dengan semantik identik.
- **Referensi saja:** tersedia pada interpreter modular, tetapi belum menjadi bagian dari runtime native.
- **Eksperimental:** perilaku dapat berubah; jangan menjadikannya kontrak paket publik tanpa mengunci versi.

Status harus ditulis per fitur. Katalog built-in yang lengkap tersedia di [docs/language/BUILTINS.md](language/BUILTINS.md), disinkronkan dengan `library/builtin_contract.json`, dan diperiksa tes. Label umum seperti “kompatibel dengan Python”, “kompatibel dengan JavaScript”, atau “berjalan di semua OS” tidak boleh digunakan tanpa definisi dan tes konkret.

## Sasaran matriks platform

Sebelum menyatakan sebuah platform didukung, proyek perlu menjalankan tes yang sama di CI untuk platform itu dan mendokumentasikan versi compiler/runtime yang dipakai.

| Platform | Sasaran verifikasi |
|---|---|
| Linux x86-64 | GCC dan Clang, tes CLI dan seluruh fixture native |
| Android / Termux | Clang + Make, skrip instalasi, contoh program dan fixture native di perangkat nyata |
| macOS | Build C11 dan seluruh fixture native di CI |
| Windows | Pilih toolchain yang didukung, verifikasi jalur file, encoding, exit code, dan fixture; jangan menganggap POSIX shell tersedia |

Matriks di atas adalah urutan target pengujian, bukan pernyataan bahwa semua platform tersebut sudah didukung.

## Kontrak tes konformansi

Setiap perubahan sintaks atau semantik sebaiknya menambahkan kasus ke suite konformansi dengan:
- sumber program yang sama untuk tiap runtime;
- keluaran stdout yang diharapkan;
- kode keluar yang diharapkan;
- kelas/pesan error yang cukup stabil untuk diperiksa;
- tes batas dan nilai tidak valid;
- versi spesifikasi atau fitur yang diuji.

Tes lintas runtime harus membandingkan hasil yang terlihat pengguna, bukan detail internal implementasi. Jika suatu fitur belum didukung pada satu runtime, tandai sebagai belum didukung; jangan menyamarkan perbedaan sebagai kelulusan tes.

## Jalur untuk pemula dan pengguna mahir

- **Pemula:** mulai dari [Panduan Pemula](PEMULA.md), jalankan contoh kecil, lalu ubah satu hal setiap kali.
- **Pengembang aplikasi:** baca [matriks runtime](NATIVE_RUNTIME.md), gunakan fungsi, koleksi, validasi input, dan hanya API yang sudah terdokumentasi.
- **Kontributor/runtime engineer:** baca [panduan kontribusi](../CONTRIBUTING.md), tambahkan tes konformansi dan kasus error, lalu verifikasi kedua jalur runtime yang tersentuh.

Kompatibilitas yang baik berarti program gagal dengan jelas saat fitur tidak tersedia, bukan diam-diam berperilaku berbeda.


## Python standard-library import subset

The experimental Python importer uses explicit allow-lists, not arbitrary host imports. The currently tested mappings are:

| Python API | Pusingcuk builtin | Targets with implementation | Important limits |
|---|---|---|---|
| `math.sqrt/floor/ceil/fabs/pow/sin/cos`, `math.pi/e` | `akar/bawah/atas/mutlak/pangkat/sinus/kosinus` and numeric constants | JS, Python, HTML | Only listed names; numeric-domain behavior is validated per helper |
| `statistics.mean` | `rata_rata` | JS, Python, HTML | One non-empty list of finite numbers; not full `statistics` semantics |
| `statistics.median` | `median` | JS, Python, HTML | One non-empty list of finite numbers; not full `statistics` semantics |

The Python importer maps the built-in `sum` to `jumlah`; that mapping targets Pusingcuk reference semantics, while native C has matching fixtures for the same contract. VM support for trig/statistics/summation helpers is not claimed. Unsupported imports such as `statistics.variance`, wildcard imports, and other modules are rejected instead of being silently passed through. HTML uses the JavaScript backend, so its helper implementation and tests share that runtime. See [Python importer limits](IMPORT_PYTHON.md) and [standard-library registry](compiler-type-system-and-stdlib.md).


## Shared builtin contract

The machine-readable source of builtin metadata is [`library/builtin_contract.json`](../library/builtin_contract.json). It defines canonical names, parameters and accepted arity, Python import allow-lists, target helper mappings, and explicit support states. The Python reference registry and JS/Python backend dispatch are derived from it; runtime implementation code remains target-specific.

- `supported`: implemented and covered by tests for that target.
- `unsupported`: explicitly not implemented by that target.
- `not-claimed`: not verified; do not promise compatibility.

The contract is not a package manager and does not imply network access. Database, server, browser, Web3, and blockchain APIs should be separate capability-scoped adapters with local/mock modes for offline development and explicit target support.


The contract records language-level platform capabilities separately from host-side adapter code. `library/adapters/database.py`, `server.py`, and `web3.py` now provide local SQLite, loopback HTTP, and mock/loopback JSON-RPC primitives with focused tests; they are not yet exposed as first-class `.cuk` APIs or claimed compiler targets. Therefore `data.database`, `server.http`, `web.dom`, `web3.blockchain`, and stable FFI remain `planned` in `library/builtin_contract.json`. Existing reference-runtime HTTP built-ins are a separate, explicitly limited capability.

<!-- BEGIN GENERATED CONFORMANCE SUMMARY -->
## Measured conformance snapshot

This table is generated from the supplied machine-readable fixture summary. It is a snapshot, not a live CI result or a claim of complete language compatibility.

| Target | Passed | Failed | Timeout | Unsupported | Unavailable |
|---|---:|---:|---:|---:|---:|
| reference | 79 | 0 | 0 | 0 | 0 |
| native | 79 | 0 | 0 | 0 | 0 |
| javascript | 79 | 0 | 0 | 0 | 0 |
| python_transpiler | 79 | 0 | 0 | 0 | 0 |
| html | 0 | 0 | 0 | 79 | 0 |
| vm | 79 | 0 | 0 | 0 | 0 |

- Fixtures in checked-in baseline summary: **79**
- Native C Python-free score: **100.00%** (79/79; unsupported fixtures remain in the denominator)
<!-- END GENERATED CONFORMANCE SUMMARY -->


## Differential report (verified artifact)

The latest verified fixture matrix is [GitHub Actions run #39465123558](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39465123558), on commit `db67c1f33454ccc2f422381dec4b02df0227f007`. The differential runner reports **79 comparisons, 0 mismatches, 0 incomplete comparisons, and 0 unsupported cases** for reference/native. Reference, native C, JavaScript, Python transpiler, and VM each record 79/79; HTML remains unsupported. This evidence is limited to the active fixture set.

| Target | Passed | Failed | Unsupported | Practical meaning |
|---|---:|---:|---:|---|
| Reference interpreter | 77 | 0 | 0 | Current language behavior baseline |
| Native C | 74 | 0 | 3 | Verified subset; unsupported fixtures are not passes |
| JavaScript | 77 | 0 | 0 | All active fixtures pass; arbitrary programs are not guaranteed |
| Python transpiler | 77 | 0 | 0 | All active fixtures pass; output still requires Python runtime |
| VM / bytecode | 77 | 0 | 0 | All active fixtures pass; VM still depends on Python runtime |
| HTML | 0 | 0 | 77 | No independently executable HTML backend is currently claimed |

These numbers are the checked-in baseline snapshot, not a live status query. Check the linked Actions run and artifacts for commit-specific evidence. A green workflow means its configured regression gate passed; it does not mean unsupported targets or arbitrary programs are covered. The three native-unsupported fixtures remain open work, and HTML has no executable fixture coverage.

## Documentation synchronization rule

For current behavior, use this evidence order:

1. `SPEC.md` and `docs/SEMANTIC_CONTRACT.md` define intended language semantics.
2. The implementation and machine-readable contracts define what is implemented.
3. `tests/conformance/manifest.json` plus `tests/conformance/baseline_summary.json` define the checked-in fixture contract and baseline.
4. The latest successful Actions run and its artifacts provide commit-specific execution evidence.
5. This compatibility document and the generated snapshots summarize those sources; historical audits, commit messages, and older workflow runs are not current feature specifications.

When a technical change alters syntax, semantics, built-ins, diagnostics, target support, or measured fixture totals, update the canonical contract and affected examples/docs in the same change. Do not append another historical report as a substitute for updating the current status. Never update baseline numbers merely to make CI green; regenerate them only from a reviewed matrix artifact.
