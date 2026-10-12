# Kompatibilitas Pusingcuk

Dokumen ini menetapkan sasaran kompatibilitas, bukan klaim bahwa seluruh sasaran sudah tercapai. Pusingcuk masih eksperimental dan dua runtime yang ada belum sepenuhnya setara.

## Sasaran desain

Pusingcuk harus mudah dimulai oleh pemula, tetap dapat dipakai untuk proyek serius, dan tidak mengunci pengguna pada satu sistem operasi atau satu implementasi runtime.

1. **Sumber yang portabel.** Berkas program menggunakan UTF-8 dan ekstensi `.pusingcuk`. Program yang hanya memakai fitur bahasa inti dan API standar yang terdokumentasi seharusnya tidak bergantung pada lokasi instalasi atau OS tertentu.
2. **Kontrak bahasa yang stabil.** Sintaks, nilai, operator, aturan scope, perilaku error, dan semantik built-in ditentukan oleh spesifikasi dan tes konformansi, bukan oleh kebetulan implementasi.
3. **Runtime yang dapat dipilih.** Interpreter referensi Python membantu pengembangan; runtime native C memungkinkan eksekusi tanpa Python setelah dibangun. Fitur hanya portabel lintas runtime jika kedua implementasi telah lulus tes yang sama.
4. **CLI yang konsisten.** Perintah menjalankan program harus memberi kode keluar nol saat berhasil, kode bukan nol saat gagal, pesan error ke stderr, dan tidak mencetak diagnostik internal saat mode normal. Perilaku CLI yang belum seragam perlu diperbaiki sebelum dinyatakan sebagai kontrak stabil.
5. **Dependensi eksplisit.** File, jaringan, database, lingkungan proses, dan kemampuan OS harus disediakan lewat API yang terdokumentasi. Jangan mengandalkan akses implisit atau efek samping khusus OS.
6. **Kompatibilitas ke depan.** Perubahan yang mematahkan sintaks atau semantik perlu dicatat dalam changelog dan versi; alias lama tidak boleh dihapus tanpa kebijakan deprekasi yang jelas.

## Status kompatibilitas saat ini

| Area | Status sekarang | Makna praktis |
|---|---|---|
| Linux dengan compiler C11 | Jalur native diuji di CI Ubuntu GCC/Clang | Bukan bukti otomatis untuk semua distro |
| Android melalui Termux | Ada skrip instalasi dan panduan | Pengujian perangkat fisik masih perlu dilakukan |
| Windows / macOS | Belum menjadi target native yang terverifikasi | Jangan menjanjikan kompatibilitas native sebelum ada CI dan tes platform |
| Interpreter Python | Unit test berjalan pada Python 3.11 dan 3.12 di CI | Ini jalur referensi pengembangan, bukan runtime mandiri |
| Runtime native C | Subset yang diuji tercatat di [matriks runtime](NATIVE_RUNTIME.md) | Jangan mengasumsikan semua fitur interpreter Python tersedia |
| Modul dan paket | Belum tersedia penuh pada native | Impor modul bukan kontrak portabel saat ini |
| UTF-8 | Berkas sumber dibaca sebagai teks UTF-8 pada CLI Python; native menangani sebagian operasi UTF-8 | Validasi UTF-8 penuh, normalisasi, dan semantik Unicode lintas runtime belum dijamin |
| File, jaringan, database | Belum ada pustaka standar lintas runtime yang lengkap | Gunakan hanya API yang secara eksplisit tersedia pada runtime target |
| Keamanan kode tak tepercaya | Tidak ada sandbox yang dijamin | Jangan menjalankan program tak tepercaya dengan hak akses penting |

## Compiler dan interoperabilitas

Pusingcuk dirancang agar dapat memiliki beberapa backend tanpa mengubah semantik bahasa. Lihat [arsitektur compiler dan interoperabilitas](COMPILER_INTEROP.md) untuk pipeline front-end → AST → analisis semantik → IR berversi → backend, serta batas rancangan ABI/FFI. Lihat [kontrak fixture konformansi](CONFORMANCE_FIXTURES.md) untuk format tes yang akan dipakai lintas runtime.

IR v1 tersedia sebagai format AST-preserving yang tervalidasi, tetapi bukan ABI stabil. CLI compiler memiliki target eksperimental JavaScript, Python, HTML, JSON IR, dan VM JSON; cakupan tiap target berbeda dan belum menjamin kesetaraan penuh. Backend C terpisah hanya mendukung subset integer yang terdokumentasi. Backend WebAssembly dan ABI/FFI stabil **belum tersedia**. Backend baru hanya dapat diklaim kompatibel setelah lulus fixture yang sama untuk fitur yang dinyatakan didukung.

## Tingkat kompatibilitas fitur

- **Inti teruji lintas runtime:** boleh disebut portabel hanya jika fixture yang sama lulus pada interpreter referensi dan runtime native.
- **Native teruji:** boleh digunakan pada native sesuai matriks, tetapi belum tentu tersedia pada interpreter referensi dengan semantik identik.
- **Referensi saja:** tersedia pada interpreter modular, tetapi belum menjadi bagian dari runtime native.
- **Eksperimental:** perilaku dapat berubah; jangan menjadikannya kontrak paket publik tanpa mengunci versi.

Status harus ditulis per fitur. Label umum seperti “kompatibel dengan Python”, “kompatibel dengan JavaScript”, atau “berjalan di semua OS” tidak boleh digunakan tanpa definisi dan tes konkret.

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
