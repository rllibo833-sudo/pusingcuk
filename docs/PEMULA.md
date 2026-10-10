# Pusingcuk dari Nol

Panduan ini mengutamakan runtime native agar kamu dapat mulai memakai Pusingcuk di Termux tanpa Python sebagai dependensi saat menjalankan program. Pusingcuk masih dalam pengembangan; runtime native hanya mendukung subset yang tercantum di [matriks kemampuan](NATIVE_RUNTIME.md).

## 1. Siapkan Termux

Gunakan Termux dari sumber yang terpelihara, lalu jalankan di shell Termux:

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

Skrip memasang executable ke `$PREFIX/bin/pusingcuk-native`. Compiler diperlukan saat membangun ulang, tetapi tidak diperlukan untuk setiap kali menjalankan program.

## 2. Jalankan program contoh pertama

```sh
pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

Contoh menghitung anggaran menggunakan kamus, perulangan, kondisi, dan fungsi buatan pengguna. Nilai keluaran yang diharapkan antara lain total pengeluaran `1200000`, sisa anggaran `1300000`, dan status anggaran aman.

Untuk memastikan build dan fixture native lulus:

```sh
make test-native
```

## 3. Buat program sendiri

Buat berkas baru dengan editor teks:

```sh
nano halo.pusingcuk
```

Masukkan kode berikut:

```pusingcuk
jancuk
lah nama = "Pusingcuk"
hedeh "Halo, " + nama
selesai jancuk
```

Simpan berkas di nano dengan **Ctrl+O**, tekan **Enter**, lalu keluar dengan **Ctrl+X**. Jalankan:

```sh
pusingcuk-native halo.pusingcuk
```

Keluaran yang diharapkan:

```text
Halo, Pusingcuk
```

Contoh fungsi:

```pusingcuk
jancuk
fungsi tambah(a, b)
    balek a + b
selesai fungsi
hedeh tambah(20, 22)
selesai jancuk
```

Simpan sebagai `fungsi.pusingcuk`, lalu jalankan `pusingcuk-native fungsi.pusingcuk`. Keluaran yang diharapkan adalah `42`.

## 4. Belajar input, kondisi, dan perulangan

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

Simpan dan jalankan seperti contoh sebelumnya. Runtime native membaca satu baris dari input standar. Cobalah mengubah kondisi dan amati perbedaannya.

## 5. Jika terjadi kesalahan

- Baca seluruh pesan `Kesalahan baris ...`; nomor baris membantu menemukan kode bermasalah.
- Pastikan berkas benar-benar disimpan dan nama/path berkas tepat.
- Periksa apakah fitur yang digunakan tercantum sebagai teruji di `docs/NATIVE_RUNTIME.md`.
- Jangan menganggap runtime native sebagai sandbox; jangan jalankan kode tak tepercaya.
- Saat meminta bantuan, kirim pesan error dan contoh kode minimal yang memunculkannya. Hapus rahasia/token dari log sebelum membagikannya.

## 6. Perbarui Pusingcuk

Dari shell Termux (bukan di dalam program Pusingcuk):

```sh
cd ~/pusingcuk
git pull --ff-only
bash scripts/install-termux.sh
```

Jika kamu sudah mengubah kode sumber sendiri, commit atau simpan perubahanmu sebelum menarik pembaruan. Opsi `--ff-only` mencegah Git membuat merge commit otomatis ketika riwayat lokal dan remote berbeda.

## 7. Apakah Python diperlukan?

- **Menjalankan executable native:** tidak membutuhkan Python.
- **Membangun executable:** membutuhkan `clang` dan `make`.
- **Menjalankan interpreter modular dan unit test Python:** membutuhkan Python.
- **Sistem modul, paket standar lengkap, serta dukungan backend/frontend penuh:** belum tersedia hanya dengan runtime native saat ini.

Pusingcuk dirancang agar bisa dipelajari pemula dan dikembangkan secara profesional, tetapi jangan menganggap kemampuan Python/JavaScript sudah tersedia sebelum ada implementasi dan tes konformansi.
