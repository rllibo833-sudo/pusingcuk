# Adapter Lokal Pusingcuk

Status: fondasi host-side untuk pengembangan dan pengujian offline. Adapter ini belum menjadi modul yang dapat diimpor langsung dari sintaks Pusingcuk.

## Sistem modul

Compiler CLI menerima impor eksplisit:

    jancuk
    pakai "lib/angka.pusingcuk" sebagai angka
    hedeh angka.tambah(20, 22)
    selesai jancuk

Modul mendeklarasikan ekspor yang boleh dipakai:

    jancuk
    ekspor fungsi tambah
    fungsi tambah(a, b)
        balek a + b
    selesai fungsi
    selesai jancuk

Resolver hanya membaca file .pusingcuk lokal, membatasi jalur pada folder proyek, menolak siklus, dan membatasi ukuran/jumlah/kedalaman modul. Import tidak mengunduh paket dan tidak membuat sandbox. Tahap pertama ini dipasang pada compiler multi-target; runtime native C dan interpreter langsung belum mendukung sintaks impor.

## Database lokal

library.adapters.LocalDatabase(workspace) memakai SQLite di folder proyek. Gunakan parameter SQL, bukan menggabungkan input pengguna ke string SQL. Adapter menolak ATTACH/DETACH, PRAGMA, virtual tables, dan fungsi file/ekstensi SQLite. Database tetap data lokal; backup dan enkripsi disk adalah tanggung jawab aplikasi/OS.

## Server lokal

library.adapters.LocalHTTPServer(routes) mengikat hanya ke alamat IP loopback literal (contohnya 127.0.0.1), memproses JSON dengan batas ukuran, dan tidak mengirim traceback ke klien. Ini untuk demo, pengembangan, dan tes offline — bukan server produksi atau kontrol autentikasi.

## Web3 / blockchain

MockBlockchain menyediakan saldo dan transfer deterministik tanpa jaringan, kunci privat, atau transaksi nyata. LocalDevJsonRpc hanya menerima endpoint HTTP pada IP loopback literal, membatasi waktu/ukuran respons, dan menolak redirect. Gunakan node pengembangan lokal; belum ada adapter mainnet, wallet, penandatanganan, atau penyimpanan kunci.

## Batas keamanan

Fitur ini bukan sandbox untuk kode tak tepercaya. Jangan jalankan program asing dengan akun yang menyimpan kredensial atau file penting. Server lokal masih dapat diakses proses lain pada perangkat yang sama; tambahkan autentikasi dan isolasi OS sebelum pemakaian sensitif. API adapter Python ini belum terhubung sebagai builtin Pusingcuk dan bukan klaim kesiapan produksi.
