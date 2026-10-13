# PusingCuk Bytecode IR — PVM v1

Status: draft implementasi; belum merupakan ABI stabil lintas versi.

## Format biner
Little-endian. Header enam byte: ASCII PVM1, diikuti versi u16 bernilai 1. Setiap record: opcode u8, payload_length u32, lalu payload UTF-8. Payload tidak memiliki terminator NUL. Reader wajib menolak header/versi salah, record terpotong, ukuran tak masuk akal, dan opcode tak dikenal. Assembler C membatasi payload 2048 byte; reader backend membatasi 1 MiB.

## 19 opcode
| Nilai | Opcode | Operand dan makna |
|---:|---|---|
| 1 | OP_HEDEH | Ekspresi yang dicetak ke stdout |
| 2 | OP_LAH | Deklarasi/assignment nama = ekspresi |
| 3 | OP_NJIR | Awal blok if; payload kondisi |
| 4 | OP_KAMPRET | Cabang else |
| 5 | OP_MUMET | Awal while; payload kondisi |
| 6 | OP_FOR | nama dalam iterable |
| 7 | OP_TANYA | nama = prompt; baca satu baris |
| 8 | OP_FUNGSI | Signature fungsi; dukungan belum lengkap |
| 9 | OP_BALEK | Ekspresi return |
| 10 | OP_BUKA | Buka file pada path |
| 11 | OP_NGINTIP | nama dari path untuk membaca file, atau path untuk mencetak isi |
| 12 | OP_CORET | Hapus file pada path |
| 13 | OP_TUTUP | Tutup blok njir/mumet/untuk atau file buka |
| 14 | OP_GEROMBOLAN | Evaluasi koleksi/list ke slot sementara |
| 15 | OP_PETIK | Evaluasi literal ke slot sementara |
| 16 | OP_CEMPLUNGIN | Tambah nilai ke list: nama_list, nilai |
| 17 | OP_PANJANG | Panjang ekspresi; bentuk assignment nama = ekspresi |
| 18 | OP_SENGGOL | Membaca payload lokal `data:text/plain,...`: `nama = payload` atau payload langsung; URL jaringan eksternal ditolak oleh backend JS/Python yang telah diperkeras |
| 19 | OP_BEDAH | Cetak representasi JSON ekspresi |

## Semantik dan portabilitas
Operand v1 adalah teks sumber UTF-8. Ekspresi portabel dibatasi pada literal string/angka, boolean benar/salah, nama, list, aritmetika, perbandingan, dan logika dan/atau/bukan. Backend menerjemahkan subset ini ke sintaks target. selesai jancuk tidak menghasilkan instruksi; penutup blok lain menghasilkan OP_TUTUP. AST assembler saat ini berupa daftar node instruksi dari parser baris, bukan AST ekspresi lengkap.

Untuk Android Termux, jangan menulis struct C mentah ke file karena padding dan endianness. Operasi file PVM tidak menerima path absolut atau ekspansi `~/`; berkas harus berada relatif terhadap direktori proyek saat proses runtime dimulai.

## Batasan saat ini
OP_FUNGSI dan semantik file handle lintas backend belum lengkap. Kesetaraan seluruh sintaks PusingCuk belum dijamin. OP_SENGGOL tidak boleh membuat koneksi jaringan. Backend JavaScript/Python hanya menerima payload lokal `data:text/plain,...` dan menolak URL eksternal. Fitur ini bukan HTTP client. Operasi file PVM berada di luar kontrak bahasa stabil.


## Filesystem confinement

### Python backend

File opcodes `OP_BUKA`, `OP_NGINTIP`, dan `OP_CORET` **ditolak secara default**. Untuk bytecode yang memang dipercaya, operator harus memberikan kapabilitas eksplisit pada saat runtime:

```sh
python3 generated_program.py --allow-file-io
```

Pada POSIX yang mendukung `openat`/`dir_fd`, `O_NOFOLLOW`, dan `O_DIRECTORY`, runtime membuka direktori proyek sebagai file descriptor tetap lalu menuruni setiap komponen relatif dengan descriptor tersebut. File final dibuka dengan `O_NOFOLLOW`; penghapusan dilakukan relatif terhadap descriptor direktori yang sudah terbuka. Path absolut, drive Windows, `..`, dan symlink ditolak. Perubahan current working directory setelah runtime dimulai tidak mengalihkan root descriptor.

Jika primitive OS itu tidak tersedia, operasi file tetap ditolak. Ini memperkuat batas path aplikasi tetapi **bukan sandbox OS umum**: program tepercaya yang diberi kapabilitas masih berjalan dengan hak akses proses untuk kemampuan lain yang tersedia di runtime.

### JavaScript backend

Opcode file (`OP_BUKA`, `OP_NGINTIP`, `OP_CORET`) secara sengaja gagal dengan pesan bahwa operasi tersebut dinonaktifkan. Backend JS tidak menawarkan flag untuk membuka kembali file I/O karena ia belum memiliki implementasi portabel yang tahan terhadap symlink race dengan descriptor relatif ke root.

### Cakupan jaminan

PVM masih draft dan bukan ABI stabil. Parser, resource limits, dan pembatasan path tidak membuat bytecode tak tepercaya aman. Jangan menjalankannya di perangkat berisi file sensitif atau kredensial. Issue #75 tetap terbuka sampai review independen menyatakan kriteria keamanan yang tersisa terpenuhi.
