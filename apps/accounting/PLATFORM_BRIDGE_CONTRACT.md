# Kontrak Bridge Platform CukAccount v1

Status: kontrak teknis untuk implementasi bertahap; bukan klaim bahwa adapter native sudah tersedia.

## Batas arsitektur

- Frontend .cuk mengelola rute, state tampilan, validasi interaksi, tema, dan pesan hasil.
- Backend .cuk memiliki aturan akuntansi/domain. UI tidak boleh menghitung saldo atau memutuskan posting sendiri.
- Runtime host menerjemahkan perintah bridge bertipe ke SQLite/Android. Bridge tidak menerima SQL mentah dari model AI atau kode .cuk arbitrer.
- Aturan bisnis tidak boleh dipindah kembali ke Dart. Host Dart/Android, bila masih dipakai, hanya menjalankan kemampuan platform yang diizinkan.
- Semua operasi tulis keuangan wajib melalui use case transaksional yang memvalidasi periode, akun, debit/kredit, idempotensi, dan audit event.

## Envelope permintaan/respons

Permintaan: contract_version, request_id, operation, input.
Respons: contract_version, request_id, status, result atau diagnostic.
Versi saat ini: cukaccount.platform.v1.

Operasi yang direncanakan:
- db.query_accounts — baca akun aktif, hasil terstruktur.
- db.save_journal_draft — simpan draft saja; tidak mem-posting.
- db.post_journal — transaksi atomik, idempotency key wajib, periode terbuka dan jurnal seimbang wajib.
- db.get_general_ledger — buku besar per akun dengan saldo berjalan.
- db.close_period — rencana tutup dan validasi prasyarat; posting penutupan hanya melalui use case teruji.
- secure_store.get_key_metadata — metadata kunci saja; jangan kembalikan kunci mentah ke .cuk.
- backup.export / backup.restore — harus memakai format berversi, validasi integritas, dan uji pemulihan sebelum dinyatakan aktif.

## Keamanan dan konsistensi

1. Tolak operasi yang tidak dikenal, input tak sesuai skema, ukuran berlebih, dan versi kontrak tak didukung.
2. Jangan log isi jurnal, kredensial, kunci, atau data finansial sensitif.
3. Backup belum boleh disebut terenkripsi sampai implementasi enkripsi dan pengujian pemulihan lulus.
4. Restore harus memvalidasi file sebelum mengganti database; kegagalan tidak boleh meninggalkan database setengah tertulis.
5. Setiap operasi tulis menghasilkan audit event yang terikat ke transaksi database.
6. Jalur AI hanya boleh menghasilkan diagnostik atau patch kode; tidak memiliki capability untuk mengubah database pembukuan pengguna.

## Gerbang implementasi

Kontrak ini belum menjadi bridge aktif. Setiap operasi harus memiliki adapter, tes unit, tes SQLite/integrasi, tes kegagalan, dan bukti CI sebelum dinyatakan selesai.
