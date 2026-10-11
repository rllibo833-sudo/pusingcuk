# Audit Native Pusingcuk — 2026-10-12

**Status:** Audit berbasis sumber GitHub; bukan sertifikasi keamanan atau bukti kesetaraan penuh seluruh bahasa. Dokumen ini diperbarui terhadap `main` setelah temuan historis diperiksa ulang.

## Ringkasan arsitektur

| Komponen | Peran | Batas penting |
|---|---|---|
| Pipeline Python | Implementasi referensi lexer/parser/AST/evaluator dan CLI | Memerlukan Python |
| Runtime C native | Menjalankan subset bahasa secara langsung tanpa Python | Belum mendukung seluruh bahasa; batas fitur harus mengikuti matriks runtime dan fixture |
| IR v1 dan backend C | IR mempertahankan struktur AST dalam format JSON berversi; backend C menghasilkan C untuk subset terbatas | IR bukan bytecode; backend tetap eksperimental |

Pernyataan yang aman: **Pusingcuk adalah bahasa eksperimental dengan pipeline referensi Python, runtime C mandiri untuk subset teruji, IR AST berversi, dan backend code generation C eksperimental.** Jangan menyebutnya compiler native umum yang lengkap.

## Pemeriksaan ulang temuan historis

### Short-circuit operator `dan` / `atau`

Laporan sebelumnya menyatakan runtime native mengevaluasi operand kanan lebih awal dan melanggar short-circuit. Pada `main`, implementasi kini memiliki mekanisme `suppress_eval` dan komentar yang menyatakan operand logis yang dilewati diparse tanpa efek runtime. Karena itu, temuan lama **tidak boleh lagi dicatat sebagai bug yang masih terbukti ada**.

Kontrak semantik tetap mensyaratkan:
- `salah dan variabel_yang_belum_ada` menghasilkan salah tanpa lookup variabel yang dilewati.
- `benar atau variabel_yang_belum_ada` menghasilkan benar tanpa lookup variabel yang dilewati.
- Operand yang dilewati tetap harus diparse agar kesalahan sintaks tetap terdeteksi.

**Status:** perbaikan terlihat pada kode sumber `main`; hasil uji aktual harus dikonfirmasi melalui fixture konformansi dan CI pada commit terbaru. Issue historis: https://github.com/rllibo833-sudo/pusingcuk/issues/44

### Kesetaraan list

Laporan sebelumnya menyatakan list native hanya dibandingkan berdasarkan identitas pointer. Pada `main`, fungsi `equal_depth` kini membandingkan elemen list secara rekursif, membatasi kedalaman perbandingan untuk melindungi stack, dan tetap menerima list yang sama berdasarkan identitas.

**Status:** implementasi kesetaraan struktural terlihat pada kode sumber `main`; konformansi penuh untuk list bersarang dan perbedaan tipe masih harus ditetapkan oleh fixture. Kamus tetap berbasis identitas objek menurut kontrak semantik saat ini. Issue historis: https://github.com/rllibo833-sudo/pusingcuk/issues/46

## Batas dan risiko yang masih perlu diuji

- Kelulusan tes hanya membuktikan perilaku yang tercakup oleh tes; bukan bukti keamanan atau paritas penuh.
- Build APK Android tidak membuktikan jalur eksekusi telah diuji pada perangkat Android/Termux nyata.
- Batas kapasitas koleksi, ukuran teks, kedalaman fungsi/rekursi, indeks, rentang, dan dukungan Unicode harus konsisten antara implementasi, spesifikasi, serta fixture.
- Kesalahan harus memiliki exit code bukan nol dan diagnostik ke stderr; teks pesan penuh hanya menjadi kontrak jika dikunci fixture.
- Alias slang harus dinormalisasi ke token kanonis. Jangan menambah alias hanya demi tren.
- Runtime native bukan sandbox. Akses filesystem, jaringan, database, proses, dan rahasia harus berupa kapabilitas eksplisit dengan izin minimum.
- Perilaku operator, precedence, scope, return, nilai numerik, error malformed input, dan perbedaan kesetaraan harus diuji lintas runtime.

## Prioritas berikutnya

1. Jalankan suite unit dan konformansi Python/native terhadap `main`; pastikan kasus short-circuit dan kesetaraan list mencakup hasil positif serta negatif.
2. Tambahkan fixture lintas-runtime untuk precedence operator, syntax error, scope fungsi, return, batas resource, rentang/nilai numerik, UTF-8, dan exit code.
3. Perlakukan hasil `UNSUPPORTED` sebagai batas yang terdokumentasi, bukan sebagai PASS.
4. Perbarui matriks runtime dan dokumentasi hanya berdasarkan bukti fixture/CI yang dapat diulang.
5. Verifikasi eksekusi native di perangkat Termux fisik dan jalur eksekusi aplikasi Android, bukan hanya keberhasilan build.
6. Jangan mengganti komponen CORE hanya karena binary native berhasil dibangun. Wajib ada matriks kapabilitas, fixture yang diwajibkan, kontrak integrasi, tinjauan keamanan untuk kapabilitas yang digunakan, build yang dapat direproduksi, bukti rollback, dan persetujuan Founder.

## Arah produk bahasa

Targetnya **mudah dipelajari, cukup serius untuk berkembang**:
- Pemula: Bahasa Indonesia yang jelas, contoh kecil, hasil yang diharapkan, dan satu konsep per pelajaran.
- Builder: CLI yang konsisten, contoh, test runner, serta formatter/linter secara bertahap.
- Ahli: spesifikasi formal, semantik deterministik, IR berversi, kapabilitas runtime eksplisit, dan backend yang dapat diuji.
- Gaya Gen Z/Gen Alpha bersifat opsional; jangan memaksa slang atau membuat pesan error bergantung pada meme yang cepat usang.

## Kriteria penerimaan perubahan bahasa

Setiap fitur baru harus disertai spesifikasi atau dokumentasi perilaku, fixture sukses dan gagal, pengujian runtime yang mengklaim mendukungnya, serta perubahan kecil yang dapat ditinjau. Gunakan PR terpisah, CI hijau pada commit yang tepat, dan jangan gabungkan branch lama secara keseluruhan hanya untuk mengambil satu dokumen atau fitur.
