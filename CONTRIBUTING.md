# Berkontribusi ke Pusingcuk

Terima kasih sudah membantu mengembangkan Pusingcuk. Prioritas proyek adalah bahasa yang mudah dipelajari, dapat dikembangkan secara serius, dan perlahan bisa berjalan native tanpa Python saat runtime.

## Prinsip kerja

1. Satu PR, satu tujuan yang jelas.
2. Mulai dari `main` terbaru; jangan membangun fitur baru di atas branch lama yang sudah tertinggal.
3. Jangan commit hasil build, cache, file backup, token, kata sandi, atau data pengguna.
4. Perubahan perilaku bahasa harus memperbarui spesifikasi, tes, dan dokumentasi yang relevan.
5. Jangan mengklaim dukungan native berdasarkan hasil interpreter Python saja.
6. Klaim kompatibilitas lintas runtime atau platform harus merujuk pada [kontrak kompatibilitas](docs/COMPATIBILITY.md) dan didukung tes yang relevan.
7. Jangan merge PR tanpa tinjauan pemilik proyek.

## Nama branch

Gunakan pola berikut:

- `feat/<fitur-singkat>` — kemampuan bahasa baru.
- `fix/<masalah-singkat>` — perbaikan bug.
- `test/<cakupan-singkat>` — pengujian saja.
- `docs/<topik-singkat>` — dokumentasi dan tutorial.
- `audit/<topik-singkat>` — temuan audit yang belum mengubah perilaku.
- `refactor/<topik-singkat>` — restrukturisasi tanpa perubahan perilaku yang disengaja.

Hindari nama generik seperti `update`, `new-feature`, atau `final-fix`.

## Sebelum mulai

```sh
git switch main
git pull --ff-only
git status --short
git switch -c docs/topik-singkat
```

Jika `git status --short` menampilkan perubahan yang belum kamu pahami, berhenti dan periksa sebelum berpindah branch. Jangan menghapus perubahan pengguna secara otomatis.

## Gerbang pengujian

Untuk perubahan bahasa modular:

```sh
python -m unittest discover -s tests -v
```

Untuk perubahan runtime native:

```sh
make test-native
```

Jika perubahan menyentuh kedua runtime, jalankan keduanya. CI wajib lulus pada commit terakhir PR. Pengujian fisik Termux tetap diperlukan untuk klaim kompatibilitas perangkat; CI Ubuntu bukan pengganti pengujian Android.

## Checklist sebelum membuka PR

- [ ] PR berasal dari `main` terbaru dan hanya berisi perubahan yang diperlukan.
- [ ] Ada tes untuk jalur sukses dan kasus error yang relevan.
- [ ] Dokumentasi dan `SPEC.md` selaras dengan perilaku implementasi.
- [ ] Runtime native dan modular tidak diklaim setara tanpa fixture konformansi.
- [ ] Klaim platform/kompatibilitas sesuai matriks yang benar-benar diuji di [kontrak kompatibilitas](docs/COMPATIBILITY.md).
- [ ] Tidak ada token, data pribadi, cache, binary, atau backup yang ikut masuk.
- [ ] Pesan error cukup jelas dan tidak membocorkan rahasia.
- [ ] Perintah tes, hasilnya, dan batas yang belum diuji ditulis jujur di deskripsi PR.

## Riwayat Git yang rapi

Gunakan commit yang menjelaskan perubahan, misalnya `feat(native): add module imports` atau `docs: improve Termux quickstart`. Kelompokkan perubahan terkait, hindari commit untuk setiap edit kecil yang belum ditinjau, dan pilih **Squash and merge** untuk PR yang telah disetujui. Jangan force-push `main` atau menghapus branch yang statusnya belum diaudit.

Branch lama yang sudah merged sebaiknya dihapus setelah dipastikan PR terkait merged dan tidak ada pekerjaan unik yang belum diselamatkan. Branch yang tertinggal jangan langsung dihapus bila statusnya belum jelas.
