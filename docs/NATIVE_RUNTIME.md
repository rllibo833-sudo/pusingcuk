# Runtime Native Pusingcuk

## Tujuan

Runtime C adalah jalur eksekusi mandiri untuk program Pusingcuk yang termasuk dalam subset native teruji. Setelah dikompilasi, executable berjalan tanpa Python. Build membutuhkan compiler C11 dan library matematika sistem.

## Kemampuan yang memiliki fixture native

| Kemampuan | Status |
|---|---|
| Alias slang: `jir`, `adooh`, `gitu`, `inthiseco`, `janggal` | Teruji |
| Variabel, angka, teks, boolean, operator dasar | Teruji |
| List, baca/ubah indeks list | Teruji |\n| Batas list 256 item dan penolakan item ke-257 | Fixture native mengharapkan error |
| Indeks teks berdasarkan code point UTF-8 | Teruji untuk teks UTF-8 valid |
| Kondisi `njir` / `adooh` dan loop `mumet` | Teruji |
| `untuk` pada list, teks, kamus (menghasilkan kunci), dan `rentang()` | Teruji |
| Built-in `panjang()` dan `rentang()` | Teruji pada argumen yang didukung |
| `tanya nama = "Prompt"` dari stdin | Teruji melalui pipe dan CLI |
| Literal kamus, kunci teks/angka/boolean, baca/ubah/tambah kunci | Teruji |\n| Batas kamus 256 entri dan penolakan entri ke-257 | Fixture native mengharapkan error |
| `panjang(kamus)`, truthiness kamus kosong/terisi, iterasi kunci | Teruji |
| Error untuk kunci yang tidak didukung dan kunci yang tidak ditemukan | Teruji |
| Fungsi buatan pengguna (`fungsi`, parameter, `balek`, rekursi) | Teruji oleh CI GCC/Clang di Ubuntu; perangkat Termux nyata belum diverifikasi |
| Sistem modul | Belum tersedia di native |

Fixture kapasitas koleksi ada di `tests/native/list_overflow.pusingcuk` dan `tests/native/dictionary_overflow.pusingcuk`; keduanya memastikan penambahan melewati 256 item/entri ditolak. Fixture kamus sukses berada di `tests/native/dictionaries.pusingcuk`; kasus kunci tidak valid dan kunci hilang masing-masing ada di `tests/native/dictionary_invalid_key.pusingcuk` dan `tests/native/dictionary_missing_key.pusingcuk`. Fixture fungsi dan rekursi ada di `tests/native/functions.pusingcuk`; jumlah argumen yang salah diuji di `tests/native/function_wrong_arity.pusingcuk`. Semuanya dijalankan oleh `make test-native`.

## Contoh aplikasi native

Contoh rekap anggaran yang memakai fungsi buatan, kamus, iterasi kunci, dan perhitungan total tersedia di `examples/native/rekap_anggaran.pusingcuk`. Panduan pemasangan executable pada Termux tersedia di [NATIVE_TERMUX.md](NATIVE_TERMUX.md).

## Build dan jalankan

```sh
make native
make run-native FILE=tests/native/strings_input.pusingcuk
make test-native
```

Binary default ditempatkan di root repositori sebagai `pusingcuk-native` (sesuai `NATIVE_BIN` pada Makefile). Atur `NATIVE_BIN` jika ingin menyimpan binary di lokasi lain. Binary hasil build dan keluaran tes adalah artefak lokal, bukan berkas yang perlu di-commit. Untuk menguji input, program membaca satu baris dari stdin; batas panjang teks mengikuti buffer native saat ini.

## Batasan dan keamanan

- Kamus native dibatasi hingga 256 entri dan menerima kunci teks, angka, atau boolean.
- Kunci yang tidak didukung serta pembacaan kunci yang tidak ditemukan menghasilkan error.
- Runtime native C belum setara penuh dengan pipeline modular Python. Fungsi native dibatasi 128 deklarasi tingkat atas, 32 parameter/argumen per fungsi, dan kedalaman panggilan 100; sistem modul belum tersedia.
- Indeks teks native menerima indeks bilangan bulat nonnegatif; indeks negatif belum didukung.
- Teks native disimpan dalam buffer tetap berukuran 1024 byte. Operasi yang membangun teks harus diperiksa terhadap batas ini; dukungan indeks/iterasi code point UTF-8 tidak berarti runtime telah memvalidasi semua urutan UTF-8 atau menyediakan normalisasi Unicode.
- Penggabungan teks native menerima hasil hingga 1023 byte payload (ditambah terminator NUL); hasil yang melampaui kapasitas ditolak, dan batas tepat diuji melalui fixture native.
- Literal angka desimal non-finite dan hasil operasi aritmetika yang menjadi `NaN`/tak hingga ditolak dengan error. Output angka integral hanya dikonversi ke integer jika berada dalam rentang `long long`; angka finite di luar rentang tersebut tetap dicetak sebagai desimal.
- Batas loop dan langkah eksekusi membantu mengendalikan beban, tetapi **bukan sandbox**. Jangan jalankan program tak tepercaya dengan asumsi terisolasi.
- Setiap fitur native baru wajib memiliki fixture yang dijalankan oleh `make test-native`, termasuk kasus error bila relevan. Dokumentasi tidak boleh mengklaim dukungan hanya karena interpreter Python mendukung fitur tersebut.

## Urutan perluasan yang disarankan

1. Tambahkan fitur kecil beserta tes native dan kontrak error.
2. Bangun serta jalankan fixture dengan CI pada setiap PR.
3. Perluas fungsi dengan diagnostik yang konsisten, pengujian scope dan batas rekursi, lalu rancang sistem modul sebagai milestone terpisah.
4. Setelah cakupan native stabil, sediakan perintah instalasi yang mudah untuk Termux dan uji pada perangkat Android nyata.
5. Jadikan Python opsional untuk pengembangan/test, bukan dependensi saat menjalankan program melalui executable native.
