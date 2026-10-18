# Status Aktif dan Prioritas PusingCuk

**Branch yang dituju untuk pekerjaan ini:** `warungpusingcuk`  
**Versi kontrak bahasa:** `0.6-dev`  
**Versi paket Python:** `0.8.0.dev0`  
**Status:** eksperimental; ringkasan ini bukan bukti bahwa seluruh tes atau target deployment lulus. Audit ini tidak menyatakan bahasa stabil atau AI akurat secara umum.

**AI knowledge/retrieval baseline:** 26 dokumen sumber terkurasi; 22 kasus baseline menghasilkan top-1. Hasil retrieval terdokumentasi terpisah dan bukan bukti model dilatih sendiri.
**Retrieval baseline historis:** 5/8 (62,5%) dan 6/8 (75%) pada evaluasi yang dicatat; angka ini dipertahankan sebagai hasil historis, bukan klaim kualitas umum.

## Gambaran yang benar saat ini

**Konformansi saat ini:** 78 fixture: 78 wajib pada interpreter referensi Python, 75 wajib pada native C, dan 3 secara eksplisit tidak didukung native. Contoh aplikasi kasir warung tercakup sebagai tes wajib pada kedua runtime.

- **Bahasa:** lexer, parser, AST, interpreter referensi, spesifikasi, kontrak built-in, dan fixture tersedia. Jalur referensi masih bergantung pada Python.
- **Native C:** ada backend/runtime mandiri untuk sebagian bahasa. Fitur yang tidak tercakup dalam tes native belum boleh diklaim kompatibel.
- **Bytecode/VM:** ada compiler bytecode dan VM eksperimental. Ini belum sama dengan runtime native yang bebas dari Python.
- **JavaScript/Python/Android:** ada backend atau prototipe dengan cakupan masing-masing; keberadaan file tidak membuktikan parity atau aplikasi siap distribusi.
- **PusingCuk AI:** kode asisten dan tool compiler tersedia. Asisten membantu menghasilkan/memperbaiki .cuk, tetapi bukan foundation model yang dilatih sendiri dan tidak boleh mengklaim kode berjalan hanya karena model menghasilkannya.
- **Frontend/backend SaaS:** UI, layanan, dan integrasi yang ada harus diperlakukan sebagai prototipe sampai jalur build, autentikasi, API, dan runtime dibuktikan pada commit yang sama.

## Urutan prioritas

### P0 — Dokumentasi dan kontrak tunggal

1. Pertahankan README sebagai pengantar singkat dan `docs/README.md` sebagai indeks.
2. Gunakan `SPEC.md` untuk perilaku bahasa yang terlihat pengguna, `docs/SEMANTIC_CONTRACT.md` untuk semantik, dan `library/builtin_contract.json` untuk metadata built-in/dukungan target.
3. Jadikan audit bertanggal sebagai bukti historis, bukan status saat ini. Hindari salinan roadmap yang berbeda-beda.
4. Setiap klaim dukungan harus menunjuk implementasi dan tes/fixture target.

### P1 — Kurangi ketergantungan Python secara terukur

1. Jadikan AST/IR dan kontrak semantik tidak bergantung pada perilaku Python yang tidak disengaja.
2. Perluas native C berdasarkan celah yang dapat direproduksi, satu perilaku per perubahan; jangan hanya menambah nama built-in.
3. Untuk setiap celah: fixture positif/negatif → spesifikasi → implementasi target → tes konformansi.
4. Lengkapi koleksi, fungsi, diagnostik, dan built-in prioritas tinggi lintas reference/native sebelum menyatakan parity.
5. Ukur ukuran binary, waktu startup, memori, dan kebutuhan runtime agar klaim “ringan” punya dasar.
6. Pisahkan **kompilasi di mesin pengembang** dari **menjalankan hasil kompilasi**: target mandiri baru terbukti bebas Python ketika artefak dapat berjalan tanpa interpreter Python terpasang.

### P2 — Siklus PusingCuk AI → .cuk → bukti

1. Gunakan engine/tool PusingCuk yang sudah ada; jangan membuat jalur AI kedua yang tidak diperlukan.
2. AI mengusulkan program .cuk dan menjelaskan perubahan.
3. Compiler menghasilkan diagnostik yang terstruktur.
4. Tool konformansi menjalankan fixture terdaftar dan mengembalikan bukti per-runtime.
5. AI memperbaiki berdasarkan diagnostik nyata; hasil tetap berstatus belum terverifikasi sampai runtime yang diwajibkan lulus.
6. Tambahkan fixture baru hanya untuk celah semantik yang benar-benar direproduksi.

### P3 — Pemisahan aplikasi

- **Frontend:** tampilan, navigasi, input, validasi antarmuka.
- **Backend:** autentikasi, API, kebijakan akses, operasi layanan.
- **Runtime .cuk:** aturan deterministik dan perilaku bahasa.
- **Library:** fungsi umum dan adapter dengan kontrak jelas.
- **Platform bridge:** kemampuan perangkat/penyimpanan yang harus diberi izin eksplisit.

Jangan memindahkan aturan bisnis ke UI hanya untuk membuat prototipe tampak selesai.

## Bukti yang wajib sebelum menyatakan selesai

- Perubahan bahasa: tes yang relevan dan fixture reference/native.
- Backend compiler: tes backend dan fixture yang memang didukung.
- AI: tes tool dan alur compile/diagnostic/runtime; respons model saja bukan bukti.
- Web/SaaS: build, API, autentikasi, dan alur utama yang benar-benar dijalankan.
- Android/desktop: artefak berhasil dibangun dan diuji pada target nyata; file workflow atau APK lama tidak cukup.

## Batas keamanan

Runtime saat ini bukan sandbox OS yang menjamin eksekusi kode tak tepercaya aman. Jangan jalankan kode pengguna tak dikenal dengan hak akses pribadi. Jangan memasukkan kunci API, service-role key, atau kredensial ke source, dokumentasi, log, maupun prompt.

## Sumber kanonis

- [Visi](VISION.md)
- [Spesifikasi bahasa](../SPEC.md)
- [Kontrak semantik](SEMANTIC_CONTRACT.md)
- [Kompatibilitas target](COMPATIBILITY.md)
- [Kontrak built-in](../library/builtin_contract.json)
- [Indeks dokumentasi](README.md)

Dokumen audit bertanggal dan catatan integrasi lama dipertahankan hanya sebagai konteks historis sampai referensi masuknya diperiksa; jangan menganggap semua rekomendasi lama masih merupakan prioritas aktif.
