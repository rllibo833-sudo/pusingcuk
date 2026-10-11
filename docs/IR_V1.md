# Pusingcuk IR v1

Status: tersedia sebagai artefak front-end yang dapat dibuat dan divalidasi. Ini bukan backend compiler atau bytecode executable.

## Tujuan

Sediakan format JSON deterministik untuk memindahkan hasil parsing ke tool/backend lain tanpa membuat backend mengurai sintaks slang Pusingcuk. IR v1 mempertahankan struktur AST; versi berikutnya dapat memperkenalkan lowering ke instruksi setelah semantik lebih lengkap.

## Envelope

- format: pusingcuk-ir.
- ir_version: integer 1.
- language_version: versi semantik bahasa.
- source_name: nama file sumber, bukan path absolut.
- features: daftar fitur unik dan terurut.
- source_map: relasi path node ke nomor baris sumber.
- program: root node Program.

Node menggunakan field kind, line, dan fields. Field disusun deterministik. Nilai literal mempertahankan tipe JSON dan angka non-finite ditolak. Entri dictionary AST disimpan sebagai daftar pasangan agar tipe key tidak berubah menjadi nama properti JSON.

## Perintah

Buat artefak:

    python -m compiler.ir program.pusingcuk -o program.pcir.json

Validasi tanpa mengeksekusi:

    python -m compiler.ir --validate-ir program.pcir.json

Tanpa opsi -o, IR ditulis ke stdout. Kesalahan parsing, pembacaan, atau validasi menghasilkan exit code bukan nol.

## Kompatibilitas

Versi IR tidak boleh berubah diam-diam. Field envelope yang tidak dikenal, node yang tidak dikenal, versi tak didukung, source map duplikat, daftar fitur yang tidak konsisten, dan angka non-finite ditolak. Backend wajib memeriksa ir_version dan features, lalu menolak fitur yang belum dipahami. Artefak diperlakukan sebagai data, tidak dieksekusi sebagai Python atau shell.

IR v1 mempertahankan AST dan belum mendefinisikan ABI, layout memori, garbage collector, concurrency, atau modul. Kontrak semantik ada di SEMANTIC_CONTRACT.md; rancangan backend lintas target ada di COMPILER_INTEROP.md.

## Backend C eksperimental

Perintah python -m compiler.c_backend program.pusingcuk -o program.c menghasilkan source C11 untuk program yang hanya menggunakan deklarasi/assignment variabel integer, literal integer yang didukung, unary minus, operasi tambah/kurang/kali, dan output integer. Kompilasikan program.c dengan compiler C11 untuk membuat executable. Backend menolak fitur yang belum didukung; ia tidak menjalankan kode sumber dan tidak mengklaim parity penuh dengan interpreter. Lihat C_BACKEND.md untuk detail.
