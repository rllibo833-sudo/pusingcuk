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

## Deployment lokal: Android + Termux + Ollama

Target penggunaan lokal adalah satu perangkat Android milik pengguna:

- Jalankan Ollama dan PusingCuk tooling dari Termux pada perangkat yang sama; arahkan provider ke endpoint loopback lokal, bukan alamat LAN atau internet.
- Jangan menyimpan API key cloud sebagai prasyarat untuk mode lokal. Jika Ollama tidak tersedia, proses harus gagal dengan diagnostik yang jelas, bukan beralih diam-diam ke provider jarak jauh.
- Data Center/evolution tooling hanya menghasilkan proposal dan laporan. Perubahan kosakata, parser, fixture, atau sumber bahasa tidak boleh ditulis otomatis; tidak boleh ada `git commit`/`git push` otomatis.
- Tinjau proposal, jalankan Reality Engine dan fixture, lalu lakukan commit secara eksplisit setelah hasilnya diperiksa.
- SQLite, HTTP loopback, dan Web3 mock di dokumen ini masih merupakan adapter host Python. API `.cuk` lintas-target yang sama pada interpreter reference dan native C **belum tersedia**; jangan gunakan contoh Python sebagai bukti bahwa program `.cuk` sudah bisa memanggil adapter.
- Verifikasi di perangkat fisik tetap diperlukan: jalankan `bash scripts/test-termux-device.sh` di Termux dan simpan hasilnya bersama versi Android, Termux, Python, compiler C, serta Ollama yang digunakan.
## Batas keamanan

Fitur ini bukan sandbox untuk kode tak tepercaya. Jangan jalankan program asing dengan akun yang menyimpan kredensial atau file penting. Server lokal masih dapat diakses proses lain pada perangkat yang sama; tambahkan autentikasi dan isolasi OS sebelum pemakaian sensitif. API adapter Python ini belum terhubung sebagai builtin Pusingcuk dan bukan klaim kesiapan produksi.
