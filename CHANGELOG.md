# Changelog

Catatan ringkas perubahan yang sudah dilakukan. Versi paket dan versi bahasa adalah dua hal berbeda.

- **Kontrak bahasa:** `0.6-dev`
- **Versi paket:** `0.8.0.dev0`
- Metadata distribusi kanonis: target paket 0.8.0.dev0.
- **Status:** pengembangan eksperimental; belum ada klaim bahwa semua backend setara.

## Unreleased

### Cuk Reality Engine — catatan branch khusus, belum menjadi kemampuan `main`

Semua butir pada bagian ini berasal dari pekerjaan branch `cuk-reality-engine`; jangan anggap sebagai implementasi `main` kecuali source, fixture, dan CI yang relevan memang sudah masuk ke branch utama. Audit 20 Oktober 2026 menemukan branch tersebut masih divergen dari `main`.

- Tegaskan status kemandirian .cuk: Reality Engine membuktikan satu program aturan pada interpreter referensi, bukan runtime mandiri, parity semua backend, toolchain mandiri, atau self-hosting.
- Ubah fallback pemetaan keputusan, alasan, dan tindakan agar ID aturan yang tidak dikenal menghasilkan status tidak dikenal dan instruksi berhenti, bukan keputusan normal. Tambahkan regresi yang menyuntikkan ID asing ke jalur keluaran.
- Tambahkan tes target JavaScript untuk menjalankan source Reality Engine yang sama pada kasus inti, termasuk input kebijakan tidak valid dan kegagalan konversi. Hasil target ini belum boleh diklaim lulus sampai CI pada commit terbaru selesai.

- Tetapkan tujuan Reality Engine sebagai program contoh berbasis aturan untuk mengembangkan dan membuktikan kemampuan bahasa `.cuk`, bukan sebagai proyek pengelolaan air produksi.
- Branch tersebut mengusulkan `docs/REALITY_ENGINE.md` untuk tabel aturan, alur eksekusi, batas klaim, cara menjalankan, dan fokus pengembangan. Berkas itu tidak ada di `main`; dokumentasi `main` yang tersedia saat ini adalah [jembatan evolusi bahasa](docs/AI_LANGUAGE_EVOLUTION_BRIDGE.md) dan [kesiapan AI Engine](docs/AI_ENGINE_READINESS.md).
- README dan indeks pada branch `cuk-reality-engine` memiliki perubahan branch-spesifik; perubahan tersebut tidak otomatis ada di `main`. `warungpusingcuk` tidak termasuk daftar branch yang ditemukan pada audit 20 Oktober 2026.
- Tambahkan tes regresi terarah untuk batas cadangan 0%, 100%, nilai negatif, dan nilai di atas 100%. Status lulus harus mengikuti hasil CI aktual; perubahan tes sendiri bukan bukti bahwa tes sudah lulus.
- Ubah alur contoh agar `aturan_air()` dievaluasi sekali; ID yang sama menjadi sumber keputusan, alasan, dan tindakan. Tambahkan regresi konsistensi untuk hasil kebijakan utama dan input tidak valid.
- Gunakan `desimal()` untuk membaca persentase cadangan agar nilai pecahan seperti `20.5` dapat melewati parsing dan diuji oleh aturan rentang. `100.1` harus ditolak oleh aturan kebijakan, bukan gagal saat konversi angka.
- Perbaiki escaping newline pada input tes supaya tiap jawaban benar-benar dikirim sebagai baris stdin terpisah.
- Tambahkan regresi untuk jawaban kebutuhan dasar di luar `ya`/`tidak` dan teks cadangan non-numerik; dokumentasikan bahwa keduanya tidak boleh menghasilkan keputusan kebijakan normal.
- Kunci batas kebijakan 50% dengan kasus tepat pada ambang dan tepat di atasnya; pastikan `NaN`, `inf`, dan `-Infinity` ditolak oleh konversi `desimal()` sebelum keputusan dibuat.

### Dokumentasi dan tata letak

- Ringkas README utama agar menjelaskan cara mulai, komponen repo, status target, dan batas kemampuan tanpa menjadi arsip audit.
- Jadikan `docs/README.md` sebagai indeks berdasarkan kebutuhan: pengguna .cuk, compiler/runtime, AI, frontend/backend, keamanan, dan status.
- Perjelas fungsi direktori serta pemisahan bahasa, compiler, library, AI, frontend, backend, dan platform.
- Ringkas status aktif agar tidak mencampur snapshot historis dari branch/commit lama dengan keadaan branch saat ini.

### Bahasa dan runtime

- Koreksi backend C: operator `==` dan `!=` pada teks membandingkan isi string dengan `strcmp`, bukan alamat string. Regresi membandingkan hasil backend C dengan interpreter referensi. Backend C subset juga mendukung `teks()` untuk teks, integer, dan boolean scalar, dengan tes parity terhadap interpreter referensi.
- Prioritas pengembangan berikutnya adalah memperluas dukungan native dan mengunci setiap perubahan semantik dengan fixture positif/negatif lintas-runtime.
- Bytecode VM tetap eksperimental; implementasi VM berbasis Python tidak dihitung sebagai runtime bebas Python.

## Catatan historis dan roadmap

- **Historis — klaim baseline 79/76:** catatan lama pernah menyebut 79 fixture, 79 wajib pada reference, dan 76 wajib pada native C dengan 3 unsupported. Klaim itu bukan baseline aktif dan tidak dihapus dari riwayat: fixture `reality-engine.unknown-rule-id-fails-closed` dipensiunkan melalui [commit `c38ce36`](https://github.com/rllibo833-sudo/pusingcuk/commit/c38ce36ed8715ab088ff16aaac35242a50ea1db8). Manifest aktif tetap **77 fixture**; jangan menambahkan fixture pensiun atau menaikkan baseline.
- **Roadmap — fail-closed untuk ID aturan tak dikenal:** simpan ide ini sebagai kandidat fixture/tes khusus di masa depan. Jika diaktifkan kembali, harus ada keputusan eksplisit, source yang aktif, expected output, dan bukti lulus pada reference serta native C. Tidak termasuk manifest atau klaim konformansi sekarang.

## Aturan changelog

Setiap perubahan perilaku bahasa harus mencatat fitur dan target yang benar-benar didukung, disertai tautan tes/fixture bila relevan. Jangan mencatat rencana sebagai fitur selesai. Simpan detail audit historis di catatan audit bertanggal; jangan menyalin seluruh audit ke changelog.
