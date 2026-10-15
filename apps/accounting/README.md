# PusingCuk Accounting (MVP)

Aplikasi desktop edukasi akuntansi berbahasa Indonesia dengan jurnal umum, ringkasan buku besar, neraca saldo, laba rugi, dan posisi keuangan dasar. Nominal diformat sebagai Rupiah Indonesia (IDR).

## Menjalankan
Memerlukan Node.js 20+ untuk membangun dari sumber.

    npm install
    npm start

## Membuat EXE Windows

    npm run dist:win

Atau buka GitHub Actions pada repo PusingCuk dan jalankan workflow **Build Accounting Windows EXE**. Setelah workflow sukses, unduh artefak **PusingCuk-Accounting-Windows** dari halaman run tersebut. Artefak workflow bersifat sementara (14 hari), bukan rilis permanen.

## Status fitur
- Jurnal lokal dan penyimpanan otomatis pada profil aplikasi/browser.
- Debit/kredit, saldo akun, neraca saldo, laba rugi dan posisi keuangan sederhana.
- Ekspor jurnal ke CSV.
- Offline-first; tidak ada login untuk fungsi lokal.
- Login dan PusingCuk AI online belum terhubung.

## Batasan akuntansi
Ini prototipe belajar, bukan sistem pembukuan produksi. Kategori akun dipilih pengguna dan rumus laporan masih dasar. Belum ada validasi setiap transaksi sebagai satu grup jurnal, periode akuntansi, jurnal penyesuaian/penutup, pajak, persediaan, penyusutan, multi-mata-uang, audit trail, atau pengujian kesesuaian SAK/PSAK. Periksa hasil dengan dosen/akuntan sebelum digunakan untuk keputusan nyata.
