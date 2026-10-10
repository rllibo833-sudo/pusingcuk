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

`tanya` menampilkan prompt string dan membaca jawaban sebagai teks dari input standar. Input interaktif melalui Pusingcuk Studio belum diverifikasi.

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

### List dan indeks

List ditulis menggunakan tanda kurung siku, misalnya `[10, 20, 30]`.
Indeks dimulai dari 0. Elemen dapat dibaca dan diubah melalui indeks.
Fungsi `panjang(list)` mengembalikan jumlah elemen.
Akses indeks di luar batas menghasilkan kesalahan.

## 9. Fungsi buatan pengguna

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

## 10. Komentar

Baris yang setelah spasi awalnya dimulai dengan # dianggap komentar.

## 11. Penanganan kesalahan

Interpreter melaporkan kesalahan dengan nomor baris jika tersedia.

## 12. Status spesifikasi

Dokumen ini mencatat perilaku implementasi saat ini.
Fitur yang belum diuji tidak dianggap telah didukung.


## 13. Koleksi dan perulangan untuk (0.4-dev)

Kamus ditulis dengan kurung kurawal dan pasangan kunci: nilai, contohnya {"nama": "Budi", "umur": 20}. Kunci dapat berupa nilai yang bisa digunakan sebagai kunci kamus. Nilai dapat diambil dan diubah melalui indeks kamus. Fungsi panjang menerima daftar, teks, atau kamus.

Perulangan untuk nama dalam koleksi menjalankan badan perulangan untuk setiap elemen daftar atau teks, setiap kunci kamus, atau setiap bilangan dari rentang.

rentang(akhir), rentang(mulai, akhir), dan rentang(mulai, akhir, langkah) menerima satu sampai tiga argumen bilangan bulat. Batas akhir tidak termasuk hasil; langkah tidak boleh nol. Iterasi tunduk pada batas total langkah evaluator.

Catatan: fitur ini diterapkan pada pipeline Python modular. Kesetaraan native C belum diverifikasi.