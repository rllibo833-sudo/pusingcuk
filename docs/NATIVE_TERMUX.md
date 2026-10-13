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

Untuk membuat program baru, gunakan ekstensi kanonis `.cuk`:

```sh
nano programku.cuk
pusingcuk-native programku.cuk
```

Berkas `.pusingcuk` tetap bisa dijalankan demi kompatibilitas. Skrip `scripts/build-android.sh` dipakai workflow CI untuk memeriksa cross-build runtime Android NDK. Uji eksekusi emulator tersedia sebagai workflow manual [Android emulator smoke test](../.github/workflows/android-emulator-smoke.yml). Keduanya belum menggantikan pengujian Termux ARM64 pada perangkat fisik.

## 4. Tes sebelum mengembangkan

```sh
make test-native
```

Perintah ini membangun runtime dan menjalankan fixture native, termasuk kamus, input, koleksi, serta kasus error. Sebelum mengirim perubahan, jalankan tes Python juga jika Python tersedia:

```sh
python -m unittest discover -s tests -v
```

## 5. Uji pada perangkat Termux fisik

Cross-build CI bukan bukti eksekusi pada perangkat ARM64. Setelah mengikuti instruksi instalasi di atas, jalankan skrip pemeriksaan integrasi ini langsung di Termux dari root repositori:

```sh
bash scripts/test-termux-device.sh
```

Skrip memeriksa interpreter Python, instalasi CLI ke virtual environment, izin executable dan shebang `.cuk`, input interaktif, kalkulator, build runtime C, versi paket, contoh anggaran, serta exit code untuk file hilang, kesalahan sintaks, dan kesalahan runtime. Instalasi Python melalui `pip` dapat memerlukan akses jaringan. Skrip **belum dijalankan otomatis oleh CI** dan hasilnya hanya dapat diklaim setelah benar-benar dijalankan pada perangkat; catat model perangkat, versi Android/API, arsitektur, versi paket Termux, dan output.

Python reference dan native C memiliki batas fitur berbeda. Contoh kalkulator memakai built-in `bilangan` dan `teks`, yang belum didukung pada native C; jalankan dengan `python pusingcuk_new.py examples/kalkulator.cuk`. Native C memakai `pusingcuk-native` dan hanya menjalankan subset pada matriks runtime.

## 6. Cakupan dan batasan

Runtime native mendukung subset yang didokumentasikan di [matriks runtime](NATIVE_RUNTIME.md), termasuk fungsi buatan pengguna, parameter, nilai balik `balek`, dan rekursi. Sistem modul belum tersedia. Jalankan `make test-native` setelah setiap perubahan untuk memeriksa kompatibilitas executable mandiri.

Runtime ini bukan sandbox. Jangan menjalankan program yang tidak tepercaya dengan asumsi bahwa program tersebut terisolasi.
