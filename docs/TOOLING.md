# Tooling dan Alur Pengembangan Pusingcuk

## Yang tersedia sekarang

| Kebutuhan | Perintah atau berkas | Batas |
|---|---|---|
| Build executable native | `make native` | Membutuhkan compiler C11 |
| Jalankan program native | `make run-native FILE=program.pusingcuk` atau `pusingcuk-native program.pusingcuk` | Hanya subset native teruji |
| Tes runtime native | `make test-native` | CI berjalan di Ubuntu; uji Termux fisik tetap diperlukan |
| Tes interpreter modular | `python -m unittest discover -s tests -v` | Membutuhkan Python |
| Periksa sintaks tanpa menjalankan | `python pusingcuk_new.py --check program.cuk` | Tidak menjalankan input, file I/O, atau fungsi program | 
| Terminal interaktif modular | `python terminal.py` | Ini bukan runtime native |
| CLI interpreter modular | `python pusingcuk_new.py program.cuk` | Membutuhkan Python; `.pusingcuk` lama tetap diterima |
| Panduan pengguna | `docs/PEMULA.md` | Mengutamakan native Termux |
| Kemampuan native | `docs/NATIVE_RUNTIME.md` | Hanya fitur yang memiliki tes boleh disebut teruji |

## Aturan diagnostik

- Bedakan error sintaks, nama yang tidak dikenal, tipe/argumen salah, file hilang, dan batas runtime.
- Tampilkan file dan baris jika tersedia.
- Pesan harus menyebut tindakan yang dapat dicoba; jangan hanya mengatakan “gagal”.
- Jangan tampilkan isi rahasia dari file konfigurasi atau environment.
- Setiap perbaikan error harus memiliki tes regresi.

## Target DX berikutnya

1. Satukan nama executable/perintah dan dokumentasi agar pengguna tidak bingung antara interpreter Python dan runtime native.
2. Tambahkan mode pemeriksaan sintaks (`--check`) hanya setelah parser dapat membedakan validasi dari eksekusi tanpa efek samping.
3. Tambahkan pesan error native yang menyertakan nama file, nomor baris, dan konteks terbatas.
4. Buat uji konformansi yang menjalankan contoh sama pada runtime modular dan native.
5. Integrasikan Pusingcuk Studio sebagai editor/run/test front-end; jangan menjanjikan fitur yang belum diuji dengan runtime native.
6. Tambahkan benchmark dan batas sumber daya setelah semantik modul serta cleanup memori stabil.

Tooling tidak boleh menjadi alasan menambah dependensi runtime Python pada executable native.
