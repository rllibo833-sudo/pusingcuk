# Start Here — Panduan Kontributor PusingCuk

Kamu tidak perlu menjadi programmer profesional untuk membantu proyek ini. Mulai dari contoh kecil, dokumentasi, atau laporan bug yang bisa direproduksi.

## Yang bisa dikerjakan

### 1. Menulis contoh .cuk
Tambahkan contoh untuk kasus nyata seperti kalkulator, catatan nilai, kuis, atau anggaran di `examples/nama.cuk`. Periksa sintaks dengan:

```sh
python pusingcuk_new.py --check examples/nama.cuk
```

### 2. Memperbaiki dokumentasi
Bantu merapikan atau menerjemahkan dokumentasi dan kamus. Jangan mengubah spesifikasi atau klaim dukungan target tanpa bukti.

### 3. Melaporkan bug
Sertakan kode minimum, perintah yang dijalankan, output aktual, output yang diharapkan, dan versi/target yang digunakan. Hindari laporan yang hanya mengatakan “tidak jalan”.

### 4. Mengusulkan kosakata
Usulan alias slang dibahas melalui issue berlabel `spec-discussion`. Jangan menambahkan keyword atau alias langsung tanpa keputusan yang sesuai dengan SPEC.

### 5. Memeriksa playground
Coba https://rllibo833-sudo.github.io/pusingcuk/playground.html. Playground saat ini bersifat eksperimental; jangan menyamakan runtime playground dengan runtime native.

## Alur kontribusi dari HP

1. Buka https://github.com/rllibo833-sudo/pusingcuk.
2. Buka file atau folder yang relevan.
3. Untuk perubahan kode, gunakan fork/branch sesuai aturan kontribusi repo.
4. Jalankan pemeriksaan yang tersedia atau minta bantuan untuk memeriksa reproduksi.
5. Jelaskan alasan perubahan dan hasil yang benar-benar telah diverifikasi.

## Jangan dilakukan tanpa diskusi

- Mengubah semantik bahasa atau menambah keyword/alias.
- Mengklaim backend kompatibel tanpa fixture.
- Menambahkan dependensi jaringan untuk fitur yang seharusnya lokal.
- Mengubah hasil laporan secara manual agar tampak hijau.
- Menganggap CI hijau sebagai bukti semua target siap produksi.

## Laporan bug yang baik

- **Kode reproduksi:** program .cuk sekecil mungkin.
- **Perintah:** perintah lengkap yang dijalankan.
- **Aktual:** output atau diagnostic yang terlihat.
- **Harapan:** hasil yang seharusnya.
- **Target:** interpreter, native C, VM, atau backend lain.
