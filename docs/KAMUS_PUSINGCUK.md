# Kamus Pusingcuk — Versi Bahasa Warung

Dokumen ini buat yang baru belajar, termasuk yang belum pernah ngoding. Anggap ini peta: kata bahasa Pusingcuk artinya apa, file repo buat apa, dan mana fitur yang sudah ada atau masih cita-cita.

## 1. Mulai dari mana?

- `README.md`: halaman depan proyek dan cara menjalankan.
- `SPEC.md`: aturan resmi sintaks bahasa.
- `docs/PEMULA.md`: tutorial langkah demi langkah.
- `docs/KOSAKATA_GENZ.md`: kata kunci dan alias slang.
- `docs/COMPATIBILITY.md`: fitur mana yang jalan di runtime mana.
- `docs/NATIVE_RUNTIME.md`: kemampuan runtime C yang sudah dites.
- `docs/COMPILER_TARGETS.md`: cara menerjemahkan program ke target lain.
- `CONTRIBUTING.md`: aturan kalau mau ikut mengembangkan.
- `SECURITY.md`: peringatan dan aturan keamanan.

## 2. Kamus kata Pusingcuk

| Kata | Bahasa gampangnya | Contoh |
|---|---|---|
| `jancuk` | Mulai program | `jancuk` |
| `selesai jancuk` | Program selesai | `selesai jancuk` |
| `lah` | Bikin variabel baru, semacam kotak buat menyimpan nilai | `lah umur = 17` |
| `hedeh` | Tampilkan sesuatu ke layar | `hedeh umur` |
| `tanya` | Nanya ke pengguna lewat terminal | `tanya nama = "Nama: "` |
| `njir` | Kalau kondisi ini benar, jalankan bagian di bawahnya | `njir umur >= 17` |
| `kampret` | Kalau kondisi tadi tidak benar, jalankan bagian alternatif | `kampret` |
| `mumet` | Ulangi kode selama syaratnya masih benar | `mumet i < 3` |
| `untuk` | Ulangi kode untuk setiap item dalam daftar atau rentang | `untuk angka dalam rentang(1, 4)` |
| `fungsi` | Bikin potongan kode yang bisa dipanggil berkali-kali | `fungsi tambah(a, b)` |
| `balek` | Mengirim hasil dari fungsi ke pemanggilnya | `balek a + b` |
| `benar` / `salah` | Nilai iya/tidak | `lah aktif = benar` |
| `dan` / `atau` / `bukan` | Logika AND / OR / NOT | `njir aktif dan umur > 12` |
| `selesai njir` | Menutup blok kondisi | `selesai njir` |
| `selesai mumet` | Menutup blok perulangan while | `selesai mumet` |
| `selesai untuk` | Menutup blok perulangan untuk | `selesai untuk` |
| `selesai fungsi` | Menutup definisi fungsi | `selesai fungsi` |

Nama alias slang boleh dipakai kalau memang didukung lexer, tetapi untuk dokumentasi resmi dan contoh lintas-runtime, lebih gampang memakai kata kanonis. Daftar alias lengkap ada di `docs/KOSAKATA_GENZ.md` dan `library/kosakata.json`.

## 3. Contoh program utuh

```pusingcuk
jancuk
lah nama = "Dina"
lah umur = 18

fungsi tambah(a, b)
    balek a + b
selesai fungsi

hedeh "Halo, " + nama
hedeh tambah(20, 22)

njir umur >= 17
    hedeh "Boleh lanjut"
kampret
    hedeh "Belum cukup"
selesai njir
selesai jancuk
```

Simpan sebagai `halo.pusingcuk`, lalu dari folder utama repo jalankan:

```sh
python pusingcuk_new.py halo.pusingcuk
```

Kalau memakai runtime native Termux, ikuti dulu langkah instalasi di `docs/PEMULA.md`. Runtime native harus dibangun lebih dulu.

## 4. Fungsi bawaan

| Fungsi | Gunanya |
|---|---|
| `panjang(nilai)` | Menghitung jumlah karakter/item sesuai jenis nilai dan runtime |
| `rentang(akhir)` | Membuat deretan angka dari 0 sampai sebelum angka akhir |
| `rentang(mulai, akhir)` | Membuat deretan angka dari mulai sampai sebelum akhir |
| `rentang(mulai, akhir, langkah)` | Membuat deretan angka dengan jarak tertentu; langkah tidak boleh 0 |
| `mutlak(angka)` | Menghilangkan tanda minus dari nilai angka |
| `minimum(a, b)` | Memilih angka yang lebih kecil |
| `maksimum(a, b)` | Memilih angka yang lebih besar |
| `bulatkan(angka)` | Membulatkan angka dengan aturan yang didokumentasikan |
| `teks(nilai)` | Mengubah nilai menjadi teks pada registry pustaka standar; cek dukungan target |
| `bilangan(nilai)` | Mengubah nilai menjadi integer pada registry pustaka standar; cek dukungan target |
| `desimal(nilai)` | Mengubah nilai menjadi angka desimal pada registry pustaka standar; cek dukungan target |
| `logika(nilai)` | Mengubah nilai menjadi benar/salah pada registry pustaka standar; cek dukungan target |

**Catatan penting:** fungsi yang ada di satu file belum tentu otomatis jalan di semua jalur Pusingcuk. Interpreter Python, runtime C, dan compiler target punya kemampuan yang berbeda. Jangan anggap sama sebelum tesnya membuktikan.

## 5. Kamus istilah teknis

| Istilah | Arti versi gampang |
|---|---|
| **Kode sumber** | Tulisan program yang dibuat manusia, misalnya file `.pusingcuk`. |
| **Lexer** | Pemilah kata. Memecah kode jadi kata kunci, nama, angka, tanda kurung, dan operator. |
| **Parser** | Pemeriksa susunan kata. Memastikan kode mengikuti aturan bahasa. |
| **AST** | Peta bentuk program setelah dibaca parser; bukan kode mentah lagi. |
| **Interpreter** | Program yang membaca lalu menjalankan kode Pusingcuk secara langsung. |
| **Runtime** | Mesin pendukung yang benar-benar menjalankan program dan mengurus nilai, fungsi bawaan, serta error. |
| **Runtime native** | Runtime yang dibangun jadi executable untuk perangkat. Runtime C Pusingcuk sudah punya fitur teruji, tapi belum selengkap interpreter. |
| **Compiler** | Penerjemah program ke bentuk lain, misalnya JavaScript atau Python. |
| **Backend compiler** | Bagian compiler yang menghasilkan target tertentu. Ini beda arti dengan “backend server”. |
| **IR** | Bentuk perantara antara kode sumber dan target compiler, supaya beberapa target bisa memakai fondasi yang sama. |
| **Bytecode** | Instruksi sederhana untuk mesin virtual, bukan kode sumber biasa. Format PVM masih draft. |
| **VM** | Virtual machine, yaitu program yang menjalankan bytecode. |
| **Tes konformansi** | Tes yang membandingkan perilaku fitur yang sama di beberapa runtime. |
| **Library / pustaka** | Kumpulan fungsi atau contoh yang bisa dipakai ulang. |
| **Dependensi** | Program atau paket tambahan yang diperlukan untuk membangun atau menjalankan sesuatu. |
| **API** | Aturan komunikasi supaya satu program bisa meminta layanan dari program lain. |
| **Database** | Tempat menyimpan data terstruktur, misalnya data pengguna atau transaksi. |
| **Frontend web** | Bagian aplikasi yang dilihat dan digunakan orang di browser. |
| **Backend web/server** | Bagian yang memproses permintaan, aturan bisnis, dan data di server. |
| **ABI / FFI** | Aturan supaya program yang dibuat dengan bahasa berbeda bisa saling memanggil fungsi. Pusingcuk belum punya kontrak stabil untuk ini. |
| **WASM** | Format kompilasi portabel bernama WebAssembly. Backend Pusingcuk ke WASM belum tersedia. |
| **Blockchain SDK** | Pustaka untuk berkomunikasi dengan jaringan blockchain. Dukungan produksi belum tersedia. |
| **CI** | Robot yang otomatis menjalankan tes ketika ada perubahan kode. Lulus CI bukan jaminan semua fitur dan semua HP sudah teruji. |
| **Sandbox** | Pagar isolasi yang benar-benar membatasi apa yang boleh disentuh program. Pusingcuk belum menjamin sandbox OS. |
| **Capability** | Izin yang diberikan secara sengaja, misalnya izin membaca file atau mengakses database. Ini arah desain keamanan ke depan. |

## 6. File dan folder utama

| Lokasi | Fungsinya |
|---|---|
| `pusingcuk_new.py` | Jalur utama interpreter yang mudah dicoba dari Python. |
| `lexer.py`, `parser.py`, `ast_nodes.py` | Memecah dan memahami sintaks program. |
| `evaluator.py`, `interpreter.py` | Menjalankan program dan menerapkan aturan nilai. |
| `compiler/` | Compiler eksperimental, IR, backend, dan VM berbasis JSON bytecode. |
| `native/`, `src/c-core/` | Kode dan build runtime C. |
| `src/backends/` | Backend PVM terpisah untuk JavaScript dan Python. PVM ini masih format draft. |
| `library/` | Registry pustaka standar, kosakata mesin, dan contoh. |
| `examples/` | Contoh program yang bisa dijadikan bahan belajar. |
| `tests/` | Tes otomatis dan contoh input untuk memastikan fitur tetap bekerja. |
| `tools/` | Alat bantu pengembangan, konformansi, dan workbench lokal. |
| `android-studio/` | Proyek Android Studio; status dan batasnya lihat dokumen khusus. |
| `archive/legacy/` | Kode lama untuk referensi sejarah; bukan jalur utama dan jangan dipakai untuk proyek baru. |
| `docs/` | Spesifikasi, tutorial, audit, roadmap, dan penjelasan teknis. |

## 7. Yang sudah ada dan yang belum

**Jalur yang memang ada:** interpreter Python, runtime native C dengan subset teruji, serta compiler eksperimental ke JavaScript, Python, HTML, JSON IR, dan VM JSON. Tiap target belum tentu mendukung fitur yang sama.

**Belum boleh dianggap selesai:** sistem modul/paket lintas-runtime, API server produksi, konektor database lengkap, backend WASM, binding frontend browser penuh, ABI/FFI stabil, blockchain produksi, atau sandbox keamanan umum.

Itu semua boleh menjadi tujuan komunitas, tapi jangan ditulis seolah sudah siap dipakai. Cara yang sehat: tentukan aturan dulu, buat contoh kecil, buat tes positif dan negatif, dokumentasikan target yang didukung, baru klaim fiturnya.

## 8. Aturan pengembangan Pusingcuk

1. Tetap **offline-first**. Jangan menambahkan `os.system`, Python `eval`/`exec`, `requests`, dependensi OpenAI, kewajiban API key, atau koneksi internet otomatis.
2. Jangan menganggap kode hasil compiler otomatis aman. Parser dan runtime harus membatasi fitur dengan jelas.
3. Kalau aturan bahasa berubah, perbarui `SPEC.md`, implementasi, tes, dan matriks kompatibilitas bersama-sama.
4. Tambahkan tes untuk kasus normal dan kasus salah, bukan cuma contoh yang berhasil.
5. Beri label jelas: direncanakan, prototipe, eksperimental, teruji, atau stabil.
6. Bikin perubahan kecil, bisa dibaca pemula, dan punya contoh.
7. Jangan commit kata sandi, token, data pribadi, file hasil build, atau file eksperimen lokal.
8. Jangan menjalankan program atau bytecode dari orang tak dikenal di HP yang berisi file penting. Operasi file belum dibatasi oleh sandbox sistem operasi.
