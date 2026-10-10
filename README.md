# Pusingcuk

Pusingcuk adalah bahasa pemrograman eksperimental dengan kosakata ramah bahasa Indonesia dan slang lokal. Tujuannya adalah mudah dipelajari, tetap dapat dikembangkan secara serius, dan perlahan bisa dijalankan native tanpa Python saat runtime.

## Status proyek

Versi: 0.4-dev.

Saat ini ada dua jalur eksekusi:
- **Interpreter modular Python** sebagai jalur referensi pengembangan: `pusingcuk_new.py`, dengan lexer, parser, AST, dan evaluator.
- **Runtime native C** untuk subset bahasa yang sudah memiliki fixture. Setelah dikompilasi, executable native berjalan tanpa Python.

Kedua jalur belum sepenuhnya setara. Jangan menganggap fitur yang tersedia di interpreter modular otomatis tersedia di native. Daftar kemampuan dan batasnya ada di [matriks runtime native](docs/NATIVE_RUNTIME.md). Sistem modul belum tersedia.

Implementasi historis yang tidak menjadi entry point utama disimpan di `archive/legacy/` untuk referensi saja. File arsip tidak termasuk jalur yang didukung dan tidak boleh dijadikan dasar klaim fitur.

## Mulai untuk pemula

Ikuti [Panduan Pusingcuk dari Nol](docs/PEMULA.md). Panduan itu mengutamakan jalur Termux native tanpa Python untuk menjalankan program.

## Jalankan interpreter modular (opsional)

Jalur ini memerlukan Python:

```sh
python pusingcuk_new.py program.pusingcuk
python terminal.py
```

Terminal interaktif menerima `:bantuan`, `:contoh`, `:batal`, dan `:keluar`. Input `tanya` dimasukkan saat program berjalan.

## Runtime native tanpa Python

Setelah memasang compiler C11 dan Make:

```sh
make native
make run-native FILE=tests/native/for_range.pusingcuk
make test-native
```

Di Termux, gunakan:

```sh
pkg update
pkg install git clang make
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
bash scripts/install-termux.sh
pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

Compiler dibutuhkan untuk build, bukan untuk setiap kali menjalankan executable. Runtime native mendukung nilai dasar, list, teks, kamus, kondisi, perulangan, input standar `tanya`, `panjang`, `rentang`, serta fungsi buatan pengguna dengan parameter dan `balek`. Deklarasi fungsi tingkat atas dipindai sebelum eksekusi, sehingga fungsi dapat dipanggil sebelum definisinya dan dapat melakukan rekursi. Detail batas runtime tercatat di [matriks runtime](docs/NATIVE_RUNTIME.md). Runtime ini **bukan sandbox** untuk kode tak tepercaya.

## Contoh program

```pusingcuk
jancuk
lah nama = "Budi"
lah umur = 20

hedeh "Halo, dunia!"
hedeh nama

njir umur >= 18 dan benar
    hedeh "Sudah dewasa"
kampret
    hedeh "Masih di bawah umur"
selesai njir

lah i = 1
mumet i <= 3
    hedeh i
    i = i + 1
selesai mumet

selesai jancuk
```

## Kosakata utama

- `jancuk`: memulai program
- `hedeh`: menampilkan nilai
- `lah`: mendeklarasikan variabel
- `njir`: memulai kondisi
- `kampret`: cabang alternatif
- `mumet`: memulai perulangan while
- `untuk nama dalam koleksi`: perulangan koleksi
- `tanya`: meminta masukan teks
- `fungsi`: mendefinisikan fungsi
- `balek`: mengembalikan nilai fungsi
- `selesai jancuk`: mengakhiri program

### Alias slang

| Kata | Setara dengan | Fungsi |
|---|---|---|
| `jir` | `hedeh` | Menampilkan nilai |
| `adooh` | `kampret` | Cabang alternatif |
| `gitu` | `selesai` | Menutup blok |
| `inthiseco` | `jancuk` | Memulai program |
| `janggal` | `bukan` | Negasi logika |

Alias tidak menghapus kata lama. Penjelasan ada di [Kosakata Slang Pusingcuk](docs/KOSAKATA_GENZ.md).

## Koleksi dan operator

Nilai yang didukung mencakup teks, angka, boolean, daftar, dan kamus. Operator matematika: `+`, `-`, `*`, `/`, `//`, `%`. Perbandingan: `==`, `!=`, `<`, `<=`, `>`, `>=`. Logika: `dan`, `atau`, `bukan`.

- Daftar menggunakan tanda siku, misalnya `[10, 20, 30]`.
- Kamus menggunakan pasangan kunci-nilai, misalnya `{"nama": "Budi", "umur": 20}`.
- Indeks daftar dan teks dimulai dari 0.
- `panjang(nilai)` menerima jenis nilai yang tercantum pada matriks runtime.
- `rentang(akhir)`, `rentang(mulai, akhir)`, dan `rentang(mulai, akhir, langkah)` menghasilkan rentang bilangan bulat; batas akhir tidak termasuk dan langkah tidak boleh nol.

## Pengujian

Interpreter modular:

```sh
python -m unittest discover -s tests -v
```

Runtime native:

```sh
make test-native
```

Jika perubahan menyentuh kedua jalur, jalankan keduanya. Tes CI Ubuntu tidak menggantikan pengujian fisik Termux.

## Batasan saat ini

- Interpreter modular masih menggunakan Python.
- Runtime native hanya mendukung subset yang didokumentasikan dan diuji.
- Sistem modul, tipe statis, dan pustaka backend/frontend lengkap belum tersedia.
- Input interaktif `tanya` di Pusingcuk Studio belum diverifikasi.
- Bahasa ini belum siap untuk menjalankan kode tak tepercaya.

## Kontribusi

Baca [CONTRIBUTING.md](CONTRIBUTING.md) sebelum membuka PR. Gunakan branch terfokus, sertakan tes dan dokumentasi, jangan commit cache/binary/rahasia, dan tunggu review sebelum merge.
