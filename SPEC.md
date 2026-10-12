# Spesifikasi Sintaks Pusingcuk v0.4-dev

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
Indeks daftar dan teks dimulai dari 0. Daftar dapat dibaca dan diubah melalui indeks. Nilai kamus dapat dibaca dan diubah melalui kunci.
Fungsi `panjang(nilai)` menerima daftar, teks, kamus, atau rentang dan mengembalikan jumlah elemen, code point UTF-8, entri, atau nilai dalam rentang.
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

Fungsi dideklarasikan dengan `fungsi nama(parameter)` dan diakhiri dengan `selesai fungsi`. Gunakan `balek ekspresi` untuk mengembalikan nilai. Jumlah argumen harus sesuai dengan jumlah parameter. Fungsi tingkat atas dipindai sebelum program berjalan, sehingga pemanggilan sebelum definisi dan rekursi didukung. Parameter dan variabel lokal terisolasi dari variabel pemanggil; nilai koleksi yang diberikan sebagai argumen tetap merujuk pada objek koleksi yang sama. Kedalaman pemanggilan dibatasi hingga 100 pada runtime native dan interpreter modular membatasi kedalaman hingga 100.

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

## 12. Penanganan kesalahan

Interpreter melaporkan kesalahan dengan nomor baris jika tersedia.

## 13. Arah compiler dan portabilitas

Semantik bahasa harus dipisahkan dari implementasi runtime agar program dapat diterjemahkan ke target lain. Baseline perilaku ada di [Kontrak Semantik](docs/SEMANTIC_CONTRACT.md). Front-end dapat mengekspor IR v1 yang mempertahankan AST; format dan validatornya ada di [IR v1](docs/IR_V1.md). Backend C eksperimental mendukung subset integer yang tercatat di [C backend](docs/C_BACKEND.md). Arsitektur target lain dan ABI/FFI dijelaskan di [Arsitektur Compiler dan Interoperabilitas](docs/COMPILER_INTEROP.md), sedangkan tes lintas runtime ada di [Kontrak Fixture Konformansi](docs/CONFORMANCE_FIXTURES.md).

Status implementasi saat ini: front-end dapat mengekspor IR v1, dan CLI `python -m compiler` memiliki target eksperimental `js`, `python`, `html`, `json`, dan `vm`. Backend source C eksperimental tersedia secara terpisah. Target-target tersebut hanya mendukung subset yang berbeda; keberadaan target bukan jaminan kesetaraan semantik atau ABI yang stabil. WebAssembly dan ABI/FFI stabil belum tersedia. Rujuk `docs/COMPILER_TARGETS.md`, `docs/IR_V1.md`, `docs/JS_BACKEND.md`, `docs/BYTECODE_VM.md`, dan `docs/COMPATIBILITY.md` sebelum mengandalkan target tertentu.

## 14. Status spesifikasi

Dokumen ini mencatat perilaku implementasi saat ini.
Fitur yang belum diuji tidak dianggap telah didukung.

## 15. Runtime native dan Termux

Runtime C dapat dibangun dengan compiler C11 dan dijalankan sebagai executable tanpa Python untuk subset fitur yang tercantum dalam `docs/NATIVE_RUNTIME.md`. Di Termux, setelah memasang `clang` dan `make`, jalankan `bash scripts/install-termux.sh`, lalu gunakan `pusingcuk-native examples/native/rekap_anggaran.pusingcuk`. Fungsi buatan pengguna tersedia pada runtime native; sistem modul belum tersedia.

## 16. Alias kosakata slang

Lexer menerima alias berikut dan menormalkannya ke kata kunci kanonis sebelum parsing:

- `jir` → `hedeh`
- `adooh` → `kampret`
- `gitu` → `selesai`
- `inthiseco` → `jancuk`
- `janggal` → `bukan`
- `gas` → `jancuk`
- `spill` → `hedeh`
- `bestie` → `lah`
- `valid` → `benar`
- `zonk` → `salah`
- `skip` → `kampret`
- `kelar` → `selesai`

Alias tidak mengubah makna sintaks dan tidak menghapus kata kunci lama. Runtime C mandiri diuji terhadap subset alias ini; fitur lain pada runtime C belum dinyatakan setara dengan interpreter modular.


## 17. Bytecode PVM v1 (draft) dan batas keamanan

Eksperimen PVM memiliki assembler dan backend JavaScript/Python. Spesifikasi framing, 19 opcode, operand, dan batas kompatibilitas berada di [docs/PVM_SPEC.md](docs/PVM_SPEC.md). Format ini masih draft: parser sumber C bersifat line-oriented, bukan parser ekspresi penuh, dan kesetaraan seluruh fitur belum dijamin. Jangan menganggap PVM v1 sebagai ABI stabil sebelum fixture konformansi lulus di CI.

**Peringatan keamanan:** backend JavaScript PVM memakai parser ekspresi terbatas dan menolak URL jaringan eksternal; backend Python memakai evaluator AST terbatas. Payload lokal `data:text/plain,` tetap didukung oleh opcode PVM terkait, tetapi operasi file PVM belum dibatasi oleh sandbox sistem operasi. Ini bukan sandbox. Jangan menjalankan bytecode atau program Pusingcuk yang tidak dipercaya.


## Experimental statistics builtins

Compiler targets JavaScript, Python, and HTML expose `rata_rata(daftar)` and `median(daftar)`, introduced by the allow-listed Python importer mappings `statistics.mean` and `statistics.median`. Each accepts one non-empty list of finite numbers and rejects booleans. These builtins are an experimental target-specific subset, not a promise of full Python `statistics` compatibility; VM and native C support are not available.
