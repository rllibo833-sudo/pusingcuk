# Rancangan Sistem Modul Pusingcuk

Status: **rancangan arsitektur, belum merupakan fitur yang tersedia**. Runtime native saat ini menerima satu berkas sumber dan belum mendukung impor modul.

## Tujuan

Sistem modul harus memungkinkan proyek tumbuh dari satu berkas latihan ke aplikasi besar tanpa menyalin kode. Desain harus bisa diterapkan konsisten pada interpreter modular dan runtime native, dengan perilaku yang dapat diuji. Python tidak boleh menjadi syarat saat executable native menjalankan modul yang didukung.

## Sintaks awal yang diusulkan

Sintaks final belum dibakukan. Proposal awal untuk dibahas:

```pusingcuk
pakai "util/angka.pusingcuk" sebagai angka

jancuk
hedeh angka.tambah(20, 22)
selesai jancuk
```

`pakai` dan `sebagai` di atas adalah proposal, bukan sintaks yang sudah didukung. Keputusan sintaks harus dicatat dalam `SPEC.md` dan diuji sebelum dianggap stabil.

## Kontrak desain

1. **Resolusi deterministik:** jalur relatif diselesaikan terhadap direktori berkas pemanggil, bukan current working directory.
2. **Tanpa pencarian liar:** versi awal tidak mengunduh paket atau menjalankan kode dari jaringan.
3. **Batas proyek:** impor harus tetap di root proyek yang ditetapkan; cegah traversal path keluar seperti `../../rahasia`.
4. **Ekstensi eksplisit:** versi awal menggunakan berkas `.pusingcuk` dan menolak ekstensi yang tidak dikenal.
5. **Satu kali evaluasi:** modul yang sama dievaluasi satu kali per proses; cache modul berada di memori proses dan tidak ditulis ke repo.
6. **Namespace:** ekspor modul tidak boleh diam-diam menimpa variabel pemanggil. Nama ekspor dan konflik nama harus punya aturan eksplisit.
7. **Siklus impor:** versi awal sebaiknya mendeteksi siklus dan menghasilkan error dengan rantai modul, bukan hang atau membaca ekspor setengah terinisialisasi.
8. **Diagnostik:** error menyebut file, baris, modul yang diminta, dan jalur resolusi yang gagal.
9. **Kompatibilitas:** perilaku yang sama harus diuji pada interpreter modular dan runtime native. Jika fitur belum ada pada salah satu runtime, dokumentasi menyatakannya.
10. **Keamanan:** batas root proyek membantu mengurangi akses file tak sengaja, tetapi tidak menjadikan runtime sandbox untuk kode tak tepercaya.

## Tahapan implementasi

### M1 — Spesifikasi dan resolver

- Putuskan sintaks, ekspor, alias, dan aturan jalur.
- Implementasikan resolver yang hanya membaca berkas di root proyek.
- Tambahkan tes path valid, modul hilang, path traversal, dan ekstensi salah.

### M2 — Interpreter modular

- Bangun cache modul per proses, namespace ekspor, dan deteksi siklus.
- Tambahkan fixture untuk impor sederhana, impor berulang, konflik nama, dan error bertingkat.
- Jangan mengubah perilaku program satu berkas yang sudah ada.

### M3 — Runtime native C

- Implementasikan parser impor dan resolver yang mengikuti kontrak M1.
- Kelola alokasi dan cleanup semua modul dengan jelas.
- Batasi jumlah modul, kedalaman impor, dan ukuran berkas; error harus terukur.
- Tambahkan fixture native yang dijalankan melalui `make test-native`.

### M4 — Pustaka standar

Mulai dari modul kecil dan portabel: operasi teks, utilitas list/dictionary, file teks dengan batas dan error yang jelas, lalu JSON dengan parser yang benar. Jangan membuat parser JSON ad hoc tanpa tes untuk string escape, Unicode, angka, nesting, nilai invalid, dan input besar.

### M5 — Konformansi dan rilis

- Jalankan fixture perilaku yang sama pada interpreter modular dan runtime native.
- Dokumentasikan fitur yang belum didukung secara eksplisit.
- Uji pada Termux nyata sebelum menyebutnya siap rilis.

## Batas backend dan frontend

Modul adalah fondasi, bukan bukti bahwa Pusingcuk sudah siap untuk semua backend/frontend. Backend memerlukan API jaringan, JSON, autentikasi, penyimpanan, observabilitas, dan batas keamanan yang jelas. Frontend web memerlukan DOM/browser APIs atau target kompilasi/interoperabilitas dengan JavaScript. Semua itu harus dibangun sebagai runtime atau binding yang terdokumentasi; bahasa tidak bisa mengakses browser hanya dengan menambahkan kata kunci.

Prioritas realistis: modul dan JSON → file/config → HTTP client/server serta error model → interoperabilitas frontend/JavaScript → tooling dan paket. Tidak boleh mengklaim kesiapan produksi sampai tiap lapisan memiliki tes, dokumentasi, dan review keamanan.
