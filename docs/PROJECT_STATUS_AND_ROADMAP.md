# PusingCuk — Status Proyek

**Snapshot:** 20 Oktober 2026 · language contract `0.6-dev` · package `0.8.0.dev0`.
**Compiler evidence commit:** `fea06e6c7bd77f46ec45b4988e45e85d5fec13e5`.
**Status rilis:** experimental. CI hijau berarti kontrak dan fixture yang dijalankan lulus; bukan jaminan semua program, platform, atau fitur AI siap produksi.

## Bukti CI terbaru

- Core: [run 39426734047](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39426734047) — sukses, termasuk unit test Python 3.11/3.12 dan native GCC/Clang.
- Fixture matrix: [run 39426734065](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39426734065) — sukses; artifact berisi hasil 77 fixture.

| Target | Hasil fixture | Status yang boleh diklaim |
|---|---:|---|
| Reference interpreter | 77/77 | Semantik acuan; masih memerlukan Python |
| Native C | 74/77; 3 unsupported | Runtime dapat dijalankan tanpa Python setelah dibangun untuk subset yang diuji |
| JavaScript transpiler | 77/77 | Semua fixture aktif lulus; bukan jaminan untuk semua program |
| Python transpiler | 77/77 | Semua fixture aktif lulus; hasil tetap memerlukan Python |
| Bytecode/VM | 77/77 | Semua fixture aktif lulus; VM saat ini masih memakai helper Python |
| HTML | 0/77; 77 unsupported | Belum merupakan target eksekusi mandiri yang terverifikasi |

Perbandingan reference/native mencakup 74 fixture wajib: **0 mismatch, 0 incomplete, 3 unsupported**. Status fixture terbaru disimpan di `tests/conformance/baseline_summary.json`; run CI dan artifact adalah bukti eksekusi untuk commit tertentu.

## Batas produk

- **Bahasa `.cuk`:** lexer, parser, kontrak semantik, interpreter referensi, native C, JavaScript/Python transpiler, dan VM tersedia. Target belum setara untuk semua fitur; dukungan per built-in ditentukan oleh `library/builtin_contract.json` dan fixture.
- **PusingCuk AI:** adapter local-first dapat menggunakan Ollama lokal. `OLLAMA_MODEL` memilih model; adapter tidak boleh dianggap sebagai model yang dilatih dari nol atau sebagai sistem perbaikan otomatis yang selalu benar.
- **Reality Engine:** menerima/menolak usulan berdasarkan bukti source/fixture yang sudah terdaftar. Menjalankan fixture yang sudah ada bukan bukti bahwa fitur baru telah ditambahkan, didokumentasikan, atau setara di semua target.
- **Keamanan workflow:** jangan memakai penggantian string global pada source, `git add .` tanpa tinjauan, `|| true` untuk tes wajib, atau commit/push otomatis ke `main`. Perubahan bahasa harus melewati kontrak, fixture, target implementation, dan CI.

## Prioritas berikutnya

1. **Native C:** implementasikan JSON parse/serialize serta HTML/CSV helpers yang saat ini menjelaskan tiga fixture unsupported; tambah tes positif/negatif dan jalankan differential matrix.
2. **HTML:** tetapkan apakah target ini wrapper browser dari JS atau backend terpisah; jangan menyebutnya executable sampai fixture benar-benar dijalankan di harness yang sesuai.
3. **AI + Reality Engine:** satukan satu jalur proposal → compiler diagnostics → fixture baru/yang relevan → eksekusi target → verifikasi; jangan menandai `fixture_added` sebelum manifest dan file fixture benar-benar berubah.
4. **Dokumentasi:** `SPEC.md` untuk sintaks/semantik pengguna, `library/builtin_contract.json` untuk status built-in, `tests/conformance/manifest.json` untuk kasus uji, `docs/COMPATIBILITY.md` untuk hasil lintas target. Dokumen status lain harus merujuk ke sumber ini, bukan menyalin angka historis.

README dan deskripsi repositori tetap berstatus experimental sampai native C dan target HTML tidak lagi memiliki gap yang diklaim sebagai target rilis.
