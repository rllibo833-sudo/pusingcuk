# CukAccount — contoh target aplikasi untuk PusingCuk

Dokumen ini mengikat tujuan CukAccount dengan pengembangan bahasa .cuk, compiler, dan PusingCuk AI. Spesifikasi produk tetap berada di [CUKACCOUNT_SPEC_AND_ROADMAP.md](https://github.com/rllibo833-sudo/Cukaccount/blob/main/CUKACCOUNT_SPEC_AND_ROADMAP.md). Perubahan implementasi bahasa, contoh, rule, dan compiler untuk tujuan ini dikerjakan di repositori **PusingCuk**.

## Hasil yang dituju

Bangun aplikasi Android **CukAccount**, bukan terminal atau editor kode. Pengguna membuka aplikasi akuntansi offline dengan navigasi dan formulir bisnis. UI memiliki dua mode yang memakai mesin aturan bisnis yang sama:

- **Mode normal:** Beranda, transaksi/jurnal, akun, periode, dan laporan dengan istilah sederhana, alur terpandu, ringkasan saldo, validasi yang jelas, dan tombol tindakan utama yang mudah ditemukan.
- **Mode profesional:** akses ke rincian jurnal, buku besar dan saldo berjalan, neraca saldo, penyesuaian/koreksi, kontrol periode dan audit trail, klasifikasi arus kas/ekuitas, serta rincian laporan. Mode ini menampilkan kontrol lebih lengkap; validasi tetap sama ketatnya.

Pengguna dapat berpindah mode tanpa membuat salinan data atau mengubah aturan pembukuan. Tema terang/gelap dan pesan UI berbahasa Indonesia harus konsisten.

## Kontrak akuntansi yang tidak boleh dilanggar

1. Fungsi inti berjalan offline; penyimpanan lokal harus persisten setelah aplikasi ditutup dan dibuka kembali.
2. Uang disimpan dan dihitung dengan representasi eksak (integer satuan terkecil yang ditentukan mata uang atau tipe desimal eksak yang teruji), bukan floating point untuk posting/laporan. Jangan memotong angka besar atau mengonversi Rupiah melalui tipe double.
3. Jurnal yang diposting minimal memiliki dua baris; akun harus valid/aktif; periode harus terbuka; total debit harus sama dengan total kredit.
4. Posting, perubahan saldo, dan audit event harus konsisten dalam satu transaksi penyimpanan. Jurnal terposting tidak diedit atau dihapus diam-diam; gunakan koreksi/pembalik dengan jejak audit.
5. Buku besar, neraca saldo, laba rugi, posisi keuangan, arus kas, dan perubahan ekuitas dihitung dari jurnal terposting dan harus dapat direkonsiliasi. Klasifikasi arus kas/ekuitas harus eksplisit, bukan ditebak dari nama akun.
6. Penutupan periode harus benar-benar mem-posting hasil penutupan yang diperlukan, mengunci periode, dan menjaga audit trail. Rencana penutupan saja bukan penutupan.
7. Pajak Indonesia dan akuntansi syariah hanya boleh dinyatakan didukung jika aturan, sumber, tanggal efektif, perlakuan, dan fixture hasilnya telah diverifikasi. Jangan mengarang tarif atau klaim kepatuhan.
8. Data contoh dan fixture publik harus sintetis; jangan masukkan data pelanggan nyata atau rahasia.

## Pembagian kerja .cuk, PusingCuk AI, dan aplikasi

- **Bahasa/compiler .cuk:** sediakan sintaks, tipe, validasi, diagnostik, serta target compiler yang dibutuhkan oleh modul bisnis dan UI CukAccount. Tambahkan kemampuan hanya dengan kontrak semantik dan contoh yang dapat dijalankan.
- **Rule .cuk:** tempatkan keputusan deterministik yang kecil dan dapat diuji, misalnya validasi keseimbangan jurnal, persamaan akuntansi, klasifikasi laporan eksplisit, dan prasyarat penutupan periode.
- **PusingCuk AI:** membantu memahami kebutuhan, menjelaskan diagnostik compiler, menyarankan perbaikan source/rule, dan mengarahkan ke tool yang diizinkan. Hasil AI tetap saran sampai divalidasi compiler dan fixture; AI tidak boleh langsung mengubah buku, mem-posting jurnal, atau melewati validasi.
- **Runtime dan penyimpanan aplikasi:** database lokal, posting jurnal, kontrol periode, laporan, backup/pemulihan, dan keamanan harus benar-benar diimplementasikan serta diuji. Rule yang lulus sendiri bukan bukti bahwa transaksi database aman.
- **Integrasi:** setiap contoh/rule memiliki input sintetis, expected output yang dikunci, serta hubungan yang jelas ke kasus domain aplikasi. Pin versi/commit PusingCuk yang digunakan dalam integrasi; jangan mengandalkan branch yang bergerak.

## Contoh bahasa yang sudah ada

[examples/accounting/report_equation.cuk](../../examples/accounting/report_equation.cuk) adalah contoh sintetis yang menghitung laba dan memeriksa persamaan dasar akuntansi. Outputnya hanya membuktikan contoh persamaan tersebut—bukan UI Android, database, posting jurnal, seluruh laporan, atau aplikasi CukAccount lengkap.

Contoh keluaran saat data seimbang:

~~~text
CUKACCOUNT_REPORT_EQUATION_BALANCED
~~~

Contoh ini merupakan titik awal untuk menambah fixture yang terpisah dan fokus. Jangan memperluas satu contoh kecil menjadi klaim bahwa seluruh aturan akuntansi telah tercakup.

## Urutan implementasi yang menghasilkan bukti nyata

1. **Kontrak dan fixture:** tambah kasus sintetis jurnal seimbang/tidak seimbang, akun tidak valid/nonaktif, periode tertutup, nominal nol/negatif/batas besar, klasifikasi arus kas eksplisit, serta expected output yang tepat.
2. **Bahasa dan AI:** pastikan rule terdaftar dengan skema input ketat, diagnostik yang berguna, dan tes regresi. Evaluasi PusingCuk AI dengan hasil yang dapat diukur; jangan menyebutnya fine-tuning bobot model tanpa pipeline teruji.
3. **Backend aplikasi Android:** hasilkan aplikasi bisnis dengan navigasi dan formulir CukAccount, serta mode normal/profesional yang benar-benar dapat dipilih. Targetnya aplikasi terpasang, bukan terminal, editor, atau demo formulir generik.
4. **Data dan domain:** sambungkan formulir ke penyimpanan offline dan use case akuntansi yang tervalidasi; pastikan data tetap ada setelah restart dan laporan bersumber dari jurnal terposting.
5. **Laporan dan penutupan:** rekonsiliasi semua laporan dengan fixture yang dihitung independen; uji penutupan, koreksi, dan audit trail.
6. **Penerimaan APK:** build hanya setelah perubahan cukup siap; verifikasi artifact, instalasi, startup, mode normal/profesional, alur jurnal, laporan, offline, dan pemulihan pada perangkat Android nyata.

## Definisi selesai

Sebuah langkah baru boleh disebut selesai jika source/rule/compiler yang relevan benar-benar berubah, pemeriksaan yang tersedia lulus, dan hasil yang dijanjikan telah dibuktikan. Dokumentasi, mockup, fixture tunggal, respons AI, atau APK yang hanya berhasil dibangun tidak sendirian membuktikan aplikasi akuntansi selesai. Catat dengan jujur apa yang berjalan, apa yang diuji, dan apa yang masih belum tersedia.
