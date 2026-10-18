# Audit PusingCuk — Phase 0

> **Snapshot audit:** 2026-10-18  
> **Commit yang diperiksa:** `8150e1adcde123c02daa4921f0903917681df9c0` (`main`)  
> **Tujuan:** baseline berbasis bukti sebelum perubahan kode. Ini bukan sertifikasi keamanan atau klaim bahwa seluruh target setara.

## Ringkasan eksekutif

- Repositori publik MIT, deskripsi GitHub menyebut bahasa eksperimental dengan interpreter Python.
- Kontrak bahasa yang dinyatakan: `0.6-dev`; metadata paket: `0.8.0.dev0`; tahap Alpha.
- Inventaris GitHub tree: **383 file**. Tree tidak terpotong.
- Manifest `tests/conformance/manifest.json`: **77 fixture**; 45 fixture negatif dengan diagnostik yang diharapkan. Profile: 72 `core`, 5 `reference`.
- Semua 77 fixture mewajibkan runtime referensi. Native C diwajibkan pada 74 dan ditandai `unsupported` pada 3.
- CI terbaru yang terlihat pada snapshot ini: [run #1134](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39122459501) **success**: unit tests Python 3.11 dan 3.12, conformance pada Python 3.12, native GCC dan Clang semuanya sukses. Ini bukti run untuk commit tersebut, bukan hasil eksekusi ulang oleh audit lokal.
- Kloning ke sandbox audit gagal karena lingkungan tidak dapat menyelesaikan `github.com`; maka saya tidak mengarang output pengujian lokal atau hitungan pass/fail individual.
- Workflow `main` belum dilindungi: endpoint branch menyatakan `protected: false`, status checks tidak diwajibkan. Owner perlu menerapkan aturan GitHub secara manual.

## 1. Ruang lingkup dan metode

Saya membaca GitHub repository metadata, recursive Git tree, `pyproject.toml`, `README.md`, `SPEC.md`, `docs/COMPATIBILITY.md`, manifest fixture, `tests/test_version_contract.py`, `tools/conformance.py`, workflow CI utama, dan status run Actions. Tidak ada file kode yang diubah pada fase audit. Inventaris lengkap setiap path yang terlihat ada di bagian Appendix; deskripsi path adalah klasifikasi awal, bukan hasil pembacaan mendalam setiap file.

**Batas penting:** GitHub tree memberi nama dan ukuran file, bukan bukti semua fungsi file. Saya tidak dapat menghitung jumlah tes per fungsi atau menguji target browser, HTML, JSON IR, JS, Python transpiler, dan VM secara terpisah hanya dari CI utama saat ini.

## 2. Inventaris tingkat direktori

| Path/area | Jumlah file | Tujuan dan status awal | Bukti/risiko |
|---|---:|---|---|
| `.github/` | 14 | Workflow, issue templates, Dependabot; **aktif** | Periksa tiap workflow untuk cakupan trigger, izin, secrets, dan job yang dapat menulis. |
| Root | 22 | Spesifikasi, interpreter, metadata, tata kelola, contoh utama; **campuran aktif** | File interpreter berada di root; struktur paket belum sepenuhnya di bawah `src/pusingcuk`. |
| `compiler/` | 11 | IR, type system, C/JS/Python backend, bytecode/VM; **eksperimental** | Adanya backend tidak membuktikan paritas. |
| `src/` | 3 | Sumber JS/Python/C di jalur lain; **status integrasi tidak jelas** | Berpotensi membingungkan dengan modul Python root dan `compiler/`; jangan pindahkan sebelum dependency map. |
| `library/` | 26 | Built-ins, kontrak, kosakata, assistant/AI, adapter; **campuran aktif/eksperimental** | Provider AI dan adapter bukan bukti model mandiri atau kemampuan selalu tersedia. |
| `native/` | 2 | Runtime C dan Makefile; **subset teruji** | CI GCC/Clang hijau untuk target yang tercakup; bukan sandbox OS. |
| `tests/` | 172 | Unit tests, native tests, manifest dan fixture, evaluasi AI; **aktif, cakupan beragam** | 77 fixture manifest bukan total seluruh tes; hasil per backend belum diterbitkan otomatis. |
| `tools/` | 12 | Conformance, repair loop, workbench, evaluasi, sandbox helper; **campuran aktif/eksperimental** | Perlu membedakan harness yang dipakai CI dari tool yang hanya diuji sebagian. |
| `docs/` | 57 | Spesifikasi pendukung, audit, roadmap, AI, keamanan, panduan; **campuran terkini/historis** | Beberapa roadmap/audit tanggal lama hidup bersama dokumen status sekarang; perlu penanda status dan tautan evidence. |
| `examples/` | 36 | Contoh bahasa, accounting, AI, native, remote; **status per contoh belum seragam** | Contoh tidak otomatis menjadi bukti kecuali dijalankan dalam test/fixture. |
| `archive/` | 12 | Interpreter/program lama; **historis** | Sudah dipisahkan, tetapi jangan dianggap aktif. |
| `android-studio/` | 6 | Proyek Android/Gradle; **eksperimental** | Workflow build terpisah; tidak termasuk matriks konformansi utama. |
| `site/` | 3, plus `web/index.html` | Halaman statis/workbench; **eksperimental** | Repo metadata menyatakan GitHub Pages belum aktif (`has_pages=false` pada saat audit). |
| `editors/` | 3 | Konfigurasi syntax VS Code; **dukungan editor dasar** | Belum setara dengan language server/compiler diagnostics. |
| `scripts/` | 3 | Build/install/test Android/Termux; **eksperimental/platform-specific** | Skrip bukan bukti tes perangkat fisik. |

## 3. Versi dan sumber kebenaran

| Item | Nilai teramati | Penilaian |
|---|---|---|
| Bahasa | `0.6-dev` | Ditentukan dalam `pyproject.toml`; harus tetap konsisten dengan `SPEC.md`, lexer, kontrak built-in, kosakata. |
| Paket Python | `0.8.0.dev0` | Metadata paket, bukan versi bahasa. |
| Lisensi | MIT | Metadata GitHub dan file LICENSE. |
| Interpreter referensi | `lexer.py`, `parser.py`, `ast_nodes.py`, `evaluator.py`, `pusingcuk_new.py` | Jalur modular yang saat ini menjadi referensi. |
| Entry points | `pusingcuk` → `pusingcuk_new:main`; beberapa entry point AI/studio/repl/build | CLI `run/check/compile/reality` belum terbukti sebagai satu antarmuka terpadu. |
| IR/bytecode | `compiler/ir.py`, `compiler/bytecode.py`, `compiler/vm.py`, dokumen IR/PVM | Dokumen menyebut IR v1 belum ABI stabil; VM eksperimental. |

`SPEC.md` seharusnya tetap menjadi sumber aturan bahasa. `docs/SEMANTIC_CONTRACT.md`, `library/builtin_contract.json`, `library/kosakata.json`, implementasi dan fixture harus menjadi turunan yang saling diperiksa—bukan spesifikasi paralel yang diam-diam bertentangan.

## 4. Baseline fixture dan target

### 4.1 Baseline eksekusi — diukur melalui GitHub Actions

Baseline dijalankan di runner GitHub Actions, commit `730b3a05fd2510b955ffeee2a21866915f60f5c6`, [run #4](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39127180391). Workflow selesai sukses karena semua target terus dijalankan dan kegagalan target dicatat; **status workflow hijau bukan berarti seluruh backend lulus**.

| Target | Fixture lulus | Gagal | Timeout | Tidak didukung | Tidak tersedia |
|---|---:|---:|---:|---:|---:|
| Python reference interpreter | 77 | 0 | 0 | 0 | 0 |
| Native C | 74 | 0 | 0 | 3 | 0 |
| JavaScript via Node | 29 | 48 | 0 | 0 | 0 |
| Python transpiler | 21 | 56 | 0 | 0 | 0 |
| HTML | 0 | 0 | 0 | 77 | 0 |
| VM/bytecode | 28 | 49 | 0 | 0 | 0 |

Jumlah fixture pada manifest: **77**. Status gagal mencakup kegagalan kompilasi dan ketidakcocokan output/exit code/diagnostik; per fixture lihat log mentah. HTML diberi status tidak didukung karena backend HTML yang dapat dieksekusi tidak ditemukan. Tiga fixture native berstatus unsupported menurut cakupan target.

**Artifact bukti:** [run #4 dan artifact `pusingcuk-fixture-baseline-39127180391-1`](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39127180391). Artifact berisi `raw.log` (154.662 byte) dan `summary.json`; tersedia untuk diunduh dari bagian **Artifacts** di halaman run. Retensi artifact 90 hari, jadi unduh/simpan salinan bila perlu bukti jangka panjang.

### 4.2 Python-Free Score awal

**Skor: 96,10% (74/77 fixture).** Ini adalah skor cakupan baseline native C, bukan klaim bahwa seluruh fitur bahasa sudah portabel atau bahwa build toolchain tidak memakai Python.

Metode: `Python-Free Score = (jumlah fixture manifest yang benar-benar lulus pada eksekusi native C) / (total seluruh fixture di manifest) × 100`. Pembagi selalu semua 77 fixture. Tiga fixture yang tidak didukung native tetap berada di pembagi dan tidak dihitung lulus. Hanya native C yang dihitung sebagai Python-free pada baseline ini. VM **tidak** dihitung karena masih mengimpor helper evaluator Python. Python yang dipakai runner untuk mengompilasi/mengorkestrasi pengujian dibedakan dari kebutuhan Python pada saat menjalankan executable native.

### 4.3 Fixture hygiene

Manifest sudah menetapkan ID unik, source path relatif, exit code, stdout, kelas diagnostik, baris sumber untuk fixture negatif, dan status runtime. Runner mengklasifikasikan timeout/harness errors terpisah dari bug program. Kekuatan ini harus dipertahankan. Kekurangannya: manifest hanya mengizinkan `reference` dan `native`; belum ada deklarasi dukungan dan hasil otomatis per JS/Python transpiler/HTML/JSON IR/VM.

## 5. CI failure yang diketahui dan reproduksi

Riwayat Actions menunjukkan [run #1133 pada commit `a8ab68c`](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39099377747) gagal pada `python -m unittest discover -s tests -v` di kedua job Python; langkah `python tools/conformance.py` dilewati. Pada versi saat itu, test `test_package_version_matches_all_package_metadata` memerlukan kalimat eksplisit dalam README yang menyatakan metadata paket. Kegagalan tersebut adalah **ketidakselarasan metadata dokumentasi**, bukan bukti kegagalan semantik bahasa.

Pada snapshot saat ini, README sudah memuat kalimat `Metadata paket pada main adalah 0.8.0.dev0` dan tes memeriksa string tersebut. [Run #1134](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39122459501) sukses pada Python 3.11, Python 3.12, conformance, GCC dan Clang. Jadi kegagalan yang disebut dalam konteks **sudah tidak sedang terjadi pada commit audit ini**; audit tidak akan membuat perubahan kode untuk memperbaikinya lagi. Saya tidak mengklaim telah menjalankan ulang tes lokal karena clone sandbox gagal akibat DNS/network.

## 6. Risiko dan duplikasi yang perlu ditangani

Prioritas berikut adalah temuan audit awal, bukan klaim kerentanan yang sudah dieksploitasi.

1. **Status checks tidak diwajibkan pada main — tinggi untuk tata kelola.** Metadata branch menyatakan `protected=false`. Risiko: perubahan bisa masuk tanpa status CI diwajibkan. Rekomendasi: owner aktifkan aturan branch/ruleset dan wajibkan semua job inti yang relevan.
2. **Matrix compatibility belum menjadi artefak yang dihasilkan — tinggi untuk klaim publik.** Dokumen kompatibilitas ada, tetapi belum menjadi output yang dibuktikan oleh runner lintas semua target. Status fitur bisa tertinggal dari code/fixture.
3. **Baseline CI berbeda dari cakupan target yang diinginkan — tinggi untuk CRE.** Workflow utama menguji reference/native; test backend terpisah bukan pengganti hasil matrix fixture seragam.
4. **Batas keamanan VM perlu tetap eksplisit — tinggi bila kode tak tepercaya.** Repo tidak memiliki sandbox tingkat OS; runner/harness yang membatasi proses bukan bukti isolasi bytecode di VM. Jangan mengiklankan VM sebagai sandbox aman.
5. **Struktur sumber bercampur — sedang.** Modul interpreter root, `compiler/`, `src/`, native C dan target web ada pada struktur berbeda. Relokasi besar harus ditunda sampai dependency map dan uji kompatibilitas ada.
6. **Dokumentasi historis dan status kini bercampur — sedang.** Ada audit tanggal dan roadmap berdampingan dengan overview/status; tanggal tidak otomatis berarti kedaluwarsa, tetapi harus diberi label historical/current.
7. **AI dan provider eksternal — sedang.** `library/assistant.py`, provider lokal/Gemini, knowledge grounding dan repair loop menunjukkan tooling; tidak membuktikan model foundation dilatih sendiri atau loop repair otomatis aman.
8. **Contoh tanpa verifikasi — sedang.** Contoh remote, database, web3, accounting dan AI harus diberi label sesuai fixture. Jangan menyimpulkan kapabilitas hanya dari filename.
9. **Workflow berjumlah banyak — sedang.** 8 workflow di `.github/workflows/` meliputi core, package/release, pages, PVM, Android dan accounting. Audit keamanan workflow mendalam per-file masih perlu; fase ini belum mengeksekusi auditor lokal karena repo tidak dapat di-clone ke sandbox.

## 7. Cakupan dokumentasi stale/roadmap

File yang perlu pemeriksaan silang pada fase berikutnya: `docs/PROJECT_STATUS_AND_ROADMAP.md`, `docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_OVERVIEW_EN.md`, `docs/REPO_STRUCTURE.md`, `docs/COMPATIBILITY.md`, `docs/COMPILER_TARGETS.md`, `docs/IR_V1.md`, `docs/PVM_SPEC.md`, `docs/BYTECODE_VM.md`, `docs/CORE_SANDBOX_RUNNER.md`, `docs/NATIVE_SECURE_ECOSYSTEM_ROADMAP.md`, `docs/AI_ENGINE_READINESS.md`, `docs/AI_ENGINE_MIGRATION_LEDGER.md`, serta audit tanggal di `docs/`. Ini daftar untuk rekonsiliasi; saya tidak menandai semua dokumen tersebut salah tanpa membandingkan klaim satu per satu.

## 8. Rencana bukti untuk fase berikutnya

1. Jadikan fixture manifest sebagai dasar utama; tambahkan schema deklarasi target tanpa mengubah semantik fixture yang ada.
2. Hasilkan matrix dengan status `pass`, `fail`, `unsupported`, `unavailable`, dan `not-measured` yang berbeda.
3. Publikasikan jumlah fixture dan pass/fail dari hasil runner aktual; jangan mengisi target yang belum dijalankan dengan angka nol atau lulus palsu.
4. Hitung Python-Free Score hanya dari eksekusi native/VM yang benar-benar sukses tanpa interpreter Python pada runtime.
5. Tambahkan stale-output check di CI dan pastikan perubahan dokumen audit tidak mengubah perilaku bahasa.
6. Sebelum restrukturisasi atau sandbox, buat peta dependensi dan kontrak tes agar perubahan besar tidak memindahkan/menghapus perilaku secara tidak sengaja.

## 9. Keputusan fase 0

**Status: audit awal berbasis GitHub dan CI selesai; pengukuran lokal penuh belum tersedia.** Tidak ada perubahan kode atau perubahan semantik pada fase ini. Audit tidak mengubah baseline, tidak menghapus konten, dan tidak menyatakan bahwa seluruh target sudah teruji.

### Appendix A — inventaris file per path

Jumlah file dari recursive tree: **383**. Kolom tujuan di bawah adalah klasifikasi berdasarkan path/nama dan bukan pengganti code review isi file satu per satu.

| File | Fungsi/status awal |
|---|---|
| `.github/ISSUE_TEMPLATE/Gen Z or gen Alpha-error.yml` | Template tata kelola atau konfigurasi GitHub. |
| `.github/ISSUE_TEMPLATE/kalkulator.yml` | Template tata kelola atau konfigurasi GitHub. |
| `.github/ISSUE_TEMPLATE/logo.yml` | Template tata kelola atau konfigurasi GitHub. |
| `.github/dependabot.yml` | Template tata kelola atau konfigurasi GitHub. |
| `.github/workflows/accounting-windows.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.github/workflows/android-emulator-smoke.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.github/workflows/android-native.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.github/workflows/android-studio-apk.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.github/workflows/build-test.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.github/workflows/experimental-pvm.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.github/workflows/package.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.github/workflows/pages.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.github/workflows/release.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.github/workflows/tests.yml` | Workflow CI/CD; tinjau trigger, izin token, secrets, actions, dan job. |
| `.gitignore` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `CHANGELOG.md` | Catatan perubahan. |
| `CODE_OF_CONDUCT.md` | Dokumen lisensi/tata kelola/keamanan. |
| `CONTRIBUTING.md` | Dokumen lisensi/tata kelola/keamanan. |
| `LICENSE` | Dokumen lisensi/tata kelola/keamanan. |
| `Makefile` | Target build/test/lint; perlu sinkron dengan CI. |
| `README.md` | Dokumentasi publik utama. |
| `README_EN.md` | Dokumentasi publik utama. |
| `SECURITY.md` | Dokumen lisensi/tata kelola/keamanan. |
| `SPEC.md` | Spesifikasi sumber kebenaran bahasa. |
| `android-studio/app/build.gradle` | Aplikasi Android/Gradle; status eksperimental, build workflow terpisah. |
| `android-studio/app/src/main/AndroidManifest.xml` | Aplikasi Android/Gradle; status eksperimental, build workflow terpisah. |
| `android-studio/app/src/main/java/org/pusingcuk/studio/MainActivity.java` | Aplikasi Android/Gradle; status eksperimental, build workflow terpisah. |
| `android-studio/build.gradle` | Aplikasi Android/Gradle; status eksperimental, build workflow terpisah. |
| `android-studio/gradle.properties` | Aplikasi Android/Gradle; status eksperimental, build workflow terpisah. |
| `android-studio/settings.gradle` | Aplikasi Android/Gradle; status eksperimental, build workflow terpisah. |
| `archive/legacy/README.md` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/interpreters/interpreter_v01.py` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/interpreters/interpreter_v02_backup.py` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/programs/error_test.pusingcuk` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/programs/list_assign_test.pusingcuk` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/programs/list_error_test.pusingcuk` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/programs/list_test.pusingcuk` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/programs/logic_test.pusingcuk` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/programs/loop_test.pusingcuk` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/programs/native_list_test.pusingcuk` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/programs/native_test.pusingcuk` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `archive/legacy/programs/program.pusingcuk` | Konten historis/legacy; jangan dianggap jalur aktif tanpa referensi. |
| `ast_nodes.py` | Jalur interpreter referensi modular / kompatibilitas. |
| `compiler/__init__.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/__main__.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/android_backend.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/bytecode.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/c_backend.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/import_python.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/ir.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/js_backend.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/python_backend.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/typesystem.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler/vm.py` | Implementasi compiler/backend/IR/VM; status per target eksperimental sampai ada fixture. |
| `compiler_ir.py` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `docs/AI_ENGINE_MIGRATION_LEDGER.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/AI_ENGINE_READINESS.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/AI_KNOWLEDGE_GROUNDING.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/AI_LANGUAGE_EVOLUTION_BRIDGE.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/AI_LOCAL_SERVICE.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/ANDROID_DISTRIBUTION.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/ANDROID_STUDIO.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/BYTECODE_VM.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/COMPATIBILITY.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/COMPILER_INTEROP.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/COMPILER_TARGETS.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/CONFORMANCE_FIXTURES.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/CORE_SANDBOX_RUNNER.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/C_BACKEND.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/DICTIONARY.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/EDITOR_SUPPORT.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/GAYA_BAHASA.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/IMPORT_PYTHON.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/INDEPENDENT_REVIEW.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/IR_V1.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/JS_BACKEND.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/KAMUS_PUSINGCUK.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/KOSAKATA_GENZ.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/MODULE_SYSTEM.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/NATIVE_AUDIT_2026-10-11.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/NATIVE_PARITY_AUDIT.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/NATIVE_RUNTIME.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/NATIVE_SECURE_ECOSYSTEM_ROADMAP.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/NATIVE_TERMUX.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/OFFLINE_ADAPTERS.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/PEMULA.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/PROJECT_OVERVIEW.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/PROJECT_OVERVIEW_EN.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/PROJECT_STATUS_AND_ROADMAP.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/PVM_SPEC.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/README.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/REPO_STRUCTURE.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/SECURITY_REVIEW_2026-10-13.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/SEMANTIC_CONTRACT.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/STUDIO_LOCALHOST.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/TERMUX_DASHBOARD.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/THREE_REPO_COMPILER_ROADMAP.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/TOOLING.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/VISION.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/WEB_WORKBENCH.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/ai/DECISION_AUTHORITY_AND_EVIDENCE.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/ai/LOCAL_MODEL_AND_RULE_SAFETY.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/compiler-type-system-and-stdlib.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/development/README.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/examples/CUKACCOUNT_TARGET.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/integrations/CORE_TOOL_CONTRACT.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/knowledge/KAWASAN_MASJID_MASTERPLAN_AND_OPERATING_MODEL.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/language/BUILTINS.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/language/README.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/migration/FOUNDER_OS_CORE_RETIREMENT_MANIFEST.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/security/README.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `docs/termux/README.md` | Dokumentasi; kesegaran dan konsistensi perlu dibandingkan dengan SPEC dan bukti CI. |
| `editors/vscode/language-configuration.json` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `editors/vscode/package.json` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `editors/vscode/syntaxes/pusingcuk.tmLanguage.json` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `evaluator.py` | Jalur interpreter referensi modular / kompatibilitas. |
| `examples/README.md` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/accounting/aturan_ringkasan.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/accounting/rekap_keuangan.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/accounting/report_equation.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/ai/engine_contract.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/android_native_demo.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/compat/README.md` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/compat/halo.pusingcuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/core/anggaran_sufficiency.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/core/anggaran_sufficiency_service.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/core/anggaran_threshold.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/core/anggaran_threshold_service.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/core/priority_triage.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/database.pusingcuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/file_io.pusingcuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/halo_dunia.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/internet.pusingcuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/kalkulator.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/kasir_warung.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/keuangan_sederhana.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/modular.pusingcuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/native/rekap_anggaran.pusingcuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/rekap_anggaran.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/rekap_anggaran.pusingcuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/remote/bot_termux.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/remote/gemini_agent.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/remote/secrets.example.json` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/terminal_bot.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/utils.pusingcuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/viral_bot.pusingcuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/warung.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/warung_bahasa/README.md` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/warung_bahasa/warung_bukti.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/warung_bahasa/warung_evolusi.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/warung_bahasa/warung_kontrak.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `examples/warung_bahasa/warung_prioritas.cuk` | Contoh .cuk/.pusingcuk; keberadaan bukan bukti dapat dijalankan. |
| `halo.cuk` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `interpreter.py` | Jalur interpreter referensi modular / kompatibilitas. |
| `lexer.py` | Jalur interpreter referensi modular / kompatibilitas. |
| `library/README.md` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/accounting_equation_check.cuk` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/adapters/__init__.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/adapters/database.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/adapters/server.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/adapters/web3.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/ai_service.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/ai_tools.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/assistant.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/budget_threshold.cuk` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/builtin_contract.json` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/builtin_contract.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/conditional_logic.pusingcuk` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/gemini_ai_provider.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/journal_balance_check.cuk` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/knowledge_grounding.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/knowledge_index.json` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/kosakata.json` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/local_ai_provider.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/local_memory.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/loops_functions_genz.pusingcuk` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/module_system.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/period_close_plan.cuk` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/report_classification_check.cuk` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/stdlib.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `library/studio_service.py` | Built-in, kontrak kosakata, AI tooling, adapter, atau modul pustaka. |
| `native/Makefile` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `native/pusingcuk.c` | Runtime C native; subset yang benar-benar diuji ditentukan fixture. |
| `parser.py` | Jalur interpreter referensi modular / kompatibilitas. |
| `pusingcuk.spec` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `pusingcuk.xml` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `pusingcuk_new.py` | Jalur interpreter referensi modular / kompatibilitas. |
| `pyproject.toml` | Metadata paket Python, entry points, dan konfigurasi build. |
| `scripts/build-android.sh` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `scripts/install-termux.sh` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `scripts/test-termux-device.sh` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `site/README.md` | UI/playground web; target dan subset harus diverifikasi terpisah. |
| `site/examples/halo.pusingcuk` | UI/playground web; target dan subset harus diverifikasi terpisah. |
| `site/index.html` | UI/playground web; target dan subset harus diverifikasi terpisah. |
| `src/backends/js/compiler.js` | Sumber lintas target/native; struktur belum konsisten dengan paket Python utama. |
| `src/backends/python/compiler.py` | Sumber lintas target/native; struktur belum konsisten dengan paket Python utama. |
| `src/c-core/main.c` | Sumber lintas target/native; struktur belum konsisten dengan paket Python utama. |
| `terminal.py` | File individual; isi dan pemakaiannya belum diverifikasi hanya dari inventaris path. |
| `tests/01_hedeh.cuk` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/02_lah.cuk` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/03_njir.cuk` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/04_mumet.cuk` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/05_file_io.cuk` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/06_gerombolan.cuk` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/conformance/actionable_syntax_error.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/alias_keywords.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/alias_keywords_extended.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/arithmetic_precedence.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtin_arity_error.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtin_domain_error.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtin_native_arity_error.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtin_native_type_error.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtins_js_expanded.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtins_length_shapes.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtins_native.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtins_native_numeric.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtins_reference.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtins_sqrt_power.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/builtins_trig_statistics.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/canonical_extension.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/collection_mutation_function_arg.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/collections_dictionary_overwrite.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/control_nested_range_loops.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/cukaccount_financial_cases.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/dictionary_keys.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/dictionary_missing_key.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/division_by_zero.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/formats_json_html_csv.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/function_scope_leak.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/function_wrong_arity.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/functions.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/json_invalid_returns_false.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/json_null_is_none.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/kasir_warung.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/kosinus_boolean.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/kosinus_wrong_arity.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/list_concatenation.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/list_equality.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/list_index.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/list_index_out_of_range.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/logarithm_domain_error.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/logarithms.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/malformed_expression.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/manifest.json` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/mean_boolean.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/mean_empty.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/mean_unsafe_integer.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/mean_wrong_arity.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/median_boolean.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/median_empty.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/median_unsafe_integer.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/median_wrong_arity.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/numeric_floor_modulo.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/output_arithmetic.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/power_boolean.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/power_negative_fractional.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/power_nonfinite.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/power_wrong_arity.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/power_zero_negative.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/range_index.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/range_index_negative.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/range_index_out_of_range.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/range_loop.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/range_zero_step.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/round_rejects_boolean.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/round_ties_even.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/round_unsafe_result.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/runner.py` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/short_circuit.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/short_circuit_malformed.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sinus_boolean.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sinus_wrong_arity.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sqrt_boolean.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sqrt_negative.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sqrt_wrong_arity.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/statistics_sum_boundaries.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sum_boolean.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sum_intermediate_unsafe.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sum_non_list.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sum_unsafe_input.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sum_unsafe_result.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/sum_wrong_arity.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/undefined_variable.cuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/conformance/unicode_output.pusingcuk` | Fixture/manifest/runner konformansi; bukti target bergantung hasil CI. |
| `tests/fixtures/ai_adversarial_eval.json` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/fixtures/core_budget_sufficiency.json` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/fixtures/cukaccount_financial_acceptance.json` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/fixtures/knowledge_retrieval_cases.json` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/fixtures/priority_triage.json` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/native/conversions.cuk` | Kasus uji runtime native C. |
| `tests/native/conversions_empty_number.cuk` | Kasus uji runtime native C. |
| `tests/native/conversions_invalid_integer.cuk` | Kasus uji runtime native C. |
| `tests/native/conversions_non_finite_decimal.cuk` | Kasus uji runtime native C. |
| `tests/native/dictionaries.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/dictionary_invalid_key.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/dictionary_key_types.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/dictionary_missing_key.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/dictionary_overflow.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/for_range.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/function_wrong_arity.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/functions.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/list_overflow.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/list_reallocation.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/nested_functions.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/numeric_large_finite.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/numeric_non_finite_literal.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/numeric_overflow.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/range_zero_step.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/slang_aliases.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/string_concat_limit.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/string_concat_overflow.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/string_index_out_of_range.pusingcuk` | Kasus uji runtime native C. |
| `tests/native/strings_input.pusingcuk` | Kasus uji runtime native C. |
| `tests/test_accounting_equation_rule.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_ai_adversarial_eval.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_ai_e2e.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_ai_service.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_ai_tools.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_all.sh` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_assistant.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_budget_example.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_builtin_contract.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_c_backend.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_cli_diagnostics.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_cli_modes.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_cli_module_outside_root.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_command_execution.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_compiler_cli.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_compiler_ir.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_conformance_contract.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_core_budget_rules.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_diagnostic_repair_loop.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_evaluator.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_examples_cuk.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_exit_codes.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_format_builtins.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_formatter.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_gemini_ai_provider.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_interpreter.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_ir.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_js_backend.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_js_build_cli.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_knowledge_grounding.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_level4_module.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_level5_hardening.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_level6_ssrf.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_lexer.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_local_ai_provider.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_local_memory.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_modular_pipeline.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_module_system_extensions.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_offline_adapters.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_parser.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_parser_diagnostics.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_period_close_plan.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_project_path_security.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_pvm_path_sandbox.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_python_backend.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_python_importer.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_registered_rules.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_repl.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_runtime_conformance.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_studio_service.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_terminal.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_try_catch_binding.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_typesystem.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_version_contract.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_vm.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_vocabulary_registry.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tests/test_web_workbench.py` | Tes otomatis atau fixture; cakupan aktual mengikuti test runner. |
| `tools/__init__.py` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/conformance.py` | Harness konformansi reference/native. |
| `tools/core-rule-runner.mjs` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/diagnostic_repair_loop.py` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/evaluate_knowledge_retrieval.py` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/evaluate_live_ai.py` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/formatter.py` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/sandbox/Dockerfile` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/sandbox/build-image.sh` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/sandbox/entrypoint.sh` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/termux_dashboard.sh` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `tools/web_workbench.py` | Tooling pengembangan/diagnostik/runner; bukan otomatis bagian runtime. |
| `web/index.html` | UI/playground web; target dan subset harus diverifikasi terpisah. |


---

# Addendum — syarat pemilik sebelum merge (2026-10-18)

> **Status: syarat belum terpenuhi sepenuhnya. PR #93 tidak boleh di-merge dulu.** Audit sumber telah diperdalam berdasarkan isi file yang tersedia lewat GitHub. Eksekusi penuh seluruh fixture di sandbox tidak dapat dilakukan karena sandbox tidak dapat menyelesaikan DNS `github.com`; log mentah kegagalan akses dicantumkan di bawah. Saya tidak mengganti hasil yang tidak tersedia dengan angka perkiraan.

## A. Eksekusi nyata per target dan log

### A.1 Hasil yang benar-benar tersedia

| Target | Perintah/eksekusi yang dapat diverifikasi | Lulus | Gagal | Tidak didukung | Status yang jujur |
|---|---|---:|---:|---:|---|
| Interpreter referensi | CI main run #1134 menjalankan `python tools/conformance.py` di Python 3.12 | Tidak ada hitungan per fixture di ringkasan job | Tidak ada hitungan per fixture di ringkasan job | Belum ada agregat per target yang disimpan | Job conformance **success** |
| Native C | CI main run #1134 menjalankan `make test-native` pada GCC dan Clang; conformance harness juga membangun C ketika dijalankan | Tidak ada hitungan per fixture di ringkasan job | Tidak ada hitungan per fixture di ringkasan job | Manifest menyatakan 3 fixture native unsupported | Job GCC/Clang **success**; hasil fixture individual belum diekspor |
| JavaScript | Tidak ada runner conformance lintas target yang bisa dijalankan dari lingkungan audit ini | Belum diukur | Belum diukur | Belum diukur | **Tidak diukur** |
| Python transpiler | Tidak ada runner conformance lintas target yang bisa dijalankan dari lingkungan audit ini | Belum diukur | Belum diukur | Belum diukur | **Tidak diukur**; jangan campur dengan reference interpreter |
| HTML | Tidak ditemukan file `compiler/html_backend.py` dalam tree; backend HTML yang berdiri sendiri belum terbukti ada | 0 terukur | 0 terukur | Tidak dapat ditentukan tanpa pemetaan CLI/target | **Keberadaan target HTML belum terverifikasi** |
| VM/bytecode | Unit test VM ada, tetapi conformance manifest saat ini hanya mengizinkan `reference` dan `native` | Belum diukur | Belum diukur | Belum dinyatakan di manifest | **Tidak diukur** |

**Penting:** “tidak diukur” tidak sama dengan nol lulus, gagal, atau unsupported. Angka harus dihasilkan dari log runner yang benar-benar dijalankan. Run #1134 membuktikan job CI berhasil pada commit main yang diperiksa, tetapi ringkasan job tidak memberi agregat pass/fail per fixture untuk ditranskripsi secara akurat.

### A.2 Percobaan sandbox audit — log mentah

Perintah yang dijalankan dari sandbox audit:

```console
$ git clone --depth 1 --branch audit/phase-0-baseline https://github.com/rllibo833-sudo/pusingcuk.git /tmp/pusingcuk-audit
Cloning into '/tmp/pusingcuk-audit'...
fatal: unable to access 'https://github.com/rllibo833-sudo/pusingcuk.git/': Could not resolve host: github.com
```

Exit status: `128`. Akibatnya tidak ada working tree lokal, sehingga perintah berikut **tidak dijalankan** di sandbox ini:

```console
python tools/conformance.py
python -m unittest discover -s tests -v
make test-native
```

Tidak ada log mentah per-fixture untuk JS, Python transpiler, HTML, atau VM karena tidak ada runner terpadu yang menjalankannya di lingkungan ini. Mengarang log tersebut akan melanggar prinsip evidence-over-claims.

### A.3 Perintah reproduksi yang tersedia bagi CI

Dari root repository, workflow core menggunakan:

```console
python -m unittest discover -s tests -v
python tools/conformance.py
make test-native
```

Sumber workflow: `.github/workflows/tests.yml`. `tools/conformance.py` saat ini hanya menerima runtime `reference` dan `native`; runner memanggil `pusingcuk_new.py` untuk reference dan executable hasil kompilasi `native/pusingcuk.c` untuk native. Jadi menjalankan perintah yang sama belum menguji JS, Python transpiler, HTML, atau VM.

### A.4 Python-Free Score — definisi yang dibatasi

Pengukuran terbaru menghasilkan **Runtime Python-Free Score 96,10% (74/77)** untuk suite fixture saat ini. Ini mengukur keberhasilan eksekusi fixture melalui executable native C; ini bukan skor seluruh bahasa dan bukan bukti toolchain bebas Python.

- **Runtime Python-free:** executable C membaca dan menjalankan file .cuk tanpa memanggil interpreter Python pada jalur eksekusi program.
- **Toolchain Python-free:** **belum terbukti**. Build fixture-native, orchestration/harness, dan pemeriksaan hasil saat ini memakai Python (tools/conformance.py dan tools/ci_fixture_matrix.py).
- Rumus skor runtime: jumlah fixture manifest yang lulus pada native C / total fixture manifest × 100. Semua fixture tetap berada dalam penyebut, termasuk fixture native yang unsupported.
- VM tidak memenuhi definisi runtime Python-free saat ini karena compiler/vm.py mengimpor helper evaluator Python.
- Skor hanya berlaku untuk suite fixture yang terdaftar pada commit pengukuran. Ia tidak mewakili semua sintaks, built-in, kombinasi fitur, perilaku, platform, atau program pengguna dalam bahasa .cuk.

Jangan menyebut skor ini sebagai bukti bahwa seluruh proses build, test, atau compiler sudah bebas Python.

## B. Pembacaan mendalam modul inti

Penilaian berikut berdasarkan pembacaan isi file dari GitHub pada branch audit, bukan eksekusi dinamis. “Tidak ditemukan” berarti tidak terlihat pada area yang diperiksa, bukan bukti formal seluruh repository.

### B.1 Lexer — `lexer.py`

**Status:** modul inti aktif, reference lexer.

- Memiliki kelas `Lexer`, `Token`, `LexerError`, pemindai angka/identifier/string, operator dan alias keyword. Token menyimpan baris dan kolom.
- Alias bahasa disatukan ke `KEYWORD_ALIASES`, tetapi daftar keyword dan alias tetap dua sumber data yang harus diuji terhadap SPEC/kosakata. Perubahan alias dapat memengaruhi program lama.
- Risiko: posisi diagnostik, escape string, eksponen, operator multi-karakter, Unicode identifier, dan alias keyword perlu fixture positif/negatif. Klaim coverage harus berasal dari fixture.
- Duplikasi: tidak ada bukti cukup untuk menyatakan lexer mati/duplikat; ia adalah dependency parser utama.
- Status kode mati: belum dibuktikan melalui analisis coverage/dead-code; jangan tandai kode sebagai mati berdasarkan nama saja.

### B.2 Parser — `parser.py`

**Status:** modul inti aktif, parser recursive-descent/precedence.

- Memakai `lex` dari lexer dan pembuat node AST dari `ast_nodes`; menangani statement, ekspresi, pemanggilan fungsi, serta format/saran diagnostik.
- Parser dan lexer masih di root, bukan package `src/pusingcuk/`; import absolut antarmodul membuat restrukturisasi berisiko bila dilakukan tanpa uji backward compatibility.
- Risiko: grammar, prioritas operator, diagnostik line/column, blok bersarang, serta error pemulihan harus terikat ke SPEC dan fixture. Pesan diagnostik tidak boleh dijadikan kontrak semantik kecuali kontrak menyatakannya.
- Duplikasi: fungsi diagnostic helper berada di parser; sebelum dipindah ke modul bersama, cek consumer dan output fixture. Tidak ada bukti cukup untuk menyebut parser dead code.

### B.3 Evaluator — `evaluator.py`

**Status:** reference runtime aktif; modul besar (~43 KB) dengan banyak tanggung jawab.

- Menjalankan AST, memelihara semantik nilai/dictionary, modul, file I/O, HTTP, dan pemanggilan command yang opt-in. Batas resource yang terlihat termasuk ukuran HTTP request/response, ukuran file modul dan kedalaman modul; beberapa operasi memakai timeout.
- Duplikasi nyata: `Path` diimpor dua kali (`from pathlib import Path`, kemudian `from pathlib import Path, PureWindowsPath`). Ini redundan dan layak dibersihkan pada fase yang tepat tanpa mengubah perilaku.
- Risiko keamanan: evaluator mengandung akses filesystem, jaringan, dan subprocess. Eksekusi command dibatasi oleh environment flag `PUSINGCUK_ENABLE_EXECUTION=1`, memakai `shell=False` dan timeout 30 detik; hal ini **bukan** sandbox OS dan bukan capability sandbox menyeluruh. Pengamanan URL dan path adalah defense-in-depth yang perlu pengujian adversarial, bukan jaminan isolasi.
- Risiko maintainability: modul monolitik membuat review regresi lebih sulit; pemecahan hanya boleh dilakukan setelah contract/fixture menutupi perilaku.
- Status kode mati: belum ada bukti coverage/dead-code report yang dapat mengonfirmasi fungsi mana tidak dipakai. Tidak menandai fungsi sebagai dead tanpa bukti call graph dan coverage.

### B.4 `compiler/`

**Status:** kumpulan backend/alat campuran; tidak satu target seragam.

- File yang terdaftar: `__init__.py`, `__main__.py`, `android_backend.py`, `bytecode.py`, `c_backend.py`, `import_python.py`, `ir.py`, `js_backend.py`, `python_backend.py`, `typesystem.py`, `vm.py`.
- `ir.py` menyatakan IR v1 deterministik dan AST-preserving; memiliki validasi ukuran/depth/node/collection. Headernya sendiri menegaskan IR bukan bytecode executable.
- `bytecode.py` memiliki daftar opcode, compiler dari IR, dan validator bytecode. `vm.py` memvalidasi bytecode dan menerapkan step limit serta depth limit, tetapi mengimpor `PusingDict` dan `language_equal` dari evaluator. Jadi VM belum terisolasi dari modul reference Python.
- `js_backend.py` dan `python_backend.py` ada, tetapi keberadaan file bukan bukti parity runtime. Manifest/harness utama belum menjalankan fixture terhadap keduanya.
- File `compiler/html_backend.py` **tidak ada** pada tree yang diperiksa. Jangan mengiklankan backend HTML mandiri sampai jalur target dan tes aktual ditemukan.
- `c_backend.py` ada sebagai backend terpisah dari `native/pusingcuk.c`; perlu dipetakan apakah keduanya memiliki peran berbeda (transpiler C vs interpreter native) agar istilah “target C” tidak ambigu.
- Risiko: format IR/bytecode belum boleh disebut ABI stabil hanya karena memiliki versi angka; perlu spesifikasi, kompatibilitas dan fixture lintas versi.
- Duplikasi: ada beberapa lapisan eksekusi/terjemahan (reference evaluator, C native interpreter, C backend, JS, Python transpiler, VM). Itu adalah beberapa implementasi semantik yang berpotensi divergen; belum cukup bukti untuk menyebut salah satunya kode mati.
- Rekomendasi: CRE perlu mengklasifikasikan target per runner yang nyata, dan menampilkan `unsupported` hanya jika ada deklarasi eksplisit; kegagalan build harus `unavailable` atau `fail`, bukan unsupported.

### B.5 `native/`

**Status:** runtime C native aktif untuk subset yang diuji.

- `native/pusingcuk.c` adalah implementasi mandiri dengan batas statis/eksplisit: jumlah variabel, item list/dict, fungsi/parameter, jumlah baris dan jumlah langkah. Header mengakui file I/O belum tersedia pada C runtime.
- `native/Makefile` mengaktifkan `-Wall -Wextra -Werror`, yang baik untuk menemukan warning pada kompilasi.
- Risiko parity: batas kapasitas dan semantik bisa berbeda dari evaluator Python; perbedaan harus berupa fixture/parity issue, bukan klaim ekuivalensi.
- Risiko maintainability: satu file C besar dengan parser/evaluator dan banyak state global meningkatkan biaya review; jangan refactor tanpa fixture yang mengunci perilaku.
- Status kode mati: TODO file I/O adalah keterbatasan yang dinyatakan, bukan kode mati. Belum ada laporan dead-code yang dapat diverifikasi.

### B.6 `library/assistant.py`

**Status:** CLI asisten AI yang menggunakan provider eksternal/lokal; bukan model dasar yang dilatih sendiri.

- Mengimpor Gemini provider dan provider Ollama lokal, retrieval knowledge grounding, tool registry, serta local memory. Default CLI memilih Ollama, sedangkan Gemini dapat dipilih melalui argumen/environment.
- Batas tool terlihat: maksimal 5 putaran dan 8 pemanggilan tool per permintaan. Batas ini mengurangi loop tak berujung, tetapi tidak menggantikan validasi izin masing-masing tool.
- Risiko reliabilitas: `ask()` menangkap `Exception` secara luas. Periksa apakah error dilaporkan secara cukup diagnostik dan apakah kegagalan provider/tool tidak tersamarkan sebagai jawaban sukses. Perubahan penanganan error harus ditopang tes.
- Risiko privasi: CLI mempunyai `LocalMemoryStore` yang mendukung penyimpanan catatan lokal. Dokumentasi UX perlu menjelaskan bahwa catatan tersimpan berbeda dari konteks percakapan in-process; jangan menyebut seluruh data tidak pernah persisten.
- Risiko klaim: adanya provider Gemini/Ollama dan retrieval tidak membuktikan model PusingCuk dilatih/fine-tuned sendiri. Klaim publik harus menyebut lapisan aplikasi/provider secara eksplisit.
- Duplikasi/dead code: tidak dapat diputuskan dari file tunggal; perlu call graph dan test coverage. Tidak ditemukan bukti cukup untuk menandai modul ini mati.

### B.7 Ringkasan risiko dan prioritas

| Prioritas | Temuan | Rekomendasi |
|---|---|---|
| Tinggi | Belum ada eksekusi fixture satu matriks untuk seluruh target | Phase 3: jalankan per target, simpan log dan JSON hasil per fixture |
| Tinggi | VM Python mengimpor helper evaluator Python | Jangan klaim VM Python-free; hilangkan coupling hanya dengan fixture parity |
| Tinggi | Evaluator memiliki filesystem/network/subprocess | Tetapkan scope izin; jangan menyebutnya OS sandbox |
| Tinggi | Klaim HTML target belum ditopang backend/runner yang ditemukan | Temukan implementasi aktual atau labeli roadmap |
| Sedang | Reference evaluator dan native C terpisah, backend C tambahan | Definisikan istilah target dan jalur build/run |
| Sedang | Import `Path` ganda dan evaluator besar | Bersihkan/refactor hanya setelah baseline tes tersedia |
| Sedang | AI provider/tool/memory memiliki beberapa jalur | Tambahkan tes error, privasi, batas tool dan dokumentasi provider |
| Belum dapat ditentukan | Kode mati secara formal | Perlu coverage, call graph, dan analisis dinamis; tidak menebak dari nama |

## C. Filter path CI tidak mencakup docs-only PR

Workflow `.github/workflows/tests.yml` memiliki `pull_request.paths` dan `push.paths` yang mencakup file kode, tes, examples, README, CHANGELOG dan konfigurasi tertentu, tetapi **tidak mencakup `docs/**`**. Akibatnya, perubahan dokumentasi saja seperti PR #93 tidak memicu workflow core. Ini adalah gap tata kelola: dokumen bukti dapat berubah tanpa pemeriksaan otomatis yang diharapkan, dan PR berisiko tertahan tanpa status check yang memberi umpan balik.

### Solusi yang direkomendasikan untuk Phase 1

1. Tambahkan `docs/**` ke filter `pull_request.paths` dan `push.paths` workflow core; minimal jalankan unit tests + conformance untuk docs-only PR, atau pisahkan workflow `docs-validation.yml` yang memeriksa tautan/format dan memvalidasi output yang digenerate.
2. Pastikan CI wajib yang tepat selalu berjalan pada PR; hati-hati bahwa GitHub dapat meninggalkan required check dalam status “Expected” bila filter path melewati workflow. Jika path filtering tetap digunakan, buat check aggregator yang selalu berjalan dan melaporkan status dengan benar.
3. Tambahkan validasi dokumen berbasis sumber: periksa tautan file/anchor, contoh runnable yang memang didaftarkan sebagai fixture, dan stale generated artifacts. Jangan jalankan semua compiler untuk setiap perubahan typo jika waktu CI menjadi berlebihan; gunakan job docs terpisah plus core CI untuk perubahan kode/fixture.
4. Terapkan ruleset/branch protection di pengaturan GitHub secara manual oleh owner; perubahan workflow tidak mengaktifkan proteksi branch secara otomatis.
5. Verifikasi dengan PR docs-only, PR code-only, dan PR campuran bahwa check yang dimaksud benar-benar muncul dan berhasil.

## D. Keputusan atas syarat merge

- [x] Tambahkan temuan filter path CI dan rekomendasi Phase 1.
- [x] Pembacaan mendalam awal terhadap lexer, parser, evaluator, compiler/, native/, dan library/assistant.py; batas bukti dan risiko dicatat.
- [x] Baseline seluruh 77 fixture diukur per target pada GitHub Actions; raw log dan JSON ringkasan tersedia sebagai artifact run #4.
- [x] Python-Free Score dihitung dari hasil nyata dengan pembagi seluruh 77 fixture: 74/77 = 96,10%.
- [x] PR #93 telah di-merge oleh pemilik. Hasil pengukuran dilampirkan lewat PR dokumentasi terpisah ini.
- [ ] Perbaikan backend JS, Python transpiler, dan VM berada di luar scope baseline ini; perlu persetujuan terpisah sebelum pekerjaan implementasi berikutnya.

**Keputusan:** Phase 1 mengukur dan melaporkan baseline saja. Tidak dimulai restrukturisasi atau Phase 2 tanpa persetujuan pemilik.


## E. Klarifikasi baseline sebelum merge — 2026-10-18

Bagian ini merupakan klarifikasi terkini atas catatan audit historis yang lebih lama di atas. Tidak ada perubahan semantik runtime dalam pembaruan baseline ini.

### E.1 Jalur native C dan cakupan Python-free

Matriks CI memanggil tools/ci_fixture_matrix.py, yang memakai tools/conformance.py::build_native untuk membangun executable dari native/pusingcuk.c dengan compiler C (CC, default cc), flag C11/optimisasi/warning, dan -lm. Untuk setiap fixture yang didukung, prosesnya menjalankan executable dengan argumen path sumber fixture, lalu membandingkan stdout, kelas stderr, exit code, dan baris sumber terhadap manifest. Runner Python menyiapkan proses dan mengumpulkan hasil, tetapi executable native menjalankan program .cuk itu sendiri tanpa interpreter Python.

| Ukuran | Kesimpulan |
|---|---|
| Runtime Python-free | Ya untuk jalur eksekusi native C yang diukur: program .cuk dieksekusi oleh executable C. |
| Toolchain Python-free | Belum: build orchestration, conformance harness, matriks, dan agregasi hasil masih memakai Python. |
| VM Python-free | Tidak: VM saat ini bergantung pada helper evaluator Python. |

### E.2 Tiga fixture yang unsupported pada native C

| Fixture | Alasan fitur |
|---|---|
| reference.json-invalid-returns-false (json_invalid_returns_false.cuk) | Penguraian JSON dan kontrak hasil parse invalid belum tersedia pada native C. |
| reference.json-null-returns-none (json_null_is_none.cuk) | Semantik JSON null menjadi nilai None belum tersedia pada native C. |
| formats.json-html-csv (formats_json_html_csv.cuk) | Memerlukan kombinasi built-in JSON, HTML escaping, dan CSV quoting yang belum didukung pada native C. |

Status ini berasal dari deklarasi native: unsupported di tests/conformance/manifest.json, bukan kegagalan build atau eksekusi yang disamarkan sebagai unsupported.

### E.3 Perbandingan summary antar-run

Run pertama: [39126748621](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39126748621). Run kedua dengan formula yang dikoreksi: [39127088393](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39127088393). Run ketiga/final: [39127180391](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39127180391).

**Semua hitungan status per target identik** pada ketiga artifact:

| Target | Lulus | Gagal | Timeout | Unsupported | Unavailable |
|---|---:|---:|---:|---:|---:|
| Reference | 77 | 0 | 0 | 0 | 0 |
| Native C | 74 | 0 | 0 | 3 | 0 |
| JavaScript | 29 | 48 | 0 | 0 | 0 |
| Python transpiler | 21 | 56 | 0 | 0 | 0 |
| HTML | 0 | 0 | 0 | 77 | 0 |
| VM | 28 | 49 | 0 | 0 | 0 |

**Ada satu selisih metadata yang disengaja:** artifact run pertama menghitung skor 74/74 = 100% karena fixture unsupported dikeluarkan dari penyebut. Formula itu kemudian diperbaiki sesuai cakupan seluruh manifest. Run kedua dan ketiga mencatat 74/77 = 96,10%; tidak ada perubahan pada hitungan status target. Artifact run ketiga menjadi baseline yang disimpan dalam repo.

### E.4 Kandidat isu bug-parity berdasarkan kelompok kegagalan

Pengelompokan di bawah berasal dari pola pesan kompilasi/eksekusi pada raw.log. Ini adalah **kelompok kandidat untuk investigasi parity**, bukan bukti bahwa semua kasus dalam satu kelompok memiliki satu akar kode yang sama. Jumlah per kelompok menjumlah ke total gagal tiap target.

**JavaScript — 48 gagal**

| Pola akar masalah yang terlihat | Jumlah |
|---|---:|
| Perbedaan kelas diagnostik runtime / mismatch output atau exit code | 22 |
| Pemeriksaan aritas saat kompilasi berbeda dari diagnostik runtime reference | 10 |
| Exception host JavaScript bocor, bukan diagnostik .cuk yang stabil dengan lokasi sumber | 4 |
| Batas integer aman ditolak saat kompilasi | 4 |
| Paritas sintaks atau lokasi diagnostik | 3 |
| Analisis nama statis menolak kasus runtime, short-circuit, atau scope | 3 |
| Cakupan built-in JSON tidak tersedia | 2 |

**Python transpiler — 56 gagal**

| Pola akar masalah yang terlihat | Jumlah |
|---|---:|
| Perbedaan diagnostik runtime / mismatch output atau exit code | 22 |
| Cakupan built-in/fungsi yang belum dikenali transpiler | 14 |
| Pemeriksaan aritas saat kompilasi berbeda dari reference | 8 |
| Paritas sintaks atau lokasi diagnostik | 3 |
| Analisis nama statis menolak kasus runtime, short-circuit, atau scope | 3 |
| Exception host Python bocor, bukan diagnostik .cuk yang stabil | 3 |
| Mismatch output/exit code pada built-in numerik | 2 |
| Kasus compile-time lain | 1 |

**VM/bytecode — 49 gagal**

| Pola akar masalah yang terlihat | Jumlah |
|---|---:|
| Perbedaan diagnostik runtime / mismatch output atau exit code | 38 |
| Exception host Python bocor, bukan diagnostik .cuk yang stabil | 6 |
| Paritas sintaks atau lokasi diagnostik saat kompilasi bytecode | 3 |
| Kelas/lokasi diagnostik runtime berbeda | 1 |
| Semantik operator/tipe, termasuk concatenation koleksi | 1 |

Kelompok ini menjadi daftar kandidat bug-parity untuk dibahas terpisah. Tidak ada perbaikan backend yang dilakukan sebagai bagian pembaruan baseline ini.

### E.5 Gerbang regresi dan batas skor

Baseline hasil terukur disimpan sebagai tests/conformance/baseline_summary.json. Workflow matriks membandingkan jumlah passed setiap target dengan snapshot tersebut; CI gagal jika hitungan lulus target mana pun turun. Perubahan baseline di masa mendatang harus ditinjau secara eksplisit, bukan diperbarui otomatis agar kegagalan terlihat hijau.

**Peringatan cakupan:** skor 96,10% dihitung hanya atas suite 77 fixture yang ada pada snapshot ini. Itu bukan persentase kelengkapan bahasa .cuk, bukan sertifikasi paritas semua backend, bukan skor keamanan, dan bukan bukti toolchain Python-free. Backend HTML tetap belum tersedia; seluruh 77 fixture HTML tercatat unsupported, bukan gagal dijalankan.
