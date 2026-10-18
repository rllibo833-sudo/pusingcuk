# Changelog

Catatan ringkas perubahan yang sudah dilakukan. Versi paket dan versi bahasa adalah dua hal berbeda.

- **Kontrak bahasa:** `0.6-dev`
- **Versi paket:** `0.8.0.dev0`
- **Status:** pengembangan eksperimental; belum ada klaim bahwa semua backend setara.

## Unreleased

### Dokumentasi dan tata letak

- Ringkas README utama agar menjelaskan cara mulai, komponen repo, status target, dan batas kemampuan tanpa menjadi arsip audit.
- Jadikan `docs/README.md` sebagai indeks berdasarkan kebutuhan: pengguna .cuk, compiler/runtime, AI, frontend/backend, keamanan, dan status.
- Perjelas fungsi direktori serta pemisahan bahasa, compiler, library, AI, frontend, backend, dan platform.
- Ringkas status aktif agar tidak mencampur snapshot historis dari branch/commit lama dengan keadaan branch saat ini.

### Bahasa dan runtime

- Tidak ada klaim fitur bahasa baru hanya dari perubahan dokumentasi.
- Prioritas pengembangan berikutnya adalah memperluas dukungan native dan mengunci setiap perubahan semantik dengan fixture positif/negatif lintas-runtime.
- Bytecode VM tetap eksperimental; implementasi VM berbasis Python tidak dihitung sebagai runtime bebas Python.

## Aturan changelog

Setiap perubahan perilaku bahasa harus mencatat fitur dan target yang benar-benar didukung, disertai tautan tes/fixture bila relevan. Jangan mencatat rencana sebagai fitur selesai. Simpan detail audit historis di catatan audit bertanggal; jangan menyalin seluruh audit ke changelog.
