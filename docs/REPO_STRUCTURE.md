# Struktur Repositori PusingCuk

Dokumen ini adalah peta direktori kanonis. Tidak perlu membuat README status baru untuk setiap subproyek; gunakan dokumen domain yang sudah ada.

## Peta tingkat atas

| Lokasi | Tanggung jawab |
|---|---|
| `README.md`, `README_EN.md` | Pengenalan singkat dan quickstart; status rilis harus sesuai bukti |
| `SPEC.md`, `CHANGELOG.md`, `LICENSE`, `CONTRIBUTING.md` | Spesifikasi publik, sejarah rilis, lisensi, kontribusi |
| `lexer.py`, `parser.py`, `ast_nodes.py`, `evaluator.py`, `interpreter.py` | Implementasi bahasa referensi |
| `pusingcuk/` | Package/CLI kompatibilitas; perubahan lexer harus lulus pemeriksaan sinkronisasi |
| `compiler/` | IR dan backend C, JavaScript, Python, bytecode/VM, Android |
| `native/` | Runtime C mandiri dan tes build native |
| `src/` | Toolchain PVM eksperimental terpisah; bukan runtime yang sama dengan `compiler/vm.py` |
| `library/` | Kontrak built-in, kosakata, stdlib, AI service/provider, adapters dan data pengetahuan |
| `examples/` | Contoh program yang dipelihara berdasarkan domain |
| `site/` | Website GitHub Pages, playground, aset dan contoh browser |
| `tests/` | Unit/integrasi, conformance manifest, fixtures AI, dan tes native |
| `tools/`, `scripts/` | Runner, generator, adapter pengembangan, CI helpers, dan utilitas instalasi |
| `docs/` | Dokumentasi pengguna, bahasa, compiler, AI, security, dan satu roadmap aktif |
| `android-studio/`, `editors/` | Integrasi IDE/editor |
| `archive/legacy/` | Interpreter, program, dan artefak historis yang tidak lagi kanonis |
| `artifacts/` | Hasil matriks yang dikomit bila memang menjadi baseline; artefak CI per-run tetap di Actions |

## Titik masuk yang sering tertukar

- `python pusingcuk_new.py program.cuk`: CLI interpreter modular yang digunakan quickstart.
- `python -m compiler program.cuk --target <target>`: compiler multi-target; dukungan fitur berbeda per backend.
- `native/pusingcuk.c`: runtime native C; bukan source compiler Python.
- `site/playground.html`: playground statis GitHub Pages. Contoh browser harus diverifikasi oleh `tools/check_playground_examples.py`; jangan menganggap interpreter Python tersedia di browser.
- `tools/ci_fixture_matrix.py` dan `tools/differential_runner.py`: matrix dan differential checks.
- `tools/reality_engine.py`: gate usulan berdasarkan bukti; bukan bukti otomatis bahwa fitur baru sudah diimplementasikan.
- `library/assistant.py` dan `library/ai_service.py`: orkestrasi AI/adaptor lokal; bukan model dasar yang dilatih sendiri.

## Root-level compatibility entry points

Beberapa modul Python di root tetap dipertahankan karena dapat dipakai sebagai entry point/kompatibilitas oleh pengguna atau tes: `pusingcuk_new.py`, `compiler_ir.py`, `datacenter_v6.py`, `V6_CLEAN.py`, `fix_parser_all.py`, `terminal.py`, dan `halo.cuk`. Sebelum memindahkan modul tersebut, audit seluruh import, workflow, dokumentasi, dan pemanggilan eksternal; memindahkan file hanya demi tampilan dapat merusak API yang ada.

Draft issue yang sebelumnya berada di root dipindahkan ke [development/ISSUE_BACKLOG.md](development/ISSUE_BACKLOG.md), karena bukan dokumen publik utama.

## Sumber kebenaran dan generator

- `SPEC.md`: semantik dan sintaks bahasa yang terlihat pengguna.
- `library/kosakata.json`: kata kunci/alias terstruktur.
- `library/builtin_contract.json`: kontrak built-in.
- `tests/conformance/manifest.json`: daftar fixture dan status runtime yang diwajibkan.
- `tests/conformance/baseline_summary.json`: snapshot hasil yang dihasilkan dari matriks.
- `docs/COMPATIBILITY.md`: ringkasan kompatibilitas yang dihasilkan/ditinjau dari kontrak dan hasil fixture.
- `docs/PROJECT_STATUS_AND_ROADMAP.md`: satu-satunya roadmap aktif.
- `scripts/gen_docs_from_spec.py` dan `tools/generate_compatibility.py`: generator dokumen; jangan mengedit manual bagian di dalam marker yang dikelola generator.

## Aturan kebersihan

1. Tempatkan fitur baru di direktori domain yang sudah ada; jangan buat direktori paralel untuk status yang sama.
2. Simpan hasil uji sementara dan log di artefak CI atau direktori output yang diabaikan Git, bukan root.
3. File yang dipindahkan harus mendapat pembaruan semua referensi dan tes dalam perubahan yang sama.
4. Jangan menghapus arsip historis hanya karena sudah lama; pindahkan atau hapus hanya setelah dipastikan bukan input tes, kompatibilitas, atau provenance.
5. Catatan audit bertanggal tetap historis. Status saat ini harus dapat ditautkan ke commit dan run CI yang sama.
