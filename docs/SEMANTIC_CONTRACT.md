# Kontrak Semantik Pusingcuk v1

Status: baseline engineering untuk perilaku yang harus dipatuhi front-end, interpreter, runtime native, dan backend berikutnya. Hanya perilaku yang ditetapkan spesifikasi atau dibuktikan fixture boleh diklaim stabil lintas runtime.

## Satu sumber kebenaran

- SPEC.md mendefinisikan sintaks dan perilaku bahasa.
- Dokumen ini menyatakan prinsip semantik yang dapat diuji.
- tests/conformance/manifest.json adalah bukti yang dapat dijalankan untuk subset yang dicakup.
- Interpreter referensi dan runtime native harus menghasilkan hasil sama untuk fixture yang menandai keduanya required.
- Backend baru tidak boleh mengubah perilaku tampak pengguna tanpa perubahan spesifikasi dan fixture yang disengaja.

## Evaluasi dan nilai

- Ekspresi mengikuti precedence dalam SPEC.md dan operand dievaluasi kiri ke kanan.
- dan / atau menggunakan short-circuit: operand kanan tidak dievaluasi jika hasil sudah ditentukan.
- Boolean benar dan salah adalah tipe berbeda dari angka. Kesetaraan benar == 1 menghasilkan tidak.
- Output boolean memakai okelah dan tidak, bukan True/False.
- Builtin statistik eksperimental `rata_rata` dan `median` menerima tepat satu daftar nonkosong yang hanya berisi angka finite; boolean dan tipe lain ditolak. Implementasi yang diuji ada pada backend JS/Python dan HTML, bukan VM/native C.
- Urutan output dan mutasi koleksi adalah perilaku teramati yang tidak boleh berubah karena optimisasi.
- Pembagian dengan nol, overflow, angka non-finite, dan diagnostik spesifik harus memiliki fixture sebelum dianggap stabil lintas backend.

## Kontrol dan fungsi

- Kondisi njir dan mumet memilih cabang/pengulangan sesuai truthiness nilai.
- Fungsi menggunakan ruang nama fungsi; balek mengembalikan nilai dan hanya sah di dalam fungsi.
- Jumlah argumen harus cocok dengan jumlah parameter.
- Alias keyword dinormalisasi pada front-end; backend tidak boleh mengurai slang lewat pencocokan teks.
- Kegagalan batas resource harus menjadi error, bukan hasil parsial yang terlihat sukses.

## Koleksi

- Indeks list dimulai dari nol.
- Kesetaraan list membandingkan panjang dan elemen secara rekursif; list dengan isi sama dibandingkan setara, termasuk list bersarang. Runtime native membatasi kedalaman perbandingan rekursif untuk melindungi stack.
- Kesetaraan kamus masih berbasis identitas objek; perubahan ke kesetaraan struktural memerlukan keputusan kontrak terpisah.
- Mutasi indeks mempertahankan identitas koleksi yang dirujuk variabel.
- Kunci dictionary teks, angka, dan boolean memiliki identitas tipe; boolean tidak boleh bertabrakan dengan angka yang nilainya sama.
- Urutan iterasi dictionary harus dinyatakan eksplisit sebelum dijadikan jaminan portabel.
- Kapasitas, indeks negatif, Unicode penuh, dan serialisasi koleksi mengikuti matriks runtime serta fixture yang sudah ada. Jangan simpulkan dukungan lintas backend dari satu implementasi.

## Error dan portabilitas

- Program gagal harus menghasilkan exit code bukan nol dan diagnostik ke stderr. Teks penuh menjadi kontrak hanya jika fixture menguncinya.
- Fixture membandingkan exit code, stdout, dan kelas error, bukan path absolut atau detail internal yang tidak stabil.
- Unsupported bukan pass.
- File, jaringan, database, proses, browser, dan FFI adalah kapabilitas platform, bukan efek samping tersembunyi dari bahasa inti.
- Runtime native tidak otomatis menjadi sandbox.

## Perubahan kontrak

Perubahan semantik wajib mencakup pembaruan SPEC.md dan dokumen ini, fixture positif/negatif, pengujian semua runtime yang mengklaim dukungan, serta catatan kompatibilitas/versi bila mematahkan perilaku lama.

## Batas compiler saat ini

IR v1 merupakan AST-preserving interchange format yang berversi, deterministik, dapat divalidasi, dan membawa source map serta daftar fitur. Ini belum bytecode, belum SSA, belum mengoptimalkan program, dan belum menghasilkan C/WASM/JavaScript. Backend dibangun setelah kontrak semantik dan fixture mencakup fitur yang diterjemahkan.


## Shared builtin metadata

`library/builtin_contract.json` is the canonical metadata source for builtin names, arity, importer allow-lists, backend helper mappings, and target support. Do not copy builtin-name tables into new importer/backend/test code. Runtime implementations remain target-specific, and every `supported` declaration must have executable tests.
