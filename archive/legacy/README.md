# Arsip historis Pusingcuk

Isi direktori ini adalah file eksperimen/backup dari tahap awal pengembangan yang dipindahkan dari root repositori agar tidak disalahartikan sebagai entry point atau suite tes resmi.

- `interpreters/`: versi interpreter lama. Tidak didukung, tidak diaudit sebagai runtime saat ini, dan jangan jalankan untuk memproses input tak tepercaya.
- `programs/`: contoh dan fixture manual lama. Gunakan `examples/` untuk contoh yang didukung dan `tests/` untuk tes otomatis yang aktif.
- `scripts/`: skrip patch historis. Tidak digunakan oleh build atau CI saat ini.

`loop_test.pusingcuk` berisi loop tanpa kondisi berhenti; jangan menjalankannya tanpa batas waktu dan pembatasan sumber daya. Jangan mengandalkan file arsip untuk menentukan perilaku bahasa saat ini.