# Changelog

Catatan perubahan PusingCuk. Versi paket/distribusi dan versi kontrak bahasa merupakan dua hal yang berbeda: **paket CLI/Python 0.7.1** menggunakan **kontrak bahasa 0.4-dev**. Versi paket mengikuti metadata distribusi, sedangkan versi bahasa menandai spesifikasi semantik dan sintaks.

## v0.7.1 — kontrak bahasa 0.4-dev

### Hardening milestone — commit 7b7f903

- **Security:** Batasi pembacaan, penulisan, dan penghapusan berkas PVM/evaluator ke path relatif di project root; menolak path absolut, traversal (..), dan komponen symlink untuk membantu mitigasi Issue #75.
- **Security:** Ikat koneksi HTTP/HTTPS ke alamat IP publik yang telah divalidasi, validasi ulang setiap redirect, dan tambahkan regresi untuk DNS rebinding/SSRF.
- **CLI & engine:** Resolusi impor relatif angkut berdasarkan direktori skrip entrypoint atau modul yang mengimpor.
- **Parser & JSON:** Tolak balek tanpa ekspresi dan kembalikan salah untuk teks JSON yang tidak valid; JSON null valid tetap menghasilkan nilai null bahasa.
- **CI/CD:** Batasi izin default workflow rilis ke contents: read, pisahkan job publikasi yang membutuhkan contents: write, dan validasi format tag sebelum build.
- **Ecosystem:** Tetapkan .cuk sebagai ekstensi sumber kanonis, sediakan MIME Linux text/x-pusingcuk, serta dokumentasikan shebang #!/usr/bin/env pusingcuk untuk skrip executable.

### Post-consolidation examples

- Tambahkan contoh executable examples/halo_dunia.cuk dan examples/keuangan_sederhana.cuk; tes CLI otomatis memverifikasi input interaktif, fungsi, loop, kondisi, dan penulisan catatan yang tetap berada dalam project root.
