# CukAccount — frontend dan backend PusingCuk

Branch `warungpusingcuk` mengunci satu contoh produk untuk mengembangkan bahasa `.cuk` dan PusingCuk AI. Sumber domain aplikasi berada di dua file kanonis:

- `cukaccount_frontend.cuk` — kontrak layar, navigasi, field formulir, aksi, dan fungsi validasi formulir.
- `cukaccount_backend.cuk` — aturan domain deterministik: persamaan akuntansi, validasi jurnal, saldo normal, periode, klasifikasi laporan, validasi input pajak tanpa menghitung kewajiban pajak, dan penanda awal pemeriksaan syariah.
- `cukaccount_backend.expected.txt` — output yang dikunci untuk regresi backend.
- `cukaccount_frontend.expected.txt` — output yang dikunci untuk rute dan validasi formulir.
- `tools/diagnostic_repair_loop.py` — pemeriksaan compiler/runtime, hash sumber, perbandingan fixture, dan laporan diagnostik untuk ditinjau PusingCuk AI.

## Jalankan pemeriksaan

Dari root repository:

```sh
python pusingcuk_new.py --check apps/accounting/cukaccount_frontend.cuk
python pusingcuk_new.py apps/accounting/cukaccount_frontend.cuk
python pusingcuk_new.py --check apps/accounting/cukaccount_backend.cuk
python pusingcuk_new.py apps/accounting/cukaccount_backend.cuk
python tools/diagnostic_repair_loop.py apps/accounting/cukaccount_backend.cuk --expected apps/accounting/cukaccount_backend.expected.txt --json
python -m unittest tests.test_diagnostic_repair_loop -v
python -m unittest tests.test_diagnostic_repair_loop -v
```

## Kontrak dan batas saat ini

- Komentar `# @...` di file frontend adalah metadata kontrak sumber. Interpreter PusingCuk saat ini mengabaikan komentar tersebut; file ini **belum dirender menjadi UI aplikasi** dan belum mengklaim memiliki runtime UI.
- Kode fungsi di kedua file adalah sintaks `.cuk` yang benar-benar diperiksa dan dijalankan oleh interpreter referensi.
- Backend ini adalah aturan domain latihan, bukan mesin akuntansi produksi. Fungsi pajak hanya memvalidasi rentang input; tidak menghitung pajak dan bukan interpretasi hukum pajak Indonesia. Pemeriksaan syariah hanya penanda awal dan bukan fatwa atau validasi kepatuhan.
- Fixture yang lulus membuktikan output pada interpreter yang diuji; tidak membuktikan kesetaraan semua runtime, integrasi database, APK Android, atau kesiapan pembukuan resmi.
- Siklus diagnostik menghasilkan laporan dan saran yang dapat dikonsumsi AI, tetapi tidak mengedit kode atau menerapkan patch otomatis. Perubahan harus melewati compiler, fixture regresi, dan tinjauan.
- Flutter/Dart dan SQLite pada repo CukAccount tetap bagian dari produk yang ada; branch ini berfokus pada sumber `.cuk` dan jalur pengembangan PusingCuk AI, bukan mengganti diam-diam fondasi aplikasi produksi.

## Prinsip kontribusi

1. Ubah sumber `.cuk`, jangan menutupi kegagalan dengan mengubah expected output secara otomatis.
2. Tambahkan kasus normal, batas, dan negatif untuk setiap aturan baru.
3. Jalankan `--check`, eksekusi interpreter, dan tes diagnostik sebelum menyatakan perubahan selesai.
4. Pertahankan output diagnostik yang dapat direproduksi dan hash sumber.
5. Jangan mengklaim fitur produksi tanpa integrasi dan bukti tes yang sesuai.

## Handoff ke PusingCuk AI

Saat compiler, runtime, atau fixture gagal, `diagnostic_repair_loop.py` menghasilkan objek `ai_handoff` dengan kontrak `pusingcuk.ai.repair.v1`. Handoff memuat sumber yang diuji, SHA-256 sumber, kode diagnostik, perbandingan output, batas perbaikan, dan instruksi agar AI mengusulkan perubahan minimal. Handoff ini siap dipakai sebagai konteks AI; pemanggilan model dan penerapan patch otomatis **belum** diklaim tersedia.

