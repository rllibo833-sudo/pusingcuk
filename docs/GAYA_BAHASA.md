# Panduan Gaya Bahasa Pusingcuk

## Tujuan

Pusingcuk memakai bahasa Indonesia yang akrab bagi Gen Z dan Gen Alpha tanpa membuat bahasa pemrogramannya terasa seperti tren sesaat. Gaya boleh santai; sintaks, spesifikasi, pesan error, dan dokumentasi teknis harus tetap jelas dan konsisten.

## Prinsip penulisan

1. **Ramah, bukan sok gaul.** Pakai sapaan seperti "Yuk coba" atau "Kalau muncul error" seperlunya. Jangan memaksa slang baru di setiap kalimat.
2. **Jelaskan istilah saat pertama muncul.** Contoh: "runtime (program yang menjalankan kode)" atau "variabel (nama untuk menyimpan nilai)".
3. **Satu langkah, satu tujuan.** Tutorial memperkenalkan satu konsep utama pada satu contoh, lalu memberi tantangan kecil.
4. **Contoh dekat dengan keseharian.** Gunakan nilai, daftar belanja, jadwal, game sederhana, musik, atau anggaran. Hindari contoh yang bergantung pada tren yang cepat basi.
5. **Kode tetap konsisten.** Kata kunci dan sintaks kanonis tidak berubah hanya demi gaya tulisan. Alias slang adalah pilihan yang terdokumentasi, bukan kewajiban.
6. **Jangan menyamakan bahasa santai dengan bahasa tidak akurat.** Sebut batas runtime, versi, platform, dan status fitur secara eksplisit.
7. **Bisa dipindai di layar ponsel.** Gunakan judul deskriptif, paragraf pendek, blok kode kecil, dan langkah bernomor.
8. **Aksesibel untuk semua usia dan latar.** Hindari ejekan, stereotip generasi, jargon yang tidak dijelaskan, dan instruksi yang menganggap pembaca sudah ahli.

## Pilihan kata

| Situasi | Gunakan | Hindari |
|---|---|---|
| Memulai tutorial | "Yuk jalankan contoh pertama." | Slang berlebihan di setiap kalimat |
| Menjelaskan error | "Program berhenti karena indeks berada di luar batas." | "Kodenya ngambek" sebagai satu-satunya penjelasan |
| Fitur belum tersedia | "Fitur ini belum didukung runtime native." | "Segera hadir" tanpa rencana yang disetujui |
| Memberi tantangan | "Coba ubah angka 3 menjadi 5, lalu jalankan lagi." | Tantangan tanpa hasil yang bisa diperiksa |
| Menjelaskan istilah | Definisi singkat saat istilah pertama muncul | Tumpukan singkatan tanpa arti |

Humor atau slang boleh menjadi pelengkap, tetapi pesan error wajib menyebut masalah dan, bila memungkinkan, lokasi serta cara memperbaikinya.

## Pola tutorial

Tutorial pemula sebaiknya berisi:
1. **Tujuan:** apa yang akan dibuat.
2. **Persiapan:** perintah yang dibutuhkan dan platform yang diuji.
3. **Kode utuh:** contoh kecil yang dapat langsung dijalankan.
4. **Hasil:** keluaran yang diharapkan.
5. **Bedah kode:** jelaskan baris penting dengan bahasa sederhana.
6. **Coba sendiri:** satu atau dua perubahan kecil beserta petunjuk hasilnya.
7. **Kalau gagal:** solusi untuk kesalahan umum dan cara melaporkan error tanpa membagikan rahasia.

Jangan menyuruh pemula memasang Python untuk menjalankan program melalui executable native. Terangkan bahwa Python masih diperlukan untuk interpreter referensi, tes, dan bridge Studio saat ini.

## Contoh nada

**Kurang membantu:** "Gas bikin program, tinggal pakai fungsi dan beres."

**Lebih membantu:** "Yuk buat fungsi untuk menjumlahkan dua angka. Fungsi adalah blok kode yang bisa dipanggil kembali. Setelah dijalankan, contoh ini seharusnya menampilkan `42`."

## Standar untuk kontributor

- Teks antarmuka, dokumentasi, tutorial, dan pesan error harus mengikuti panduan ini.
- Contoh kode harus memakai sintaks yang benar-benar didukung pada runtime yang disebutkan.
- Jika contoh native, pastikan ada fixture atau langkah uji yang relevan.
- Jangan menjanjikan keamanan, kompatibilitas OS, atau dukungan fitur yang belum diverifikasi.
- Istilah slang baru perlu alasan desain, definisi yang tidak ambigu, tes, dan dokumentasi. Jangan menambah alias hanya agar terlihat kekinian.
- Pertahankan istilah teknis kanonis di samping penjelasan sederhananya agar pengguna bisa berkembang ke dokumentasi tingkat lanjut.

## Kapan panduan ini berlaku?

Panduan ini berlaku untuk README, tutorial, contoh, pesan CLI, pesan error, dan kontribusi baru. Panduan ini tidak mengubah sintaks atau semantik bahasa dengan sendirinya.
