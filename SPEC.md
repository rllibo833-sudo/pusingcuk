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
Kamus ditulis dengan kurung kurawal dan pasangan kunci-nilai, misalnya `{"nama": "Budi", "umur": 20}`.
Indeks daftar dan teks dimulai dari 0. Daftar dapat dibaca dan diubah melalui indeks. Nilai kamus dapat dibaca dan diubah melalui kunci.
Fungsi `panjang(nilai)` menerima daftar, teks, atau kamus dan mengembalikan jumlah elemen atau karakter.
Kunci kamus harus dapat digunakan sebagai kunci. Kunci yang tidak ditemukan dan indeks di luar batas menghasilkan kesalahan.

## 9. Perulangan untuk

Contoh:

    jancuk
    untuk angka dalam rentang(1, 5)
        hedeh angka
    selesai untuk
    selesai jancuk

Perulangan modular untuk nama dalam koleksi mengunjungi setiap elemen daftar atau teks, setiap kunci kamus, atau setiap bilangan dalam rentang. Runtime native C yang diuji mendukung iterasi list, teks (per code point UTF-8), dan `rentang()`; iterasi kamus belum tersedia di native.

`rentang(akhir)`, `rentang(mulai, akhir)`, dan `rentang(mulai, akhir, langkah)` menerima satu sampai tiga argumen bilangan bulat. Batas akhir tidak termasuk hasil. Langkah tidak boleh nol. Setiap perulangan dibatasi 10000 iterasi dan seluruh program dibatasi 100000 langkah native/modular.

## 10. Fungsi buatan pengguna

Fungsi dideklarasikan dengan `fungsi nama(parameter)` dan diakhiri dengan `selesai fungsi`. Gunakan `balek ekspresi` untuk mengembalikan nilai. Jumlah argumen harus sesuai dengan jumlah parameter. Kedalaman pemanggilan fungsi dibatasi oleh interpreter.

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

## 13. Status spesifikasi

Dokumen ini mencatat perilaku implementasi saat ini.
Fitur yang belum diuji tidak dianggap telah didukung.

## 14. Alias kosakata slang

Lexer menerima alias berikut dan menormalkannya ke kata kunci kanonis sebelum parsing:

- `jir` → `hedeh`
- `adooh` → `kampret`
- `gitu` → `selesai`
- `inthiseco` → `jancuk`
- `janggal` → `bukan`

Alias tidak mengubah makna sintaks dan tidak menghapus kata kunci lama. Runtime C mandiri diuji terhadap subset alias ini; fitur lain pada runtime C belum dinyatakan setara dengan interpreter modular.
