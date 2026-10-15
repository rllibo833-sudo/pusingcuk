# PusingCuk Accounting — aplikasi belajar akuntansi

MVP desktop offline untuk latihan akuntansi berbahasa Indonesia. Sumber aplikasi berada di apps/accounting/; contoh bahasa PusingCuk berada di examples/accounting/.

## Fitur MVP
- Jurnal umum yang dapat diedit: tanggal, keterangan, akun, kategori, debit, kredit.
- Ringkasan buku besar dan neraca saldo, laba rugi, serta posisi keuangan dasar.
- Format Rupiah Indonesia (id-ID, IDR), penyimpanan lokal, ekspor CSV.
- Tidak membutuhkan jaringan untuk fungsi lokal.

## Build Windows
Dari direktori apps/accounting jalankan npm install lalu npm run dist:win. Untuk membangun di GitHub, buka Actions dan jalankan workflow Build Accounting Windows EXE. Setelah sukses, unduh artefak PusingCuk-Accounting-Windows dari halaman run; artefak disimpan selama 14 hari.

## Rumus dan batasan
Saldo normal aset/beban = debit - kredit. Saldo normal liabilitas/ekuitas/pendapatan = kredit - debit. Laba/rugi = pendapatan - beban. Persamaan dasar posisi keuangan: aset = liabilitas + ekuitas + hasil periode, dengan memperhatikan kebijakan penutupan periode.

Ini alat belajar MVP, bukan software akuntansi tersertifikasi. Validasi debit-kredit total saja tidak menjamin setiap transaksi seimbang atau klasifikasi akun benar. Belum mencakup semua SAK/PSAK, jurnal penyesuaian otomatis, persediaan multi-metode, depresiasi, konsolidasi, pajak kompleks, multi-periode, mata uang asing, atau audit trail. PusingCuk AI online belum diaktifkan; jangan kirim data transaksi ke layanan eksternal sebelum autentikasi, backend, persetujuan, dan perlindungan data dikonfigurasi. Offline tidak memerlukan login.
