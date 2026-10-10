# Pusingcuk Native di Termux

Panduan ini membangun executable C Pusingcuk. Setelah build, menjalankan program yang termasuk subset native **tidak membutuhkan Python**. Compiler diperlukan hanya untuk membangun atau membangun ulang executable.

## 1. Persiapan

Di Termux, masuk ke folder repositori Pusingcuk, lalu jalankan:

```sh
pkg update
pkg install git clang make
```

Jika repositori belum ada:

```sh
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
```

Jika sudah ada, masuk ke foldernya dan ambil pembaruan:

```sh
cd ~/pusingcuk
git pull
```

## 2. Bangun runtime native

```sh
bash scripts/install-termux.sh
```

Skrip mengompilasi `native/pusingcuk.c` dan memasang executable ke `$PREFIX/bin/pusingcuk-native`. Skrip tidak memasang paket secara otomatis; pasang `clang` dan `make` jika belum tersedia.

## 3. Jalankan contoh pertama

Dari root repositori:

```sh
pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

Contoh tersebut menggunakan kamus untuk menyimpan kategori pengeluaran, mengiterasi kunci, menghitung total, dan menampilkan sisa anggaran. Nilai contoh bisa kamu ubah langsung di file.

Untuk membuat program baru:

```sh
nano programku.pusingcuk
pusingcuk-native programku.pusingcuk
```

## 4. Tes sebelum mengembangkan

```sh
make test-native
```

Perintah ini membangun runtime dan menjalankan fixture native, termasuk kamus, input, koleksi, serta kasus error. Sebelum mengirim perubahan, jalankan tes Python juga jika Python tersedia:

```sh
python -m unittest discover -s tests -v
```

## 5. Cakupan dan batasan

Runtime native mendukung subset yang didokumentasikan di [matriks runtime](NATIVE_RUNTIME.md), termasuk fungsi buatan pengguna, parameter, nilai balik `balek`, dan rekursi. Sistem modul belum tersedia. Jalankan `make test-native` setelah setiap perubahan untuk memeriksa kompatibilitas executable mandiri.

Runtime ini bukan sandbox. Jangan menjalankan program yang tidak tepercaya dengan asumsi bahwa program tersebut terisolasi.
