# Audit Kesenjangan Runtime Native Pusingcuk

**Status:** Dokumen audit historis; jangan gunakan bagian temuan lama di bawah sebagai gambaran implementasi terkini.  
**Scope:** Audit runtime Pusingcuk bersifat umum. Referensi ke integrasi aplikasi eksternal di bawah adalah contoh opsional, bukan arah wajib proyek.  
**Audit sumber awal:** dibuat sebelum dukungan kamus dan fungsi native selesai.  
**Status terkini:** runtime C telah memiliki fixture untuk list, kamus, fungsi pengguna, rekursi terbatas, input, rentang, dan alias slang. Rujuk [Runtime Native](NATIVE_RUNTIME.md) dan [Roadmap Native, Keamanan, dan Ekosistem](NATIVE_SECURE_ECOSYSTEM_ROADMAP.md) sebagai sumber status yang lebih baru.

## Mengapa dokumen ini dipertahankan

Dokumen ini menyimpan konteks historis keputusan desain agar riwayat proyek tidak hilang. Pernyataan lama bahwa tipe kamus tidak ada dan fungsi native belum didukung sudah kedaluwarsa setelah implementasi berikutnya. Jangan menghidupkan kembali klaim tersebut tanpa memeriksa kode dan fixture terbaru.

## Prinsip audit yang tetap berlaku

1. **Native bukan otomatis setara penuh.** Fitur hanya dinyatakan didukung jika memiliki fixture native dan pemeriksaan CI yang relevan.
2. **Python tetap referensi sementara.** Pipeline modular Python masih ada; CLI native dapat menjalankan subset teruji tanpa Python.
3. **SPEC adalah kontrak semantik.** Perubahan bahasa harus disertai spesifikasi, fixture sukses, fixture kegagalan, dan catatan kompatibilitas.
4. **Batas runtime harus eksplisit.** Kapasitas koleksi, kedalaman panggilan, ukuran teks, indeks, dan batas eksekusi harus didokumentasikan.
5. **Runtime bukan sandbox.** Jangan jalankan kode tak tepercaya dengan asumsi isolasi atau perlindungan OS.
6. **Tidak ada klaim keamanan absolut.** Keamanan perlu threat model, pembatasan capability, pengujian negatif, fuzzing, dan tinjauan independen sebelum penggunaan sensitif.

## Urutan kerja yang disarankan

1. Pertahankan tes Python sebagai referensi dan perluas golden fixtures lintas-runtime.
2. Lengkapi konformansi semantik, error diagnostik, batas sumber/teks/memori, serta pengujian input rusak.
3. Tentukan arsitektur modul dan paket sebelum menambah banyak pustaka.
4. Bangun kemampuan backend (HTTP, database berparameter, autentikasi/otorisasi, secrets) sebagai adapter eksplisit dengan izin minimum.
5. Bangun kemampuan frontend secara bertahap: HTML/template aman atau target web, lalu tentukan batas JavaScript/WebAssembly yang realistis.
6. Sinkronkan status runtime pada dokumentasi teknis utama. Jika Pusingcuk dipakai oleh aplikasi atau repo lain, catat keputusan pada dokumentasi proyek tujuan dan pastikan aplikasi publik hanya mengekspos kemampuan yang sudah dibuktikan.

## Gerbang penerimaan

- Seluruh tes modular dan native test target lulus.
- Perubahan hanya menyentuh berkas yang memang terkait; tidak memasukkan binary, cache, keluaran tes, patch lokal, atau rahasia.
- CI hijau pada commit yang tepat.
- README, SPEC, dan matriks runtime tidak melebih-lebihkan kemampuan.
- Perubahan lintas repositori mengikuti kontrak integrasi yang disepakati oleh maintainer masing-masing repo dan menyertakan referensi commit/bukti.

Audit ini berbasis sumber GitHub. Pengujian CI tidak membuktikan perilaku pada perangkat Termux fisik; hal tersebut tetap perlu diverifikasi di perangkat.
