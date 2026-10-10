# pusingcuk

**pusingcuk** adalah bahasa pemrograman eksperimental bergaya esoterik
yang terinspirasi dari slang frustrasi developer Indonesia.

Proyek ini dikembangkan dan dijalankan melalui Android menggunakan
Termux dan Python.

## Status

Versi: 0.4-dev

Implementasi saat ini berupa interpreter Python.

Entry point pipeline Python modular: `pusingcuk_new.py` (lexer, parser, AST, evaluator). Pusingcuk Studio memakai pipeline ini. `interpreter.py` tetap merupakan implementasi lama.
`interpreter_v01.py` dan `interpreter_v02_backup.py` disimpan sebagai arsip historis, bukan entry point utama.

## Mulai untuk pemula

Belum pernah coding? Mulai dari [Panduan Pusingcuk dari Nol](docs/PEMULA.md). Isinya cara membuka terminal di Termux, mengetik program pertama, memakai `tanya`, dan membaca error tanpa perlu mengunduh ZIP.

## Terminal interaktif sederhana

Jalankan terminal Pusingcuk dari folder repositori:

    python terminal.py

Ketik program dari `jancuk` sampai `selesai jancuk`. Terminal menjalankan program setelah penutup itu dimasukkan. Gunakan `:bantuan`, `:contoh`, `:batal`, atau `:keluar` untuk perintah terminal. Input `tanya` dimasukkan setelah program mulai dijalankan.

## Runtime native tanpa Python

Runtime C mandiri dapat dikompilasi dan dijalankan tanpa interpreter Python untuk subset sintaks yang didukung:

    make native
    make run-native FILE=tests/native/for_range.pusingcuk
    make test-native

Compiler C11 diperlukan saat build; menjalankan executable hasil build tidak memerlukan Python. Runtime native yang diuji mendukung nilai dasar, list, teks, indeks list/teks (berdasarkan code point UTF-8), baca/ubah indeks kamus, kondisi, `mumet`, perulangan `untuk` pada list/teks/kamus/rentang, input standar `tanya`, `panjang`, dan `rentang`. Fungsi buatan pengguna masih belum tersedia di native. Lihat [matriks kemampuan runtime native](docs/NATIVE_RUNTIME.md) untuk status fitur dan batasannya. Runtime ini **bukan sandbox** untuk kode tak tepercaya; dukungan fitur dibuktikan lewat fixture native, bukan diasumsikan dari interpreter modular.

## Menjalankan program

Jalankan file program:

    pusingcuk program.pusingcuk

Jika perintah pusingcuk belum tersedia:

    python pusingcuk_new.py program.pusingcuk

## Contoh program

    jancuk

    lah nama = "Budi"
    lah umur = 20

    hedeh "Halo, dunia!"
    hedeh nama

    njir umur >= 18 dan benar
        hedeh "Sudah dewasa"
    kampret
        hedeh "Belum dewasa"
    selesai njir

    lah i = 1
    mumet i <= 3
        hedeh i
        i = i + 1
    selesai mumet

    selesai jancuk

## Keyword

- jancuk: memulai program
- hedeh: mencetak nilai
- lah: mendeklarasikan variabel
- njir: memulai kondisi
- kampret: cabang alternatif
- selesai njir: mengakhiri kondisi
- mumet: memulai perulangan while
- selesai mumet: mengakhiri perulangan
- untuk nama dalam koleksi: memulai perulangan koleksi
- selesai untuk: mengakhiri perulangan koleksi
- selesai jancuk: mengakhiri program
- tanya: meminta masukan teks dari pengguna, misalnya `tanya nama = "Nama? "`
- fungsi: mendefinisikan fungsi
- balek: mengembalikan nilai dari fungsi

### Kosakata Gen Z dan Gen Alpha

Pusingcuk menerima kata slang sebagai alias yang tetap kompatibel dengan sintaks lama:

| Kata | Setara dengan | Fungsi |
|---|---|---|
| `jir` | `hedeh` | Menampilkan nilai |
| `adooh` | `kampret` | Cabang alternatif pada kondisi |
| `gitu` | `selesai` | Menutup blok, diikuti jenis blok |
| `inthiseco` | `jancuk` | Memulai program; penutupnya `gitu inthiseco` |
| `janggal` | `bukan` | Negasi logika |

Contoh:

```pusingcuk
inthiseco
lah umur = 17
njir janggal (umur >= 18)
    jir "Belum dewasa, jir."
adooh
    jir "Sudah dewasa."
gitu njir
gitu inthiseco
```

Daftar istilah dan alasan pemilihannya ada di [Kosakata Slang Pusingcuk](docs/KOSAKATA_GENZ.md). Alias ini tidak menghapus kata lama, jadi program yang sudah ada tetap kompatibel.

## Nilai dan operator

Nilai yang didukung mencakup teks, angka, boolean, daftar, dan kamus. Built-in `panjang` menghitung panjang teks, daftar, atau kamus; `rentang` membuat rentang bilangan bulat untuk perulangan.

- benar dan salah: boolean
- +, -, *, /, //, %: matematika
- ==, !=, <, <=, >, >=: perbandingan
- dan, atau, bukan: logika

### Daftar, kamus, teks, dan indeks

- Daftar ditulis dengan tanda kurung siku, misalnya `[10, 20, 30]`.
- Kamus ditulis dengan pasangan `kunci: nilai`, misalnya `{"nama": "Budi", "umur": 20}`.
- Indeks daftar dan teks dimulai dari 0; nilai daftar dapat diubah melalui indeks.
- Nilai kamus dapat dibaca dan diubah melalui kunci.
- `panjang(nilai)` menerima daftar, teks, atau kamus.

### Perulangan `untuk` dan rentang

- Bentuk: `untuk nama dalam koleksi`, ditutup dengan `selesai untuk`.
- Koleksi yang didukung: daftar, teks, kamus (iterasi menghasilkan kunci), dan hasil `rentang(...)`.
- `rentang(akhir)`, `rentang(mulai, akhir)`, atau `rentang(mulai, akhir, langkah)` menerima bilangan bulat; batas akhir tidak termasuk dan langkah tidak boleh nol.
- Perulangan tunduk pada batas total langkah evaluator.

Contoh:

```pusingcuk
jancuk
untuk angka dalam rentang(1, 5)
    hedeh angka
selesai untuk
selesai jancuk
```

Contoh program lain tersedia di `examples/rekap_anggaran.pusingcuk`.

## Contoh masukan pengguna

```pusingcuk
jancuk
tanya nama = "Siapa nama kamu? "
hedeh "Halo, " + nama
selesai jancuk
```

## Pengujian

Jalankan seluruh tes:

    python -m unittest discover -s tests -v

Tes terminal juga memeriksa contoh `:contoh`, program buatan sendiri, dan alur input `tanya`.

## Batasan saat ini

- Interpreter masih menggunakan Python untuk parsing ekspresi.
- Fungsi buatan pengguna didukung dengan `fungsi` dan `balek`.
- Input interaktif `tanya` pada Studio belum terverifikasi; gunakan CLI untuk input interaktif.
- Sistem modul belum tersedia.
- Belum ada sistem tipe statis.
- Belum siap untuk menjalankan kode yang tidak tepercaya.
- Sintaks dan implementasi masih dapat berubah.

## Tujuan proyek

Membangun bahasa pemrograman yang konsisten, dapat diuji,
dan semakin mandiri dari implementasi Python.
