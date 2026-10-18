# Changelog

Catatan ringkas perubahan yang sudah dilakukan. Versi paket dan versi bahasa adalah dua hal berbeda.

- **Kontrak bahasa:** `0.6-dev`
- **Versi paket:** `0.8.0.dev0`
- Metadata distribusi kanonis: target paket 0.8.0.dev0.
- **Status:** pengembangan eksperimental; belum ada klaim bahwa semua backend setara.

## Unreleased

### Cuk Reality Engine — branch khusus

- Tetapkan tujuan Reality Engine sebagai program contoh berbasis aturan untuk mengembangkan dan membuktikan kemampuan bahasa `.cuk`, bukan sebagai proyek pengelolaan air produksi.
- Tambahkan [dokumentasi kanonis Reality Engine](docs/REALITY_ENGINE.md), termasuk tabel aturan, alur eksekusi, batas klaim, cara menjalankan, dan fokus pengembangan branch.
- Tautkan dokumentasi Reality Engine dari README dan indeks dokumentasi pada branch `cuk-reality-engine`, tanpa mengubah `main` atau `warungpusingcuk`.
- Tambahkan tes regresi terarah untuk batas cadangan 0%, 100%, nilai negatif, dan nilai di atas 100%. Status lulus harus mengikuti hasil CI aktual; perubahan tes sendiri bukan bukti bahwa tes sudah lulus.
- Ubah alur contoh agar `aturan_air()` dievaluasi sekali; ID yang sama menjadi sumber keputusan, alasan, dan tindakan. Tambahkan regresi konsistensi untuk hasil kebijakan utama dan input tidak valid.
- Gunakan `desimal()` untuk membaca persentase cadangan agar nilai pecahan seperti `20.5` dapat melewati parsing dan diuji oleh aturan rentang. `100.1` harus ditolak oleh aturan kebijakan, bukan gagal saat konversi angka.
- Perbaiki escaping newline pada input tes supaya tiap jawaban benar-benar dikirim sebagai baris stdin terpisah.
- Tambahkan regresi untuk jawaban kebutuhan dasar di luar `ya`/`tidak` dan teks cadangan non-numerik; dokumentasikan bahwa keduanya tidak boleh menghasilkan keputusan kebijakan normal.

### Dokumentasi dan tata letak

- Ringkas README utama agar menjelaskan cara mulai, komponen repo, status target, dan batas kemampuan tanpa menjadi arsip audit.
- Jadikan `docs/README.md` sebagai indeks berdasarkan kebutuhan: pengguna .cuk, compiler/runtime, AI, frontend/backend, keamanan, dan status.
- Perjelas fungsi direktori serta pemisahan bahasa, compiler, library, AI, frontend, backend, dan platform.
- Ringkas status aktif agar tidak mencampur snapshot historis dari branch/commit lama dengan keadaan branch saat ini.

### Bahasa dan runtime

- Koreksi backend C: operator `==` dan `!=` pada teks membandingkan isi string dengan `strcmp`, bukan alamat string. Regresi membandingkan hasil backend C dengan interpreter referensi. Backend C subset juga mendukung `teks()` untuk teks, integer, dan boolean scalar, dengan tes parity terhadap interpreter referensi.
- Prioritas pengembangan berikutnya adalah memperluas dukungan native dan mengunci setiap perubahan semantik dengan fixture positif/negatif lintas-runtime.
- Bytecode VM tetap eksperimental; implementasi VM berbasis Python tidak dihitung sebagai runtime bebas Python.

## Aturan changelog

Setiap perubahan perilaku bahasa harus mencatat fitur dan target yang benar-benar didukung, disertai tautan tes/fixture bila relevan. Jangan mencatat rencana sebagai fitur selesai. Simpan detail audit historis di catatan audit bertanggal; jangan menyalin seluruh audit ke changelog.
