# Spesifikasi Sintaks Pusingcuk 0.6-dev

> Konvensi berkas: gunakan ekstensi `.cuk` untuk program baru, setara peran `.py` di Python. Ekstensi `.pusingcuk` tetap diterima oleh interpreter, runtime native, dan compiler yang relevan demi kompatibilitas. Ekstensi tidak menentukan fitur runtime; fitur harus tetap diverifikasi melalui tes konformansi.

## 1. Struktur program

Setiap program dimulai dengan:

    jancuk

Dan diakhiri dengan:

    selesai jancuk

## 2. Deklarasi variabel

    lah nama = "Budi"
    lah umur = 20
    lah aktif = benar

Nama variabel harus diawali huruf atau garis bawah.

Deklarasi ulang nama variabel yang sudah ada ditolak.

## 3. Assignment

    umur = umur + 1

Assignment hanya boleh dilakukan pada variabel yang sudah dibuat.

## 4. Output

    hedeh "Halo"
    hedeh umur
    hedeh umur + 1

## 5. Input pengguna

    tanya nama = "Nama? "
    hedeh "Halo, " + nama

`tanya` menampilkan prompt teks dan membaca satu baris dari input standar. Ini tersedia pada runtime modular dan native CLI; input interaktif melalui Pusingcuk Studio belum diverifikasi. Runtime native mendukung indeks teks nonnegatif berbasis code point UTF-8; indeks negatif belum didukung.

## 6. Kondisi

    njir umur >= 18
        hedeh "Dewasa"
    kampret
        hedeh "Belum dewasa"
    selesai njir

Cabang kampret bersifat opsional.

## 7. Perulangan

    lah i = 1
    mumet i <= 3
        hedeh i
        i = i + 1
    selesai mumet

Interpreter memiliki batas 10000 iterasi per loop dan 100000 langkah eksekusi total.

## 8. Operator

Matematika: + - * / // %

Perbandingan: == != < <= > >=

Logika: dan, atau, bukan

Boolean: benar, salah

### Daftar, kamus, teks, dan indeks

Daftar ditulis menggunakan tanda kurung siku, misalnya `[10, 20, 30]`.
Kamus ditulis dengan kurung kurawal dan pasangan kunci-nilai, misalnya `{"nama": "Budi", "umur": 20}`. Kunci teks, angka, dan boolean merupakan jenis kunci berbeda; khususnya, kunci `benar` dan kunci angka `1` tidak sama. Operator kesetaraan juga tidak menyamakan boolean dengan angka.
Indeks daftar dan teks dimulai dari 0. Daftar dapat dibaca dan diubah melalui indeks. Operator `+` menerima dua angka, dua teks, atau dua daftar; konkatenasi daftar menghasilkan daftar baru dengan urutan elemen dipertahankan tanpa memutasi operand. Nilai kamus dapat dibaca dan diubah melalui kunci.
`panjang(nilai)` menghitung elemen teks, daftar, kamus, atau rentang. `rentang(akhir)`, `rentang(mulai, akhir)`, dan `rentang(mulai, akhir, langkah)` membuat urutan bilangan bulat dengan batas akhir eksklusif; langkah tidak boleh nol. Nilai rentang yang disimpan dalam variabel dapat dibaca melalui indeks nonnegatif berbasis nol; indeks bukan bilangan bulat atau di luar batas menghasilkan kesalahan runtime. Interpreter referensi Python menyediakan 25 built-in terkontrak, termasuk konversi, matematika, trigonometri, logaritma, dan statistik. Runtime native C kini memiliki fixture untuk seluruh 25 nama built-in, tetapi sebagian tipe/representasi tetap merupakan subset: `bilangan` menerima angka non-boolean atau teks integer dalam rentang aman; `desimal` menerima angka finite non-boolean atau teks angka finite; `logika` memakai truthiness; `teks` menerima teks, angka finite, boolean, dan nilai None. `teks()` pada native C menolak list, kamus, dan rentang sampai format lintas runtime disepakati. Fitur yang hanya ada pada subset Python tidak dianggap portabel hanya karena namanya terdaftar. `bulatkan` memakai aturan ties-to-even, misalnya `bulatkan(2.5)` menjadi `2` dan `bulatkan(3.5)` menjadi `4`. `akar(nilai)` menerima tepat satu angka finite non-boolean dan menolak nilai negatif. `pangkat(basis, eksponen)` menerima tepat dua angka finite non-boolean; basis negatif memerlukan eksponen bulat, dan basis nol tidak boleh dipangkatkan dengan eksponen negatif. `sinus(radian)` dan `kosinus(radian)` menerima satu angka finite non-boolean dalam radian. `logaritma(angka)` menghasilkan logaritma natural dan `log10(angka)` menghasilkan logaritma basis 10; keduanya menerima satu angka finite non-boolean yang harus lebih besar dari nol. Domain tidak valid dan hasil non-finite menjadi kesalahan runtime pada Python maupun native C. `jumlah(daftar)` menerima satu daftar angka finite non-boolean; daftar kosong menghasilkan nol. Input integer-valued serta setiap hasil akumulasi integral sementara atau akhir `jumlah` yang berada di luar rentang aman `±(2^53 - 1)` ditolak agar perilaku Python/C konsisten. `rata_rata(daftar)` dan `median(daftar)` menerima satu daftar tidak kosong berisi angka finite non-boolean; nilai di luar rentang integer aman `±(2^53 - 1)` ditolak. Rata-rata menjumlahkan elemen yang masing-masing dibagi panjang daftar; median mengurutkan nilai lalu mengambil nilai tengah atau rata-rata dua nilai tengah. Overflow dan hasil non-finite menjadi kesalahan runtime, bukan output parsial. Hasil non-finite merupakan kesalahan runtime. Hasil matematika bulat dalam rentang integer aman lintas target dinormalisasi menjadi integer; hasil pecahan memakai representasi desimal terpendek yang mempertahankan nilai binary64. `jadi_json(teks)` mengembalikan `salah` jika teks bukan JSON valid, sementara teks JSON `null` yang valid menghasilkan nilai None pada interpreter reference. `json_baca(teks)` menghasilkan kamus yang dapat dibaca dan diubah melalui akses indeks pada interpreter referensi Python dan backend JavaScript; runtime native C belum mengklaim dukungan JSON. `teks(benar)` menghasilkan `okelah`; `teks(salah)` menghasilkan `tidak`. Detail argumen dan dukungan per target harus mengikuti [katalog built-in](docs/language/BUILTINS.md).
Kunci kamus native dibatasi pada teks, angka, dan boolean. Assignment ke kunci baru menambahkan entri, sedangkan assignment ke kunci yang sudah ada memperbarui nilainya. Kamus kosong bernilai salah dan kamus berisi entri bernilai benar dalam kondisi; perulangan `untuk` menghasilkan kunci kamus. Kunci yang tidak didukung, kunci yang tidak ditemukan, dan indeks di luar batas menghasilkan kesalahan.

## 9. Perulangan untuk

Contoh:

    jancuk
    untuk angka dalam rentang(1, 5)
        hedeh angka
    selesai untuk
    selesai jancuk

Perulangan modular untuk nama dalam koleksi mengunjungi setiap elemen daftar atau teks, setiap kunci kamus, atau setiap bilangan dalam rentang. Runtime native C yang diuji mendukung iterasi list, teks (per code point UTF-8), kamus (menghasilkan kunci), dan `rentang()`.

`rentang(akhir)`, `rentang(mulai, akhir)`, dan `rentang(mulai, akhir, langkah)` menerima satu sampai tiga argumen bilangan bulat. Batas akhir tidak termasuk hasil. Langkah tidak boleh nol. Setiap perulangan dibatasi 10000 iterasi dan seluruh program dibatasi 100000 langkah native/modular.

## 10. Fungsi buatan pengguna

Fungsi dideklarasikan dengan `fungsi nama(parameter)` dan diakhiri dengan `selesai fungsi`. Aturan mutlak: `balek` wajib diikuti ekspresi pada baris yang sama; `balek` kosong adalah kesalahan sintaks terkontrol. Gunakan `balek ekspresi` untuk mengembalikan nilai. Jumlah argumen harus sesuai dengan jumlah parameter. Fungsi tingkat atas dipindai sebelum program berjalan, sehingga pemanggilan sebelum definisi dan rekursi didukung. Parameter dan variabel lokal terisolasi dari variabel pemanggil; nilai koleksi yang diberikan sebagai argumen tetap merujuk pada objek koleksi yang sama. Kedalaman pemanggilan dibatasi hingga 100 pada runtime native dan interpreter modular membatasi kedalaman hingga 100.

Contoh:

```pusingcuk
jancuk
fungsi tambah(a, b)
    balek a + b
selesai fungsi
hedeh tambah(2, 3)
selesai jancuk
```

## 11. Komentar

Baris yang setelah spasi awalnya dimulai dengan # dianggap komentar.

### Blok penanganan kesalahan `coba`

Interpreter referensi mendukung `coba ... ketangkep nama ... akhirnya ... selesai coba`. `nama` menjadi variabel lokal pada blok `ketangkep` dan berisi pesan kesalahan sebagai teks; variabel dengan nama sama di scope luar tetap tidak berubah. `akhirnya` bersifat opsional dan dijalankan setelah percobaan/penanganan. Runtime native C belum mendukung blok ini; kode yang memakai fitur tersebut tetap reference-only sampai conformance fixture C tersedia.

## 12. Penanganan kesalahan

Kesalahan sumber dibedakan menjadi **kesalahan sintaks** dan **kesalahan runtime**. Keduanya ditulis ke stderr dan menyertakan nomor baris jika tersedia. Interpreter referensi dan runtime native C menggunakan kode keluar yang sama untuk program: `0` berhasil, `1` kesalahan runtime, dan `2` kesalahan sintaks. CLI Python menggunakan kode `3` untuk berkas sumber yang tidak ditemukan; runtime native menyamakan kode itu untuk kasus yang sama. Pesan internal boleh berbeda, tetapi kelas error dan baris sumber pada fixture lintas-runtime harus sama. Pada CLI interpreter referensi, diagnostik parser menampilkan nama berkas, baris, kolom, potongan sumber, penunjuk, dan saran koreksi dalam Bahasa Indonesia yang sopan. Runtime lain boleh memakai susunan pesan berbeda; kontrak lintas-runtime tetap kelas error, kode keluar, stdout, dan nomor baris. Perubahan detail pesan tidak boleh menyembunyikan penyebab teknis atau menambahkan keyword/alias baru.

## 13. Arah compiler dan portabilitas

Semantik bahasa harus dipisahkan dari implementasi runtime agar program dapat diterjemahkan ke target lain. Baseline perilaku ada di [Kontrak Semantik](docs/SEMANTIC_CONTRACT.md). Front-end dapat mengekspor IR v1 yang mempertahankan AST; format dan validatornya ada di [IR v1](docs/IR_V1.md). Backend C eksperimental mendukung subset integer yang tercatat di [C backend](docs/C_BACKEND.md). Arsitektur target lain dan ABI/FFI dijelaskan di [Arsitektur Compiler dan Interoperabilitas](docs/COMPILER_INTEROP.md), sedangkan tes lintas runtime ada di [Kontrak Fixture Konformansi](docs/CONFORMANCE_FIXTURES.md).

Status implementasi saat ini: front-end dapat mengekspor IR v1, dan CLI `python -m compiler` memiliki target eksperimental `js`, `python`, `html`, `json`, dan `vm`. Backend source C eksperimental tersedia secara terpisah. Target-target tersebut hanya mendukung subset yang berbeda; keberadaan target bukan jaminan kesetaraan semantik atau ABI yang stabil. WebAssembly dan ABI/FFI stabil belum tersedia. Rujuk `docs/COMPILER_TARGETS.md`, `docs/IR_V1.md`, `docs/JS_BACKEND.md`, `docs/BYTECODE_VM.md`, dan `docs/COMPATIBILITY.md` sebelum mengandalkan target tertentu.

## 14. Status spesifikasi dan pembekuan sintaks

Mulai versi 0.5-dev, sintaks dan kosakata yang tercantum dalam dokumen ini dibekukan untuk masa maintenance. Kata kunci inti, alias slang, operator, dan bentuk blok yang sudah tercatat tetap dipertahankan. Kata kunci atau alias baru, perubahan ejaan, maupun perubahan makna sintaks hanya boleh ditambahkan dengan izin eksplisit Founder Pusingcuk.

Interpreter Python modular (`pusingcuk_new.py`, melalui `lexer.py`, `parser.py`, dan `evaluator.py`) adalah implementasi referensi. Perilakunya harus mengikuti dokumen ini; jika ditemukan perbedaan, perbaiki implementasi referensi atau ubah spesifikasi hanya setelah mendapat izin Founder.

Runtime C, backend JavaScript, backend Python hasil kompilasi, dan PVM adalah implementasi pengikut eksperimental. Mereka boleh mendukung subset yang lebih kecil dan tidak menjadi acuan untuk mengubah makna bahasa. Jangan mengklaim kesetaraan penuh hanya karena sebuah target tersedia.

Dokumen ini mencatat perilaku resmi yang dituju. Jika dukungan implementasi belum lengkap, tandai sebagai batas implementasi; jangan diam-diam mengubah makna sintaks.

## 15. Runtime native dan Termux

Runtime C dapat dibangun dengan compiler C11 dan dijalankan sebagai executable tanpa Python untuk subset fitur yang tercantum dalam `docs/NATIVE_RUNTIME.md`. Di Termux, setelah memasang `clang` dan `make`, jalankan `bash scripts/install-termux.sh`, lalu gunakan `pusingcuk-native examples/native/rekap_anggaran.pusingcuk`. Fungsi buatan pengguna tersedia pada runtime native; sistem modul belum tersedia.

## 16. Alias kosakata slang Gen Z dan Gen Alpha

Kosakata slang adalah lapisan gaya bahasa Pusingcuk, bukan bahasa inti terpisah. Daftar alias berikut dibekukan bersama sintaks; jangan menambah alias atau kata kunci baru tanpa izin eksplisit Founder.

Alias dinormalisasi oleh lexer sebelum parsing. Daftar lengkap 23 alias terbagi menjadi dua kelompok. Alias API tambahan bukan bagian dari sintaks inti dan dukungannya bergantung pada target runtime.

### Alias inti (12)

- `jir` → `hedeh` — output
- `adooh` → `kampret` — cabang alternatif
- `gitu` → `selesai` — penutup blok
- `inthiseco` → `jancuk` — pembuka program alternatif
- `janggal` → `bukan` — negasi logika
- `gas` → `jancuk` — pembuka program alternatif
- `spill` → `hedeh` — output
- `bestie` → `lah` — deklarasi variabel
- `valid` → `benar` — boolean benar
- `zonk` → `salah` — boolean salah
- `skip` → `kampret` — cabang alternatif
- `kelar` → `selesai` — penutup blok

### Alias API tambahan (11)

Alias berikut adalah nama alternatif untuk API reference Python; alias tersebut tidak menyatakan kompatibilitas native atau lintas-backend:

- `simpen` → `tulis` — menulis teks ke berkas
- `bongkar` → `baca` — membaca teks dari berkas
- `simpen_json` → `tulis_json` — menulis JSON ke berkas
- `bongkar_json` → `baca_json` — membaca JSON dari berkas
- `impor` → `angkut` — memuat modul lokal
- `waktu` → `jam` — waktu lokal
- `gas_api` → `kepo_internet` — HTTP GET
- `stalking` → `kepo_internet` — HTTP GET
- `kirim_gosip` → `kirim_api` — HTTP POST
- `parse_json` → `jadi_json` — parse JSON
- `kepo` → `tanya` — input pengguna

Alias inti tidak mengubah makna sintaks dan tidak menghapus kata kanonis. Runtime C mandiri hanya diuji terhadap subset alias inti yang tercatat di `docs/NATIVE_RUNTIME.md`. Alias API tambahan tidak membuat kapabilitas menjadi lintas-runtime.


## 17. Bytecode PVM v1 (draft) dan batas keamanan

Eksperimen PVM memiliki assembler dan backend JavaScript/Python. Spesifikasi framing, 19 opcode, operand, dan batas kompatibilitas berada di [docs/PVM_SPEC.md](docs/PVM_SPEC.md). Format ini masih draft: parser sumber C bersifat line-oriented, bukan parser ekspresi penuh, dan kesetaraan seluruh fitur belum dijamin. Jangan menganggap PVM v1 sebagai ABI stabil sebelum fixture konformansi lulus di CI.

**Peringatan keamanan:** backend JavaScript PVM memakai parser ekspresi terbatas dan menolak URL jaringan eksternal; backend Python memakai evaluator AST terbatas. Payload lokal `data:text/plain,` tetap didukung oleh opcode PVM terkait, tetapi operasi file PVM belum dibatasi oleh sandbox sistem operasi. Ini bukan sandbox. Jangan menjalankan bytecode atau program Pusingcuk yang tidak dipercaya.


## Shared builtin metadata

Canonical builtin names, accepted argument counts, Python standard-library allow-lists, backend helper mappings, and per-target support states are recorded in `library/builtin_contract.json`. This is machine-readable implementation metadata connected to the semantic contract; it does not replace the language specification or imply support in targets marked `unsupported` or `not-claimed`. Platform services such as databases, servers, browser APIs, Web3, and blockchain integrations remain explicit adapters/capabilities, not implicit offline core behavior.
