# Indeks contoh PusingCuk

Berkas baru sebaiknya memakai ekstensi kanonis `.cuk`. Berkas `.pusingcuk` lama tetap tersedia demi kompatibilitas; ekstensi saja tidak menjamin fitur tersedia pada semua runtime.

## Contoh sumber kanonis (.cuk)

Jalankan dari direktori akar repositori menggunakan interpreter referensi Python:

```sh
python pusingcuk_new.py examples/halo_dunia.cuk
python pusingcuk_new.py examples/keuangan_sederhana.cuk
python pusingcuk_new.py examples/warung.cuk
python pusingcuk_new.py examples/rekap_anggaran.cuk
python pusingcuk_new.py examples/kalkulator.cuk
```

| Berkas | Kegunaan | Catatan |
|---|---|---|
| `halo_dunia.cuk` | Input interaktif dan output teks | Meminta nama lalu menyapa pengguna. Shebang dapat dipakai setelah CLI `pusingcuk` terpasang dan tersedia di `PATH`. |
| `keuangan_sederhana.cuk` | Fungsi, konversi angka, loop, kondisi, dan input | Jika menyetujui penyimpanan, menulis `keuangan_sederhana.txt` sebagai berkas relatif dalam project root. |
| `warung.cuk` | Variabel, operasi matematika, kondisi | Contoh statis sederhana tanpa akses jaringan atau file. |
| `rekap_anggaran.cuk` | Kamus, fungsi buatan, total pengeluaran, dan kondisi | Contoh kalkulasi anggaran menggunakan kamus. |
| `kalkulator.cuk` | Input interaktif, konversi angka, kondisi, dan operasi dasar | Menggunakan keyword inti `njir`, `kampret`, dan `selesai`; bukan keyword `jika`. Dijalankan pada interpreter referensi karena built-in konversi belum tersedia di native C. Uji pembagian nol dan input nonnumerik. |

Untuk memeriksa sintaks tanpa menjalankan program, tambahkan `--check`, misalnya:

```sh
python pusingcuk_new.py --check examples/halo_dunia.cuk
```

## Contoh runtime native C

Runtime native C adalah target berbeda dengan subset fitur tersendiri. Bangun dan jalankan contoh native dari akar repositori:

```sh
make native
./pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

Contoh native masih memakai ekstensi kompatibilitas lama dan alias sintaks yang diuji pada runtime C. Kalkulator memakai `bilangan` dan `teks`, sehingga contoh itu untuk interpreter Python; native C belum mendukung built-in konversi tersebut. Jangan menganggap modul, HTTP, atau file I/O tersedia pada runtime native hanya karena interpreter Python mendukungnya.

## Contoh kompatibilitas (.pusingcuk)

Contoh ini dipertahankan untuk demonstrasi API yang sudah ada dan kompatibilitas sumber lama:

| Berkas | Kegunaan | Efek samping / prasyarat |
|---|---|---|
| `compat/halo.pusingcuk` | Padanan contoh halo untuk ekstensi lama | Tidak memerlukan jaringan. |
| `file_io.pusingcuk` | Membaca dan menulis catatan warung | Menulis `warung.txt`; perhatikan berkas bernama sama agar tidak tertimpa. |
| `database.pusingcuk` | Serialisasi dan pembacaan JSON lokal | Menulis `database.json`; perhatikan berkas bernama sama agar tidak tertimpa. |
| `modular.pusingcuk` + `utils.pusingcuk` | Impor modul lokal dan penanganan error | Jalankan dari akar repositori supaya jalur modul dan berkas sesuai contoh. |
| `rekap_anggaran.pusingcuk` | Contoh kalkulasi anggaran versi lama | Contoh CLI interpreter Python. |
| `viral_bot.pusingcuk` | Serialisasi JSON dan contoh POST HTTP | Mengirim payload demo ke `https://httpbin.org/post`. Jalankan hanya jika memang ingin mengirim permintaan eksternal. |

Contoh jaringan bersifat **opsional**, bukan syarat penggunaan atau pengujian dasar:

- `internet.pusingcuk` melakukan HTTP GET ke GitHub API dan wttr.in.
- `viral_bot.pusingcuk` melakukan HTTP POST ke httpbin.org.

Permintaan tersebut memerlukan jaringan dan dapat mengirim permintaan ke layanan pihak ketiga. CI inti tidak bergantung pada koneksi eksternal untuk contoh ini. Jangan masukkan token, kata sandi, data pribadi, atau informasi sensitif ke dalam contoh jaringan.

## Cara menjalankan contoh yang menulis berkas

Jalankan contoh file/JSON di direktori kerja sementara atau cadangkan berkas target terlebih dahulu. Walaupun evaluator Python membatasi operasi file relatif terhadap project root, batas itu bukan sandbox sistem operasi dan tidak menggantikan kehati-hatian terhadap penimpaan berkas. Jangan menjalankan program atau bytecode yang tidak dipercaya.

Lihat juga [spesifikasi bahasa](../SPEC.md), [katalog built-in](../docs/language/BUILTINS.md), [matriks kompatibilitas](../docs/COMPATIBILITY.md), dan [kebijakan keamanan](../SECURITY.md).
