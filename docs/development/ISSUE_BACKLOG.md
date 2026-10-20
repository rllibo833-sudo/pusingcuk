# Issue Siap Dibuat di GitHub

Dokumen ini berisi draft untuk issue yang perlu dibuat atau diverifikasi. Sebelum membuat issue, cek issue yang sudah ada agar tidak duplikat. Jangan menandai masalah sebagai terbuka jika sudah diperbaiki dan terverifikasi.

## 1. [bug] Lexer menolak digit Unicode dengan diagnostic yang jelas

**Label yang disarankan:** `bug`, `good first issue`

Karakter seperti `²`, `³`, dan `¹` dapat dianggap digit oleh Python `str.isdigit()`, tetapi tidak dapat diproses sebagai angka desimal biasa oleh `int()`. Lexer harus menerima digit ASCII sesuai grammar bahasa dan memberi `LexerError` yang berguna untuk input di luar grammar.

Reproduksi:
```cuk
jancuk
lah x = ²5
selesai jancuk
```

**Kriteria penerimaan:** tidak ada traceback mentah; diagnostic menunjuk lokasi input; fixture positif dan negatif melindungi perilaku.

## 2. [bug] Validasi pemetaan namespace built-in

**Label yang disarankan:** `bug`

Periksa konsistensi `BUILTIN_NAMESPACES`, registry `BUILTINS`, dan pemeriksaan built-in yang hilang di `library/stdlib.py`. Pastikan namespace seperti `json` memanggil implementasi kanonis dan menghasilkan diagnostic yang stabil bila pemetaan tidak valid.

**Kriteria penerimaan:** tes langsung untuk lookup namespace dan fixture .cuk untuk jalur publik.

## 3. [bug] Evaluator menangani akses atribut AST dengan aman

**Label yang disarankan:** `bug`

Parser dapat menghasilkan node `Attribute` untuk ekspresi seperti `data.nama`. Evaluator harus menangani akses yang didukung, dan menolak akses yang tidak valid dengan diagnostic terkontrol—bukan crash internal.

**Kriteria penerimaan:** fixture untuk akses properti kamus yang valid, key yang hilang, dan nilai yang tidak mendukung akses atribut.

## 4. [conformance] Integrasikan differential runner

**Label yang disarankan:** `conformance`

Bandingkan target yang benar-benar tersedia dengan normalisasi exit code, stdout, kelas diagnostic, dan nomor baris. Ketidaksesuaian harus menghasilkan laporan reproduksi; jangan menyebut target yang tidak tersedia sebagai gagal semantik.

## 5. [conformance] Buat compatibility matrix dari eksekusi fixture

**Label yang disarankan:** `conformance`

Hasilkan laporan mesin dan Markdown dari manifest fixture. CI harus gagal jika artefak yang dikomit tidak cocok dengan hasil generator, tanpa mengubah laporan secara manual.

## 6. [cleanup] Sinkronkan dokumentasi dengan bukti aktual

**Label yang disarankan:** `docs`, `cleanup`

Audit versi, jumlah fixture, daftar built-in, status backend, dan instruksi menjalankan contoh. Semua angka harus berasal dari sumber yang dapat diperbarui dan tidak boleh diperkirakan.
