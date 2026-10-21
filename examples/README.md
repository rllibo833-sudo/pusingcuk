# Contoh resmi .cuk

Folder ini berisi contoh dengan tingkat kematangan berbeda. **Ekstensi `.cuk` tidak berarti program sudah tervalidasi atau didukung semua target compiler.** Status sintaks, runtime, dan target harus dibuktikan oleh tes, bukan diasumsikan dari nama file.

## Mulai dari contoh minimal

Jalankan perintah berikut dari root repository dengan interpreter referensi:

```sh
python pusingcuk_new.py examples/hello.cuk
python pusingcuk_new.py examples/warung.cuk
python pusingcuk_new.py examples/rekap_anggaran.cuk
```

Contoh tersebut sengaja berfokus pada program deterministik tanpa input terminal, jaringan, API eksternal, atau akses file. Jika salah satu perintah gagal pada HEAD saat ini, anggap sebagai regresi; jangan lanjutkan ke contoh yang lebih kompleks sebelum error diperbaiki.

| Contoh | Konsep | Efek samping |
|---|---|---|
| `hello.cuk` | Variabel dan output | Tidak ada |
| `warung.cuk` | Aritmetika dan kondisi | Tidak ada |
| `rekap_anggaran.cuk` | Dictionary, fungsi, kalkulasi | Tidak ada |
| `halo_dunia.cuk` | Input interaktif | Membutuhkan stdin/terminal |
| `kalkulator.cuk` | Input, konversi, kondisi | Memerlukan built-in konversi pada target yang digunakan |
| `terminal_bot.cuk` | Bot berbasis input | Memerlukan terminal; bukan contoh browser |
| `json_demo.cuk` | JSON built-ins | Dukungan berbeda antar-target; jangan gunakan sebagai contoh universal sebelum matrix lulus |

## Prototipe self-hosting

`self_hosting/` berisi program `.cuk` untuk mengeksplorasi tahap lexer, parser, evaluator, interpreter mini, code generation, dan kontrak runtime. Ini adalah prototipe kecil, **bukan** compiler PusingCuk yang self-hosted. Batasan dan urutan menuju bootstrap sungguhan dijelaskan di [`self_hosting/README.md`](self_hosting/README.md).

Jalankan pemeriksaan runtime otomatis dari root repository dengan `python -m unittest tests.test_self_hosting_examples -v`. Lulus di interpreter referensi bukan bukti dukungan pada runtime lain; dukungan lintas target harus dibuktikan terpisah.

## Validasi sebelum menambah atau mempromosikan contoh

- Pemeriksaan sintaks semua sumber `.cuk` dilakukan oleh workflow **Example syntax check**.
- Contoh galeri browser yang dipublikasikan harus lulus eksekusi reference dan cocok byte-for-byte dengan file `.expected.txt` melalui `python tools/check_playground_examples.py`.
- Fixture konformansi ada di `tests/conformance/manifest.json`; itu merupakan kontrak tes, bukan daftar klaim bahwa semua target sudah mendukung semua fitur.
- Jangan menghapus contoh hanya karena belum didukung native C. Pindahkan ke kategori eksperimental atau perbaiki dan uji target yang dimaksud. Hapus hanya jika memang duplikat, usang, atau gagal dan tidak layak dipelihara.

## Native C

Native C adalah runtime terpisah dengan dukungan yang harus diverifikasi. Sebelum menjalankan contoh dengan native, bangun dari root:

```sh
make native
./pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

Jangan menganggap contoh Python-reference, HTTP, file I/O, konversi, atau JSON otomatis tersedia pada native C. Periksa hasil fixture dan dokumentasi kompatibilitas untuk target yang dituju.

## Playground dan contoh browser

Galeri browser yang dipublikasikan ada di `site/examples/playground/`. Setiap program memiliki file `.expected.txt`; CI memverifikasi output dengan interpreter referensi. Playground saat ini adalah galeri statis, **bukan terminal browser yang menjalankan semua fitur bahasa**. Jangan mengaktifkan kembali terminal Pyodide atau menampilkan contoh seolah dapat dijalankan sebelum ada runtime browser yang benar dan tes end-to-end.

## Aturan pemeliharaan

1. Contoh publik harus singkat, deterministik, dan menyatakan target yang didukung.
2. Jangan gunakan alias atau built-in yang tidak tercantum pada spesifikasi/kontrak tanpa menambahkan tes dan dokumentasi.
3. Jangan mengubah expected output hanya untuk membuat CI hijau; pastikan implementasi referensi dan hasil aktual benar.
4. Contoh yang belum lulus runtime dipisahkan jelas dari quickstart, bukan dipromosikan sebagai contoh pemula.
