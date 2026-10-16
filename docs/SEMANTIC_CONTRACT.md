# Kontrak Semantik Pusingcuk v1

**Versi bahasa yang diatur:** `0.5-dev`. Nomor `v1` pada judul adalah revisi dokumen kontrak semantik, bukan versi bahasa.

Status: baseline engineering untuk perilaku yang harus dipatuhi front-end, interpreter, runtime native, dan backend berikutnya. Hanya perilaku yang ditetapkan spesifikasi atau dibuktikan fixture boleh diklaim stabil lintas runtime.

## Satu sumber kebenaran

- SPEC.md mendefinisikan sintaks dan perilaku bahasa.
- Dokumen ini menyatakan prinsip semantik yang dapat diuji.
- tests/conformance/manifest.json adalah bukti yang dapat dijalankan untuk subset yang dicakup.
- Interpreter referensi dan runtime native harus menghasilkan hasil sama untuk fixture yang menandai keduanya required.
- Backend baru tidak boleh mengubah perilaku tampak pengguna tanpa perubahan spesifikasi dan fixture yang disengaja.

## Baseline yang dipelihara saat ini

Interpreter Python modular adalah implementasi referensi. Runtime native C adalah implementasi kedua yang dijaga agar cocok pada subset yang tercantum sebagai wajib di `tests/conformance/manifest.json`. Fixture yang menyatakan `reference: required` dan `native: required` harus menghasilkan perilaku yang sama untuk exit code, stdout, dan kelas error sesuai kontrak fixture.

Untuk perubahan bahasa, ikuti satu jalur:
1. Tetapkan maksud perilaku di `SPEC.md` dan kontrak ini.
2. Perbarui lexer Python dan runtime C untuk fitur yang memang diklaim didukung pada keduanya.
3. Perbarui `library/kosakata.json` atau `library/builtin_contract.json` jika metadata terkait berubah.
4. Tambahkan kasus sukses dan kegagalan pada tes; gunakan fixture konformansi untuk perilaku yang harus sama di Python dan C.
5. Jalankan unit test Python, `make test-native`, dan `python tools/conformance.py`; CI harus lulus sebelum kompatibilitas diklaim.

Alias yang tercantum di bagian alias resmi `SPEC.md` adalah bagian dari permukaan bahasa. Perubahan pada alias harus disinkronkan pada lexer Python, pemetaan token runtime C, registry kosakata, dan fixture. Alias untuk kapabilitas platform yang belum tersedia di C harus tetap ditandai sesuai dukungan runtime, tidak disamarkan menjadi dukungan penuh.

Backend JavaScript kini memiliki implementasi untuk seluruh built-in terkontrak; fixture positif dan negatif tetap diperlukan untuk menjaga kesetaraan perilaku. JSON/HTML/CSV hanya tersedia pada target yang dinyatakan `supported` di kontrak. Compiler/transpiler lain dan PVM tetap eksperimental. Keduanya tidak mengubah semantik acuan, dan hasilnya tidak dihitung sebagai baseline Python/C.

## Evaluasi dan nilai

- Ekspresi mengikuti precedence dalam SPEC.md dan operand dievaluasi kiri ke kanan.
- dan / atau menggunakan short-circuit: operand kanan tidak dievaluasi jika hasil sudah ditentukan.
- Boolean benar dan salah adalah tipe berbeda dari angka. Kesetaraan benar == 1 menghasilkan tidak.
- Output boolean memakai `okelah` dan `tidak`, bukan `True`/`False`. Built-in `teks` juga menggunakan ejaan bahasa Pusingcuk untuk boolean.
- Kontrak built-in disimpan di `library/builtin_contract.json`, diuji oleh `tests/test_builtin_contract.py`, dan didokumentasikan di `docs/language/BUILTINS.md`. Interpreter referensi mendukung 25 built-in terdaftar; native C memiliki fixture untuk 17: `panjang`, `rentang`, `mutlak`, `minimum`, `maksimum`, `bulatkan`, `bawah`, `atas`, `akar`, `pangkat`, `logaritma`, `log10`, `sinus`, `kosinus`, `jumlah`, `rata_rata`, dan `median`. Transpiler/VM memiliki subset tersendiri.
- `sinus` dan `kosinus` menerima satu angka finite non-boolean dalam radian; semua input finite punya domain matematis valid, hasil non-finite ditolak, dan hasil integral dalam rentang aman dinormalisasi sebagai integer.
- `jumlah` menerima tepat satu daftar angka finite non-boolean. Daftar kosong bernilai integer 0; input integer-valued di luar `±(2^53 - 1)`, akumulasi non-finite, dan setiap hasil akumulasi integral sementara atau akhir di luar rentang aman ditolak sebagai error runtime. Hasil integral yang aman dinormalisasi ke integer; penjumlahan dilakukan berurutan dalam binary64 pada kedua runtime.
- `rata_rata` dan `median` menerima satu daftar tidak kosong yang berisi angka finite non-boolean dalam rentang aman `±(2^53 - 1)`; daftar kosong, boolean, tipe lain, aritas salah, dan angka di luar rentang ditolak. Fixture mengunci singleton, cancellation di batas aman, fraksi binary64, nilai negatif, sampel duplikat, median ganjil/genap, dan batas aman inklusif.
- Urutan output dan mutasi koleksi adalah perilaku teramati yang tidak boleh berubah karena optimisasi.
- Pembagian dengan nol harus gagal sebagai `runtime_error` pada baris sumber operasi; pembagian lantai negatif mengikuti floor matematika (`-7 // 3` menjadi `-3`) dan modulo memakai aturan `a - floor(a / b) * b` (`-7 % 3` menjadi `2`).
- Built-in numerik hanya menerima angka finite; boolean bukan angka. `akar(x)` mensyaratkan `x >= 0`; `pangkat(a, b)` menolak `a < 0` dengan `b` bukan integer serta `a == 0` dengan `b < 0`.
- Hasil non-finite, termasuk overflow `pangkat(10, 1000)`, menjadi `runtime_error`, bukan `inf`, `NaN`, atau output parsial. Hasil matematika integral dalam rentang aman `±(2^53 - 1)` direpresentasikan sebagai integer; hasil non-integral dicetak dengan representasi desimal terpendek yang round-trip ke nilai binary64.
- `bulatkan` menggunakan ties-to-even. Native C untuk `mutlak`, `minimum`, `maksimum`, `bulatkan`, `bawah`, `atas`, `akar`, `pangkat`, `sinus`, `kosinus`, `jumlah`, `rata_rata`, dan `median` hanya diklaim setelah fixture positif serta kasus aritas, tipe, domain/rentang, dan hasil numerik yang relevan lulus.

## Kontrol dan fungsi

- Kondisi njir dan mumet memilih cabang/pengulangan sesuai truthiness nilai.
- Blok `coba ... ketangkep nama` pada interpreter referensi mengikat teks pesan exception ke nama lokal handler; variabel scope luar dengan nama sama tidak tertimpa. Native C belum mengimplementasikan blok try/catch, sehingga fitur ini belum kontrak parity lintas-runtime.
- Fungsi menggunakan ruang nama fungsi; balek mengembalikan nilai dan hanya sah di dalam fungsi.
- Jumlah argumen harus cocok dengan jumlah parameter.
- Parameter dan variabel lokal tidak boleh bocor ke scope pemanggil; mutasi koleksi yang diteruskan sebagai argumen tetap terlihat karena kedua scope merujuk objek koleksi yang sama.
- Alias keyword dinormalisasi pada front-end; backend tidak boleh mengurai slang lewat pencocokan teks.
- Kegagalan batas resource harus menjadi error, bukan hasil parsial yang terlihat sukses.

## Koleksi

- Indeks list dimulai dari nol.
- Kesetaraan list membandingkan panjang dan elemen secara rekursif; list dengan isi sama dibandingkan setara, termasuk list bersarang. Runtime native membatasi kedalaman perbandingan rekursif untuk melindungi stack.
- Kesetaraan kamus masih berbasis identitas objek; perubahan ke kesetaraan struktural memerlukan keputusan kontrak terpisah.
- Mutasi indeks mempertahankan identitas koleksi yang dirujuk variabel; mutasi melalui parameter fungsi juga harus terlihat dari variabel pemanggil.
- Indeks list di luar batas dan kunci kamus yang tidak ditemukan harus gagal secara eksplisit dengan kelas `runtime_error` dan nomor baris yang sama pada fixture lintas-runtime.
- Kunci dictionary teks, angka, dan boolean memiliki identitas tipe; boolean tidak boleh bertabrakan dengan angka yang nilainya sama.
- Urutan iterasi dictionary harus dinyatakan eksplisit sebelum dijadikan jaminan portabel.
- Kapasitas, indeks negatif, Unicode penuh, dan serialisasi koleksi mengikuti matriks runtime serta fixture yang sudah ada. Jangan simpulkan dukungan lintas backend dari satu implementasi.

## Error dan portabilitas

- Kesalahan sintaks mengembalikan exit code `2`; kesalahan runtime `1`; sukses `0`. Kesalahan CLI untuk berkas yang tidak ditemukan mengembalikan `3` pada kedua CLI yang dipelihara.
- Diagnostik program gagal ditulis ke stderr dengan kelas `syntax_error` atau `runtime_error` dan nomor baris bila tersedia. Detail pesan dan kolom boleh lebih kaya pada satu runtime, tetapi kelas, kode keluar, stdout, dan nomor baris yang dilaporkan fixture wajib sama. CLI interpreter referensi juga menyajikan nama berkas, kolom, potongan sumber, penunjuk caret, dan saran koreksi yang sopan. Detail tersebut memperbaiki pengalaman pengembang, tetapi tidak mengubah kategori error lintas-runtime. Keyword dan alias harus tetap mengikuti `SPEC.md` serta registry kosakata yang ada; perbaikan diagnostik tidak menambahkan ejaan bahasa baru.
- Manifest tidak mendukung kode keluar berbeda per runtime untuk fixture yang sama. Perbedaan yang tersisa harus ditandai sebagai `unsupported`, bukan disamarkan sebagai pass.
- Unsupported bukan pass.
- File, jaringan, database, proses, browser, dan FFI adalah kapabilitas platform, bukan efek samping tersembunyi dari bahasa inti.
- Runtime native tidak otomatis menjadi sandbox.

## Perubahan kontrak

Perubahan semantik wajib mencakup pembaruan SPEC.md dan dokumen ini, fixture positif/negatif, pengujian semua runtime yang mengklaim dukungan, serta catatan kompatibilitas/versi bila mematahkan perilaku lama.

## Batas compiler saat ini

IR v1 merupakan AST-preserving interchange format yang berversi, deterministik, dapat divalidasi, dan membawa source map serta daftar fitur. Ini belum bytecode, belum SSA, belum mengoptimalkan program, dan belum menghasilkan C/WASM/JavaScript. Backend dibangun setelah kontrak semantik dan fixture mencakup fitur yang diterjemahkan.


## Shared builtin metadata

`library/builtin_contract.json` is the canonical metadata source for builtin names, arity, importer allow-lists, backend helper mappings, and target support. Do not copy builtin-name tables into new importer/backend/test code. Runtime implementations remain target-specific, and every `supported` declaration must have executable tests.
