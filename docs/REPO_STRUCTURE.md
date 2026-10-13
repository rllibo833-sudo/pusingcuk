# Peta Repositori Pusingcuk

Dokumen ini menunjukkan tempat yang tepat untuk memulai. Baseline yang aktif adalah **interpreter referensi Python + runtime native C**. Folder eksperimen tetap disimpan, tetapi bukan bukti bahwa fitur tersebut sudah stabil atau setara lintas runtime.

## Jalur pengguna

| Lokasi | Fungsi |
|---|---|
| `README.md` | Ikhtisar dan cara tercepat menjalankan program |
| `docs/PEMULA.md` | Tutorial dasar |
| `docs/termux/README.md` | Jalur Termux dengan Python atau executable C native |
| `SPEC.md` | Sintaks dan perilaku yang dimaksudkan |
| `docs/language/README.md` | Peta keyword, alias, kamus, built-in, dan kontrak bahasa |
| `docs/COMPATIBILITY.md` | Status dukungan per runtime |
| `SECURITY.md` | Kebijakan resmi dan pelaporan kerentanan |

## Implementasi bahasa yang dipelihara

| Lokasi | Peran |
|---|---|
| `pusingcuk_new.py` | CLI interpreter referensi; `--check` memvalidasi tanpa menjalankan program |
| `lexer.py` | Tokenisasi sumber dan normalisasi alias |
| `parser.py` | Parsing token ke AST |
| `ast_nodes.py` | Struktur AST |
| `evaluator.py` | Evaluasi AST dan semantik runtime Python |
| `terminal.py` | Terminal interaktif/REPL |
| `native/pusingcuk.c` | Runtime C11 mandiri dengan subset fitur teruji |
| `Makefile` | Target build dan tes runtime C |
| `library/kosakata.json` | Metadata kosakata dan status alias per target |
| `library/builtin_contract.json` | Kontrak metadata built-in yang dapat dibaca mesin; bukan package manager |

`interpreter.py` adalah implementasi historis yang terpisah; verifikasi entry point sebelum mengubah perilaku. `compiler/`, `compiler_ir.py`, `src/backends/`, dan `src/c-core/` berisi eksperimen compiler/VM/PVM, bukan jalur kompatibilitas utama. Khusus `src/c-core/`, periksa dokumen PVM karena itu bukan duplikat runtime di `native/pusingcuk.c`.

## Tes dan bukti kompatibilitas

- `tests/test_*.py`: unit/integration tests Python.
- `tests/conformance/manifest.json`: daftar fixture dengan hasil yang diharapkan dan status runtime.
- `tests/native/`: fixture batas dan error khusus runtime C.
- `tools/conformance.py`: menjalankan fixture yang sama pada Python dan C sesuai manifest.
- `make test-native`: membangun dan menguji runtime C lokal.
- `python -m unittest discover -s tests -v`: menjalankan suite unit Python.

Perilaku baru wajib disertai tes. Klaim kompatibilitas Python/C harus didukung fixture yang berstatus `required` pada keduanya; `unsupported` bukan kelulusan parity.

## Peta dokumentasi

- **Bahasa dan kamus:** `docs/language/README.md`, `SPEC.md`, `docs/PEMULA.md`, `docs/DICTIONARY.md`, `docs/KAMUS_PUSINGCUK.md`, `docs/KOSAKATA_GENZ.md`.
- **Semantik dan kompatibilitas:** `docs/SEMANTIC_CONTRACT.md`, `docs/COMPATIBILITY.md`, `docs/CONFORMANCE_FIXTURES.md`.
- **Native C dan Termux:** `docs/NATIVE_RUNTIME.md`, `docs/NATIVE_TERMUX.md`, `docs/termux/README.md`.
- **Keamanan:** `SECURITY.md`, `docs/security/README.md`, dan catatan audit bertanggal.
- **Eksperimen tertunda:** `docs/COMPILER_TARGETS.md`, `docs/COMPILER_INTEROP.md`, `docs/IR_V1.md`, `docs/PVM_SPEC.md`, `docs/ANDROID_STUDIO.md`, `docs/WEB_WORKBENCH.md`.

Indeks lengkap tersedia di [docs/README.md](README.md).

## Contoh, skrip, dan proyek tambahan

- `examples/`: contoh program pengguna.
- `examples/native/`: contoh yang ditujukan bagi subset native C.
- `scripts/`: skrip instalasi dan build; periksa isinya sebelum menjalankannya.
- `tools/`: conformance runner dan alat developer, termasuk workbench/dasbor opsional.
- `android-studio/`: aplikasi editor Android eksperimental; build APK tidak menjadi gate baseline dan bukan compiler APK Pusingcuk.
- `archive/legacy/`: kode lama untuk referensi, bukan titik mulai yang disarankan.
- `site/` dan `web/`: aset web; periksa workflow publikasi sebelum memindahkan/menghapus.
- `halo.cuk`: contoh kanonis ringkas untuk memverifikasi CLI.

## Alur kerja GitHub Actions

| Workflow | Peran |
|---|---|
| `.github/workflows/tests.yml` | CI utama: unit test Python, native C, dan konformansi |
| `.github/workflows/build-test.yml` | Verifikasi paket CLI Python dan executable PyInstaller |
| `.github/workflows/release.yml` | Build aset rilis untuk tag |
| `.github/workflows/android-native.yml` | Cross-build dan validasi binary runtime C untuk Android; bukan build aplikasi APK |
| `.github/workflows/experimental-pvm.yml` | Pemeriksaan PVM manual, di luar gate baseline |
| `.github/workflows/android-emulator-smoke.yml` | Smoke test emulator Android manual, tidak menahan gate inti | 
| `.github/workflows/android-studio-apk.yml` | Build APK Studio manual, ditunda dari CI inti |

Artefak build dan cache tidak boleh dimasukkan ke Git. `.gitignore` mengabaikan `__pycache__`, hasil test/coverage, `build/`, `dist/`, metadata paket, output Gradle, dan binary lokal. Cache Actions bersifat eksternal dan harus diatur pada workflow, bukan di-commit ke repositori.
