# Arsitektur Compiler dan Interoperabilitas Pusingcuk

Status: rancangan arsitektur untuk memandu implementasi. Dokumen ini bukan klaim bahwa compiler multi-target atau FFI sudah tersedia.

## Tujuan

Pusingcuk harus dapat dipelajari sebagai bahasa Indonesia yang ramah, tetapi programnya tidak boleh terikat pada satu implementasi. Sasaran teknisnya adalah satu kontrak semantik dengan beberapa jalur eksekusi dan target kompilasi.

Istilah singkat:
- **Front-end** membaca sumber, memeriksa sintaks dan makna, lalu menghasilkan representasi program.
- **IR (intermediate representation)** adalah bentuk program perantara yang tidak bergantung pada sintaks sumber atau satu target.
- **Backend** menerjemahkan IR menjadi executable, bytecode, atau kode bahasa target.
- **ABI/FFI** adalah aturan data dan pemanggilan fungsi ketika Pusingcuk berkomunikasi dengan bahasa lain.

## Prinsip yang tidak boleh dilanggar

1. Satu spesifikasi semantik menjadi sumber kebenaran; setiap backend wajib mengikuti kontrak yang sama.
2. Alias slang seperti `jir` dan kata kanonis seperti `hedeh` harus menghasilkan makna yang sama setelah parsing. Backend tidak boleh menerjemahkan slang berdasarkan pencocokan teks.
3. Backend tidak boleh diam-diam mengubah perilaku tipe, truthiness, evaluasi boolean, urutan evaluasi, mutasi koleksi, atau error.
4. Fitur yang belum didukung target harus menghasilkan diagnostic yang jelas saat compile, bukan menghasilkan kode yang tampak sukses tetapi berbeda perilaku.
5. IR dan format artefak harus memiliki versi eksplisit. Perubahan yang mematahkan kompatibilitas memerlukan versi baru atau migrasi.
6. Host language adalah detail implementasi. Menulis compiler dalam C, Rust, Python, atau bahasa lain tidak membuat semantik Pusingcuk otomatis sama dengan bahasa host.
7. Optimisasi hanya boleh diterapkan jika mempertahankan semantik yang ditetapkan dan dibuktikan dengan tes.
8. Runtime native tidak dianggap sandbox. Kompilasi ke bahasa lain juga tidak otomatis membuat kode aman.

## Pipeline yang dituju

```text
Pusingcuk source (.pusingcuk)
  -> lexer
  -> parser
  -> AST
  -> name/scope/arity validation
  -> semantic analysis + feature capability checks
  -> Pusingcuk IR (versioned)
  -> optimizer (optional, semantics-preserving)
  -> backend
       -> native executable
       -> C source
       -> WebAssembly
       -> JavaScript/TypeScript target
       -> foreign-function bridge
  -> conformance tests + artifact/runtime checks
```

Pipeline ini adalah arah desain, bukan daftar backend yang sudah stabil. Saat ini interpreter modular Python menjadi jalur referensi dan runtime C native menjalankan subset teruji. Front-end menghasilkan IR v1 yang mempertahankan AST dan dapat divalidasi. CLI compiler memiliki target eksperimental JavaScript, Python, HTML, JSON IR, dan VM JSON dengan cakupan berbeda; backend C terpisah hanya mendukung subset integer terbatas. Optimizer umum, WebAssembly, ABI/FFI stabil, dan sistem modul/paket lintas-runtime belum tersedia.

## Batas antara bahasa inti dan platform

Bahasa inti berisi literal, variabel, ekspresi, kondisi, loop, fungsi, koleksi, serta aturan error yang ditetapkan spesifikasi. Kemampuan platform harus masuk melalui API eksplisit, bukan global tersembunyi.

API platform nantinya dikelompokkan menurut kapabilitas, misalnya:
- `core`: operasi murni dan nilai inti;
- `io.console`: input/output terminal;
- `io.files`: akses file;
- `net.http`: jaringan;
- `data.json`: encode/decode JSON;
- `web.dom`: antarmuka browser;
- `server.http` dan `data.sql`: server/database.

Nama di atas adalah contoh kategori rancangan, bukan modul yang saat ini dapat diimpor. API yang tidak didukung target harus ditolak atau diberi status capability yang eksplisit. Akses jaringan/file tidak boleh disisipkan secara implisit oleh backend.

## Kontrak IR

IR awal harus sederhana, deterministik, dapat divalidasi, dan mudah dibuat dari AST. Versi pertama sebaiknya tidak mengunci desain ke SSA, LLVM, bytecode tertentu, atau model memori spesifik.

Setiap artefak IR minimal perlu menyimpan:
- `ir_version`: versi format IR;
- `language_version`: versi semantik Pusingcuk;
- `source_map`: relasi node/instruksi ke file dan baris sumber;
- `features`: fitur semantik yang digunakan;
- `entry_point`: titik mulai program;
- `functions`: fungsi dengan parameter, blok, dan instruksi;
- informasi nilai dan operasi yang dapat divalidasi.

Prinsip format:
- Encoding UTF-8 dan serialisasi deterministik.
- Identifier internal terpisah dari nama tampilan sumber.
- Nilai boolean tidak disamakan dengan angka.
- Literal angka, string, dan kunci kamus mempertahankan aturan spesifikasi.
- Mutasi koleksi, evaluasi kiri-ke-kanan, dan urutan output tidak boleh berubah karena target.
- Setiap operasi memiliki aritas, jenis operand, efek samping, dan kondisi error yang didefinisikan.
- IR yang versi/strukturnya tidak dikenal harus ditolak dengan diagnostic, bukan ditebak.

JSON dapat berguna sebagai format debug atau pertukaran awal, tetapi belum dipilih sebagai format IR final. Implementasi pertama harus menguji kebutuhan debug, ukuran, validasi, dan evolusi versi sebelum format dibekukan.

## Strategi target kompilasi

### 1. C sebagai backend awal

C dapat menghasilkan executable yang mudah dipindahkan ke banyak toolchain, tetapi backend wajib menerapkan nilai Pusingcuk secara eksplisit. Jangan memetakan kamus, boolean, string UTF-8, atau error langsung ke tipe C yang semantiknya berbeda tanpa lapisan runtime yang teruji.

### 2. WebAssembly sebagai target portabel

WASM cocok untuk distribusi lintas host setelah model memori, import capability, error, dan ABI stabil. WASM tidak otomatis menyediakan file system, jaringan, DOM, atau sandbox aplikasi yang lengkap; semuanya memerlukan host API yang eksplisit.

### 3. JavaScript/TypeScript

Target ini relevan untuk web dan tooling full-stack. Backend harus mempertahankan perbedaan boolean/angka, aturan truthiness Pusingcuk, urutan evaluasi, error, dan semantik koleksi; jangan mengandalkan coercion JavaScript.

### 4. Rust atau bahasa lain

Backend Rust atau target lain baru layak setelah IR dan runtime value model stabil. Hindari membangun backend kedua hanya dengan translasi teks. Gunakan IR yang sama dan suite konformansi yang sama.

### 5. Interoperabilitas dengan library host

FFI harus menggunakan ABI berversi dengan tipe lintas bahasa yang kecil dan jelas. Kandidat tipe dasar: integer dengan rentang eksplisit, float IEEE-754 yang valid, boolean, string UTF-8 dengan panjang eksplisit, byte buffer, dan handle objek opaque. Jangan mengirim pointer mentah, layout struct native, atau exception host melintasi batas ABI tanpa kontrak.

Setiap panggilan lintas bahasa harus menetapkan ownership/lifetime, alokasi dan pembebasan memori, pemetaan error, thread-safety, serta konversi nilai. Nilai yang tidak dapat direpresentasikan harus menghasilkan error konversi, bukan kehilangan informasi diam-diam.

## Profil portabel

Sebelum seluruh bahasa bisa dikompilasi ke banyak target, tetapkan profil portabel bertahap:
1. **Core**: nilai dasar, variabel, ekspresi, kondisi, loop, fungsi dan koleksi yang memiliki semantik bersama.
2. **Console**: input/output standar melalui API eksplisit.
3. **Platform API**: file, jaringan, browser, database dan layanan OS berdasarkan capability.
4. **Native extensions**: integrasi host/FFI dengan ABI dan versi yang jelas.

Sebuah program hanya portabel ke target jika seluruh fitur dan capability yang digunakannya didukung target itu dan lulus suite konformansi. Portabilitas tidak ditentukan oleh ekstensi file atau keberhasilan parsing saja.

## Jalur implementasi

1. Bekukan kontrak semantik dan buat manifest fixture konformansi.
2. Bangun harness yang membandingkan interpreter referensi dan native untuk profil yang benar-benar didukung.
3. Pisahkan parsing/validasi dari eksekusi sehingga compiler dapat memakai AST yang sama.
4. Rancang model nilai runtime dan diagnostik lintas implementasi.
5. Tambahkan IR versi awal, validator IR, dan source map.
6. Buat satu backend kedua sebagai proof-of-concept setelah IR stabil; bandingkan output dan error dengan fixture.
7. Baru setelah itu tambah optimizer, package/module system, WASM, web backend, dan FFI.
8. Self-hosting adalah sasaran jauh, bukan prasyarat compiler yang berguna.

## Kriteria penerimaan backend baru

Backend belum boleh disebut siap hanya karena bisa mengompilasi contoh "Halo dunia". Ia perlu:
- menerima atau menolak setiap fitur berdasarkan capability yang dideklarasikan;
- lulus fixture konformansi untuk fitur yang didukung;
- menyamakan stdout, exit code, dan kelas error yang disepakati;
- menguji batas angka, teks UTF-8, koleksi, fungsi, rekursi, dan input;
- menghasilkan diagnostic dengan lokasi sumber;
- mendokumentasikan toolchain, target OS/arsitektur, dan dependensi;
- membuktikan artefak berjalan di lingkungan target yang diklaim.

## Status saat ini

| Komponen | Status |
|---|---|
| Spesifikasi sintaks dan semantik awal | Ada, perlu diperluas dan diuji konsistensinya |
| Interpreter modular Python | Jalur referensi |
| Runtime native C | Subset teruji; belum setara penuh |
| IR v1 | Tersedia sebagai format AST-preserving yang tervalidasi; belum menjadi ABI stabil |
| Backend C source generation | Eksperimental; hanya subset integer terdokumentasi |
| WebAssembly backend | Belum tersedia |
| JavaScript backend | Ada sebagai target eksperimental; bukan backend produksi yang sepenuhnya kompatibel |
| ABI/FFI stabil | Belum tersedia |
| Modul dan package manager | Belum tersedia penuh |

Jangan mengklaim target eksperimental sebagai stabil atau mengklaim ABI/FFI sampai implementasi, tes, dan dokumentasi target benar-benar ada.
