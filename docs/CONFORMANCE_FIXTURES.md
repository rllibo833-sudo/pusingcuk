# Kontrak Fixture Konformansi Pusingcuk

Status: harness awal tersedia melalui `python tools/conformance.py`; cakupan fixture masih kecil dan akan diperluas bertahap.

## Tujuan

Fixture adalah program kecil dengan hasil yang diharapkan dan metadata tentang fitur yang diuji. Fixture menjadi penghubung antara spesifikasi, interpreter referensi, runtime native, dan backend compiler berikutnya.

## Struktur yang dituju

Fixture sumber disimpan sebagai `.pusingcuk`. Metadata sebaiknya dipisahkan ke manifest yang mudah dibaca mesin, misalnya JSON. Contoh rancangan:

```json
{
  "schema_version": 1,
  "id": "core.function.add",
  "source": "functions_add.pusingcuk",
  "profile": "core",
  "requires": ["functions", "integer-arithmetic"],
  "expected": {
    "exit_code": 0,
    "stdout": "42\n",
    "stderr_class": null
  },
  "runtimes": {
    "reference": "required",
    "native": "required",
    "wasm": "optional"
  }
}
```

Manifest aktif berada di `tests/conformance/manifest.json`. Harness memvalidasi versi schema, ID unik, field yang diizinkan, exit code, kelas error, status runtime, dan path fixture; ia tidak menjalankan perintah dari metadata.

## Aturan metadata

- `schema_version` versi format manifest; `id` unik dan stabil.
- `source` harus berupa path relatif dalam direktori fixture; path traversal harus ditolak.
- `profile` menunjukkan profil fitur yang diuji.
- `requires` mencantumkan fitur yang benar-benar dipakai.
- `expected.exit_code` wajib untuk kasus sukses maupun gagal.
- `stdout` dan kelas error ditulis eksplisit; stderr penuh boleh diuji untuk kasus yang memang stabil, tetapi jangan membuat seluruh suite rapuh terhadap variasi path.
- Status runtime harus dibedakan: `required`, `optional`, atau `unsupported`. Unsupported tidak dihitung lulus sebagai konformansi; laporan harus menyebut fitur belum didukung.
- Fixture negatif harus mengharapkan kegagalan yang sesuai, bukan menerima semua error sebagai hasil benar.
- Metadata tidak boleh mengeksekusi perintah shell atau mengubah environment runner.

## Kategori awal

1. Lexing/parsing: kata kunci, alias slang, komentar, string dan error sintaks.
2. Nilai/ekspresi: angka, teks, boolean, equality, truthiness, operator dan overflow.
3. Scope/fungsi: parameter, jumlah argumen, return, rekursi, nama tidak dikenal.
4. Koleksi: list/kamus, key identity, indeks, mutasi, batas kapasitas.
5. Control flow: kondisi, loop, iterasi, batas eksekusi.
6. CLI: exit code, stdout/stderr, file tidak ditemukan, opsi tidak dikenal.
7. Platform/capability: fitur file, jaringan, browser, atau FFI hanya diuji pada runtime yang menyatakan capability tersebut.
8. Compiler: source map, diagnostik compile-time, target output dan runtime hasil kompilasi.

## Perbandingan runtime

Harness membandingkan perilaku yang terlihat pengguna, bukan representasi memori internal. Minimal bandingkan:
- kode keluar;
- stdout byte-for-byte untuk output yang dikontrak;
- kelas error dan lokasi sumber untuk kasus gagal;
- tidak ada crash, hang, atau output parsial yang tidak diharapkan.

Jika error message memang menjadi kontrak publik, uji pesan yang distabilkan. Selain itu, uji kelas error dan lokasi agar refactor internal tidak mematahkan tes yang tidak relevan.

## Keamanan dan determinisme

- Jangan menjalankan fixture yang tidak dipercaya dengan kredensial atau hak istimewa.
- Tetapkan timeout, batas output, dan batas resource untuk setiap runner.
- Jalankan dari direktori sementara bila fixture menghasilkan file.
- Jangan mengizinkan manifest memilih executable atau shell command arbitrer.
- Pastikan test runner membersihkan artefak lokal dan tidak commit hasil build.

## Gerbang sebelum implementasi dianggap siap

1. [x] Manifest schema terdokumentasi dan divalidasi.
2. [x] Harness menampilkan PASS/FAIL/UNSUPPORTED terpisah.
3. [x] Satu fixture sukses dan satu fixture gagal dijalankan pada runtime wajib saat ini (reference dan native).
4. [x] CI menjalankan suite di job native GCC dan Clang.
5. [ ] Tambahkan cakupan fixture dan jalankan untuk setiap backend baru sebelum backend dianggap konforman.
6. [ ] Perluas kelas diagnostik error setelah kontrak error publik distabilkan.

## Hubungan dengan dokumen lain

- [Spesifikasi bahasa](../SPEC.md) mendefinisikan semantik yang harus diikuti.
- [Kontrak kompatibilitas](COMPATIBILITY.md) mendefinisikan klaim portabilitas.
- [Arsitektur compiler dan interoperabilitas](COMPILER_INTEROP.md) menjelaskan pipeline IR/backend/FFI.
- [Runtime native](NATIVE_RUNTIME.md) mencatat subset native yang benar-benar diuji.
