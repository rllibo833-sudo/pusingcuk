# pusingcuk

**pusingcuk** adalah bahasa pemrograman eksperimental bergaya esoterik
yang terinspirasi dari slang frustrasi developer Indonesia.

Proyek ini dikembangkan dan dijalankan melalui Android menggunakan
Termux dan Python.

## Status

Versi: 0.2-dev

Implementasi saat ini berupa interpreter Python.

Interpreter aktif: `interpreter.py`.
`interpreter_v01.py` dan `interpreter_v02_backup.py` disimpan sebagai arsip historis, bukan entry point utama.

## Menjalankan program

Jalankan file program:

    pusingcuk program.pusingcuk

Jika perintah pusingcuk belum tersedia:

    python interpreter.py program.pusingcuk

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
- selesai jancuk: mengakhiri program
- tanya: meminta masukan dari pengguna
- fungsi: mendefinisikan fungsi
- balek: mengembalikan nilai dari fungsi

## Nilai dan operator

Nilai yang didukung mencakup string, angka, dan boolean.

- benar dan salah: boolean
- +, -, *, /, //, %: matematika
- ==, !=, <, <=, >, >=: perbandingan
- dan, atau, bukan: logika

### List dan indeks

- List ditulis menggunakan tanda kurung siku, misalnya `[10, 20, 30]`.
- Elemen diakses berdasarkan indeks, dimulai dari 0.
- Elemen list dapat diubah melalui indeks.
- Fungsi `panjang(list)` mengembalikan jumlah elemen.

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

## Batasan saat ini

- Interpreter masih menggunakan Python untuk parsing ekspresi.
- Fungsi buatan pengguna didukung dengan `fungsi` dan `balek`.
- Sistem modul belum tersedia.
- Belum ada sistem tipe statis.
- Belum siap untuk menjalankan kode yang tidak tepercaya.
- Sintaks dan implementasi masih dapat berubah.

## Tujuan proyek

Membangun bahasa pemrograman yang konsisten, dapat diuji,
dan semakin mandiri dari implementasi Python.
# pusingcuk
