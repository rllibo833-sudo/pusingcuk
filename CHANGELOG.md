# Changelog

Catatan perubahan PusingCuk. Metadata paket pada `main` adalah **0.7.2** (belum dipublikasikan sebagai tag rilis); kontrak bahasa kanonis tetap **0.4-dev**. Tag rilis `v0.7.1` menunjuk snapshot yang lebih lama daripada `main`; catatan di bawah belum termasuk dalam artefak rilis `v0.7.1`.

## Unreleased — target paket 0.7.2; kontrak bahasa 0.4-dev

### Audit dan sinkronisasi

- **Versioning:** selaraskan metadata paket di `pyproject.toml`, `Makefile`, registry kosakata, dan fallback runtime native ke `0.7.2`; versi bahasa tetap `0.4-dev`.
- **Keamanan PVM:** opcode file pada JavaScript dinonaktifkan; runtime Python default-deny dan hanya membuka capability untuk bytecode tepercaya melalui `--allow-file-io`. Jika primitive POSIX tersedia, akses memakai root descriptor tetap, `dir_fd`/`openat`, dan `O_NOFOLLOW`; absolute path, traversal, dan symlink ditolak. Ini mitigasi aplikasi, bukan sandbox OS; Issue #75 tetap terbuka untuk review independen.
- **Jaringan:** evaluator Python memvalidasi tujuan HTTP(S), mengikat koneksi pada IP publik yang telah diperiksa, memvalidasi ulang redirect, dan membatasi ukuran respons. Perlindungan ini tidak boleh diasumsikan tersedia pada runtime native, PVM, atau kode hasil kompilasi.
- **CLI dan parser:** resolusi impor statis mengikuti direktori proyek/modul; `balek` tanpa ekspresi ditolak; `jadi_json` menghasilkan `salah` untuk JSON invalid, sedangkan JSON `null` valid menjadi nilai null bahasa.
- **CI/CD:** permission workflow dirinci dan action pihak ketiga dipatok pada commit SHA. Workflow release manual meminta tag eksplisit agar tidak tanpa sengaja membangun ulang tag lama.
- **Contoh dan belajar:** tambah kalkulator `examples/kalkulator.cuk` dengan keyword kanonis `njir`/`kampret`, tangani input nonnumerik dan pembagian nol, serta tes CLI; indeks contoh menjelaskan dukungan target dan efek samping file/jaringan.
- **Parser dan diagnostik:** pesan kesalahan mencantumkan nama file, baris, kolom, potongan sumber, pointer, dan saran koreksi tanpa bahasa yang merendahkan; tes regresi mengunci format lokasi.
- **Termux/CLI:** sediakan `scripts/test-termux-device.sh` untuk menguji instalasi paket, shebang/executable, input interaktif, native C, dan kode keluar di perangkat nyata. Skrip ini harus dijalankan manual di perangkat; cross-build CI tidak dihitung sebagai uji perangkat.
- **CI/tata kelola:** jalankan regresi PVM secara otomatis pada workflow tes utama; metadata paket `0.7.2` tetap dibedakan dari kontrak bahasa `0.4-dev`. Perlindungan branch settings harus diverifikasi/diaktifkan pada pengaturan GitHub repo.
- **Dokumentasi:** sinkronkan batas kompatibilitas, versi paket/bahasa, dan peringatan keamanan; contoh PusingCuk maupun bytecode tidak boleh dipresentasikan sebagai eksekusi yang terisolasi.

### Gate sebelum rilis

- Verifikasi status seluruh 19 built-in melalui `library/builtin_contract.json`; 15 didukung pada native C, 14 pada transpiler JS, 14 pada transpiler Python/HTML, dan 6 pada VM eksperimental.
- Jalankan `python -m pytest -q`, `make test`, serta workflow build Python dan native C. CI yang lulus hanya membuktikan cakupan pengujian yang dijalankan; tidak menutup risiko sandbox pada Issue #75.
