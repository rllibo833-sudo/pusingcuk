# Pusingcuk IR v1

Status: kontrak AST-preserving berversi dengan validasi struktur dan batas sumber daya. IR bukan bytecode executable.

## Envelope wajib

- `format`: string tetap `pusingcuk-ir`.
- `ir_version`: integer 1; versi tidak dikenal ditolak.
- `language_version`: versi semantik Pusingcuk.
- `source_name`: nama file saja, bukan path absolut/relatif.
- `features`: daftar nama fitur nonkosong, unik dan terurut, dihitung dari AST.
- `source_map`: daftar `{path, line}` yang harus cocok persis dengan setiap node AST.
- `program`: root node `Program`.

Setiap node hanya boleh memiliki `kind`, `line`, dan `fields`. Jenis node dan himpunan field wajib divalidasi berdasarkan kontrak v1. Nilai dictionary AST direpresentasikan sebagai pasangan berurutan agar tipe kunci tidak berubah menjadi nama properti JSON.

## Batas input validator

IR eksternal diperlakukan sebagai data tidak tepercaya. Validator menolak:
- dokumen JSON lebih besar dari 8 MiB;
- kedalaman struktur lebih dari 128;
- lebih dari 100.000 node, item koleksi, atau entri source map;
- string lebih dari 1.000.000 karakter;
- nilai angka non-finite, tipe JSON tak didukung, field node/envelope yang hilang atau tak dikenal;
- source map duplikat atau tidak cocok dengan AST;
- daftar fitur yang tidak konsisten atau versi IR tak didukung.

Batas ini melindungi parsing dan validasi artefak, bukan sandbox untuk program hasil kompilasi. Perubahan batas memerlukan perubahan kontrak dan tes kompatibilitas yang disengaja.

## Perintah

Buat IR:

    python -m compiler.ir program.pusingcuk -o program.pcir.json

Validasi tanpa mengeksekusi:

    python -m compiler.ir --validate-ir program.pcir.json

Tanpa `-o`, IR ditulis ke stdout. Kesalahan parsing, pembacaan, ukuran, atau validasi menghasilkan exit code bukan nol.

## Determinisme dan kompatibilitas

Serialisasi menggunakan UTF-8, urutan kunci deterministik, dan newline akhir. Mengurai lalu menserialisasi ulang IR valid harus menghasilkan byte yang sama. Backend harus memeriksa `ir_version` dan semua fitur yang dipakai; fitur yang belum didukung harus ditolak dengan diagnostik, bukan ditebak.

Perubahan breaking pada bentuk node atau semantiknya memerlukan versi IR baru atau aturan migrasi eksplisit. IR v1 tidak mendefinisikan ABI, layout memori, garbage collector, concurrency, atau sistem modul.
