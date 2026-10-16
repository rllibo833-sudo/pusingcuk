# Changelog

Catatan perubahan PusingCuk. Versi paket dan versi bahasa adalah dua identifier terpisah. Metadata pengembangan paket adalah **0.8.0.dev0** (PEP 440 untuk lini **0.8.0-dev**), dengan kontrak bahasa kanonis **0.5-dev**; tag lama tetap merupakan snapshot historis.

## [Unreleased - 0.5-dev] — target paket 0.8.0.dev0

### Audit dan sinkronisasi

- **Versioning:** pindahkan lini pengembangan paket ke `0.8.0.dev0` (PEP 440 untuk `0.8.0-dev`) dan kontrak bahasa ke `0.5-dev`; registry, runtime native, dan tes mempertahankan keselarasan metadata.
- **Keamanan PVM:** opcode file pada JavaScript dinonaktifkan; runtime Python default-deny dan hanya membuka capability untuk bytecode tepercaya melalui `--allow-file-io`. Jika primitive POSIX tersedia, akses memakai root descriptor tetap, `dir_fd`/`openat`, dan `O_NOFOLLOW`; absolute path, traversal, dan symlink ditolak. Ini mitigasi aplikasi, bukan sandbox OS; Issue #75 tetap terbuka untuk review independen.
- **Jaringan:** evaluator Python memvalidasi tujuan HTTP(S), mengikat koneksi pada IP publik yang telah diperiksa, memvalidasi ulang redirect, dan membatasi ukuran respons. Perlindungan ini tidak boleh diasumsikan tersedia pada runtime native, PVM, atau kode hasil kompilasi.
- **CLI dan parser:** resolusi impor statis mengikuti direktori proyek/modul; `balek` tanpa ekspresi ditolak; `jadi_json` menghasilkan `salah` untuk JSON invalid, sedangkan JSON `null` valid menjadi nilai null bahasa.
- **CI/CD:** permission workflow dirinci dan action pihak ketiga dipatok pada commit SHA. Workflow release manual meminta tag eksplisit agar tidak tanpa sengaja membangun ulang tag lama.
- **Contoh dan belajar:** tambah kalkulator `examples/kalkulator.cuk` dengan keyword kanonis `njir`/`kampret`, tangani input nonnumerik dan pembagian nol, serta tes CLI; indeks contoh menjelaskan dukungan target dan efek samping file/jaringan.
- **Parser dan diagnostik:** pesan kesalahan mencantumkan nama file, baris, kolom, potongan sumber, pointer, dan saran koreksi tanpa bahasa yang merendahkan; tes regresi mengunci format lokasi.
- **Termux/CLI:** sediakan `scripts/test-termux-device.sh` untuk menguji instalasi paket, shebang/executable, input interaktif, native C, dan kode keluar di perangkat nyata. Skrip ini harus dijalankan manual di perangkat; cross-build CI tidak dihitung sebagai uji perangkat.
- **CI/tata kelola:** jalankan regresi PVM secara otomatis pada workflow tes utama; metadata paket `0.8.0.dev0` tetap dibedakan dari kontrak bahasa `0.5-dev`. Perlindungan branch settings harus diverifikasi/diaktifkan pada pengaturan GitHub repo.
- **Built-in lintas-runtime:** tambah `logaritma` (natural log) dan `log10`; kontrak domain positif, aritas, Python reference, native C, tes unit, serta fixture sukses dan domain error kini dikunci.
- **DX:** menjalankan `pusingcuk` tanpa argumen masuk ke REPL terminal yang sudah ada; paket menampilkan versi terminal `0.5-dev`.
- **Editor dan kontributor:** tambahkan extension skeleton TextMate untuk VS Code, panduan kompatibilitas Acode, `README_EN.md`, dan contoh bot terminal yang bisa dijalankan.
- **Penanganan kesalahan:** tegaskan kontrak lokal `ketangkep nama` dan tambah regresi agar pesan exception dapat diperiksa tanpa menimpa variabel luar; native C tetap dinyatakan unsupported untuk try/catch.
- **Dokumentasi:** sinkronkan batas kompatibilitas, versi paket/bahasa, dan peringatan keamanan; contoh PusingCuk maupun bytecode tidak boleh dipresentasikan sebagai eksekusi yang terisolasi.

### Gate sebelum rilis

- Verifikasi status seluruh 25 built-in melalui `library/builtin_contract.json`; 17 didukung pada native C, 14 pada transpiler JS, 14 pada transpiler Python/HTML, dan 6 pada VM eksperimental.
- Jalankan `python -m pytest -q`, `make test`, serta workflow build Python dan native C. CI yang lulus hanya membuktikan cakupan pengujian yang dijalankan; tidak menutup risiko sandbox pada Issue #75.
