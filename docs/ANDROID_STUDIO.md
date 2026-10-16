# Pusingcuk Studio untuk Android

Pusingcuk Studio adalah aplikasi Android awal untuk menulis dan menjalankan program Pusingcuk langsung di ponsel. APK membawa executable runtime C yang dikompilasi untuk Android ARM; Python dan Termux tidak dibutuhkan saat menggunakan aplikasi.

## Fitur MVP

- Editor kode `.pusingcuk` dengan area input standar dan terminal keluaran.
- Menjalankan program lewat runtime native C yang dibundel di APK.
- Batas sumber 64 KiB, input 16 KiB, waktu eksekusi 3 detik, dan penangkapan output maksimum 256 KiB untuk masing-masing stdout/stderr.
- Simpan dan buka satu proyek lokal di penyimpanan privat aplikasi.
- Impor satu berkas dari repositori GitHub publik melalui GitHub Contents API.
- Bagikan/ekspor kode melalui menu berbagi Android.
- Bantuan AI online opsional lewat Gemini API; key diberikan oleh pengguna, disimpan terenkripsi memakai Android Keystore, dan tidak ditanam pada APK.
- Kode editor hanya ikut terkirim ke provider bila pengguna mencentang persetujuan di dialog AI. Source yang disarankan AI tidak dijalankan otomatis.
- Editor/runtime tetap bisa dipakai tanpa API key. AI perlu internet dan mengikuti kuota/biaya provider.
- CI membangun APK debug dan mengunggahnya sebagai artefak GitHub Actions selama 14 hari.

## Build

Workflow `.github/workflows/android-studio-apk.yml` dijalankan manual melalui `workflow_dispatch`; build APK Studio tidak dipicu otomatis oleh setiap pull request. Artefak `pusingcuk-studio-0.6-dev-debug-apk` tersedia pada halaman run GitHub Actions yang berhasil.

Workflow mengompilasi `native/pusingcuk.c` untuk ABI `arm64-v8a` dan `armeabi-v7a`, menempatkan executable ke assets, lalu membangun APK dengan JDK 17, Android SDK/NDK, dan Gradle 8.9.

## Cache dan file sementara

Saat menjalankan program, Studio menulis salinan sumber sementara ke direktori cache privat aplikasi agar runtime native dapat membacanya sebagai file. File tersebut dihapus setelah eksekusi normal; saat aplikasi dibuka kembali, file sementara berawalan `program-` yang lebih lama dari 24 jam dibersihkan. Penghentian paksa masih dapat meninggalkan file sampai pembersihan berikutnya atau sampai Android mengosongkan cache.

Cache aplikasi bukan penyimpanan permanen dan bukan mekanisme penghapusan aman. Jangan menyimpan kata sandi, token, kunci privat, atau data sensitif di kode sumber. Proyek yang disimpan secara eksplisit berada di penyimpanan privat aplikasi dan berbeda dari cache sementara.

## GitHub dan keamanan

Versi awal hanya mengimpor file dari repositori **publik** dan membagikan kode lewat Android share sheet. Belum ada push/commit langsung ke GitHub, autentikasi akun, clone/pull multi-file, branch/commit UI, atau dukungan repo privat. Fitur tulis memerlukan desain OAuth/PKCE atau GitHub App yang aman; jangan menanam personal access token dalam APK atau kode sumber.

Aplikasi tidak mengirim kode yang dijalankan ke layanan cloud. Impor GitHub hanya dilakukan setelah pengguna memilih pemilik, repositori, dan path file. Permintaan jaringan menggunakan HTTPS.

## Bantuan AI

Bantuan online memanggil Gemini `gemini-3.5-flash-lite` atau `gemini-3.8-flash` langsung melalui HTTPS. Ini antarmuka AI di dalam Studio, bukan klaim bahwa model dasar dilatih oleh PusingCuk atau bahwa seluruh ToolRegistry Python berjalan di APK. Jangan mengirim source privat/rahasia tanpa memahami bahwa permintaan dikirim ke provider eksternal. API key dienkripsi di penyimpanan privat aplikasi menggunakan kunci Android Keystore; hapus melalui tombol **Hapus kunci** di dialog AI. Model dapat berubah ketersediaan dan provider dapat mengenakan batas atau biaya.

## Batas runtime

Aplikasi memakai runtime native C yang sudah ada; ia **tidak** otomatis mendapat semua fitur interpreter Python. Kemampuan bahasa mengikuti [matriks runtime native](NATIVE_RUNTIME.md). Sistem modul, language server, debugger, dan backend web frontend belum tersedia. Runtime bukan sandbox OS; timeout tidak mencegah semua bentuk penyalahgunaan resource. Jangan menjalankan kode yang tidak dipercaya.

## Tahap lanjutan

1. Tambahkan pengelola multi-file dan riwayat proyek.
2. Rancang autentikasi GitHub yang aman untuk clone/push/branch/commit/PR.
3. Tambahkan lexer/highlighting, diagnostik baris, dan tes perangkat fisik.
4. Perluas runtime native dan conformance suite sebelum menambah janji kompatibilitas.
5. Rancang backend/frontend Pusingcuk sebagai milestone compiler/library tersendiri; APK editor ini sendiri belum membuat framework backend/frontend.
