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

Untuk Android Termux, jangan menulis struct C mentah ke file karena padding dan endianness. Path ~/... pada OP_BUKA diselesaikan memakai HOME; jika kosong, fallback adalah /data/data/com.termux/files/home. Path absolut tersebut dipertahankan.

## Batasan saat ini
OP_FUNGSI dan semantik file handle lintas backend belum lengkap. Kesetaraan seluruh sintaks PusingCuk belum dijamin. OP_SENGGOL tidak boleh membuat koneksi jaringan. Backend JavaScript/Python yang telah diperkeras hanya menerima payload lokal `data:text/plain,...` dan menolak URL eksternal. Fitur ini bukan HTTP client. Jangan jalankan bytecode tak tepercaya: opcode file masih dapat membaca atau menghapus file yang bisa diakses proses, karena belum ada pembatasan sandbox sistem operasi.
