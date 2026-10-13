# Pusingcuk dari Nol

Yuk mulai dari program kecil, lalu naik pelan-pelan ke fungsi dan proyek mini. Panduan ini memakai ekstensi kanonis `.cuk` untuk program baru dan mengutamakan executable native supaya kamu bisa menjalankan program tanpa Python setelah Pusingcuk dibangun. Berkas `.pusingcuk` lama tetap didukung. Runtime native masih berkembang dan hanya mendukung fitur yang tercantum di [matriks kemampuan](NATIVE_RUNTIME.md).

Gaya dokumentasi mengikuti [Panduan Gaya Bahasa](GAYA_BAHASA.md): santai, jelas, dan tidak mengorbankan ketepatan teknis.

## 1. Siapkan alat di Android / Termux

Gunakan Termux dari sumber yang terpelihara. Jalankan perintah berikut di shell Termux:

```sh
pkg update
pkg install git clang make
```

Unduh kode sumber:

```sh
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
```

Bangun dan pasang executable native:

```sh
bash scripts/install-termux.sh
```

Selesai build, executable dipasang sebagai `pusingcuk-native`. Compiler dibutuhkan saat membangun ulang, bukan setiap kali menjalankan program.

## 2. Jalankan contoh pertama

```sh
pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

Program contoh menghitung anggaran menggunakan kamus, perulangan, kondisi, dan fungsi. Beberapa hasil yang diharapkan adalah total pengeluaran `1200000`, sisa anggaran `1300000`, dan status anggaran aman.

Kalau ingin memastikan build dan fixture native lulus, jalankan:

```sh
make test-native
```

## 3. Buat program halo

Buat file baru:

```sh
nano halo.cuk
```

Isi dengan kode ini:

```pusingcuk
jancuk
lah nama = "Pusingcuk"
hedeh "Halo, " + nama
selesai jancuk
```

Simpan di nano dengan **Ctrl+O**, tekan **Enter**, lalu keluar dengan **Ctrl+X**. Jalankan:

```sh
pusingcuk-native halo.cuk
```

Hasilnya:

```text
Halo, Pusingcuk
```

**Bedah singkat:**
- `jancuk` menandai awal program.
- `lah nama = ...` membuat variabel bernama `nama`.
- `hedeh` menampilkan nilai.
- `selesai jancuk` menandai akhir program.

## 4. Buat fungsi pertamamu

Fungsi adalah blok kode yang bisa dipanggil kembali. Contoh berikut menjumlahkan dua angka:

```pusingcuk
jancuk
fungsi tambah(a, b)
    balek a + b
selesai fungsi

hedeh tambah(20, 22)
selesai jancuk
```

Simpan sebagai `fungsi.cuk`, lalu jalankan:

```sh
pusingcuk-native fungsi.cuk
```

Hasil yang diharapkan adalah `42`.

**Mini-challenge:** ganti `20` dan `22` dengan dua angka lain. Sebelum menjalankan program, coba tebak hasilnya.

## 5. Minta input dan pilih respons

```pusingcuk
jancuk
tanya nama = "Siapa nama kamu? "
njir nama == ""
    hedeh "Nama belum diisi"
kampret
    hedeh "Halo, " + nama
selesai njir
selesai jancuk
```

Program membaca satu baris teks. Jika input kosong, program menampilkan pesan bahwa nama belum diisi. Jika tidak kosong, program menyapa nama tersebut.

**Mini-challenge:** ubah kalimat sapaan. Jalankan lagi dan lihat apakah output berubah sesuai editmu.

## 5.1 Kalkulator sederhana

Repositori juga menyediakan kalkulator interaktif yang meminta dua angka dan operasi `+`, `-`, `*`, atau `/`:

```sh
python pusingcuk_new.py examples/kalkulator.cuk
```

Kalkulator ini memakai keyword resmi `njir`, `kampret`, dan `selesai njir`, bukan keyword `jika`. Ia juga menunjukkan penanganan input nonnumerik dan pembagian dengan nol. Contoh tersebut memakai built-in konversi yang belum tersedia di runtime native C, jadi jalankan dengan interpreter Python. Perbedaan ini disengaja dan dijelaskan dalam [matriks kompatibilitas](COMPATIBILITY.md).

## 6. Coba perulangan

```pusingcuk
jancuk
lah i = 1
mumet i <= 3
    hedeh i
    i = i + 1
selesai mumet
selesai jancuk
```

Program menampilkan angka 1, 2, dan 3. Variabel `i` bertambah satu pada setiap putaran. Kondisi `i <= 3` membuat perulangan berhenti setelah angka 3.

## 7. Kalau program gagal jalan

- Baca pesan `Kesalahan baris ...`; nomor baris membantu menemukan masalah.
- Pastikan file sudah disimpan dan path-nya benar.
- Periksa apakah fitur yang digunakan termasuk fitur native teruji di [matriks runtime](NATIVE_RUNTIME.md).
- Jika diminta memasukkan teks, ketik input di terminal lalu tekan Enter.
- Saat meminta bantuan, kirim pesan error dan contoh kode terkecil yang masih memunculkan masalah. Hapus token, kata sandi, dan data pribadi dari log.

Runtime native bukan sandbox. Jangan menjalankan program yang tidak dipercaya dengan hak akses penting.

## 8. Perbarui Pusingcuk

Di shell Termux, dari direktori repositori:

```sh
cd ~/pusingcuk
git pull --ff-only
bash scripts/install-termux.sh
```

Jika kamu mengubah kode sumber sendiri, simpan atau commit perubahanmu sebelum menarik pembaruan. Opsi `--ff-only` mencegah Git membuat merge commit otomatis saat riwayat lokal dan remote berbeda.

## 9. Apakah Python diperlukan?

- **Menjalankan executable native:** tidak membutuhkan Python.
- **Membangun executable:** membutuhkan `clang` dan `make`.
- **Menjalankan interpreter modular dan unit test Python:** membutuhkan Python.
- **Menjalankan Pusingcuk Studio saat ini:** bridge web lokal membutuhkan Python; program yang dieksekusi tetap melalui runtime native C.
- **Sistem modul, pustaka standar lengkap, dan tooling tingkat lanjut:** belum tersedia sepenuhnya di runtime native.

Langkah berikutnya setelah nyaman dengan contoh dasar adalah mempelajari [kosakata slang](KOSAKATA_GENZ.md), [kemampuan runtime native](NATIVE_RUNTIME.md), dan [kontrak kompatibilitas](COMPATIBILITY.md). Jangan menganggap fitur dari Python atau JavaScript otomatis tersedia di Pusingcuk.
