# Pusingcuk dari Nol 🚀

Panduan santai buat yang baru mulai. Kamu nggak harus jago programming dulu.

## 1. Masuk ke proyek

Buka Termux, lalu jalankan:

```bash
cd ~/pusingcuk
```

Kalau foldernya belum ada, jangan lanjut dengan menebak-nebak path. Pastikan dulu lokasi proyekmu.

## 2. Buka terminal Pusingcuk

```bash
python terminal.py
```

Kalau berhasil, akan muncul `Pusingcuk Terminal 0.1` dan prompt `pusingcuk>`.

**Penting:** perintah seperti `cd`, `git pull`, dan `python terminal.py` diketik di shell Termux. Kode bahasa Pusingcuk diketik setelah prompt `pusingcuk>`. Jangan tertukar, ya.

## 3. Program pertamamu

Ketik satu baris, tekan Enter, lanjut baris berikutnya:

```pusingcuk
jancuk
lah angka = 3 + 4
hedeh angka
selesai jancuk
```

Hasil yang benar:

```text
7
```

Artinya:
- `jancuk`: mulai program.
- `lah angka = 3 + 4`: hitung angka dan simpan hasilnya ke variabel bernama `angka`.
- `hedeh angka`: tampilkan nilai `angka`.
- `selesai jancuk`: jalankan program sampai selesai.

## 4. Minta input dari orang yang menjalankan program

```pusingcuk
jancuk
tanya nama = "Siapa nama kamu? "
hedeh "Halo, " + nama
selesai jancuk
```

Saat program berjalan, terminal akan bertanya nama. Ketik jawabanmu lalu tekan Enter. Program lalu menyapa nama tersebut.

## 5. Perintah khusus terminal

Ketik perintah ini saat prompt `pusingcuk>` muncul dan belum ada program yang sedang ditulis.

| Perintah | Fungsinya |
|---|---|
| `:bantuan` | Menampilkan petunjuk |
| `:contoh` | Menjalankan contoh penjumlahan |
| `:keluar` | Menutup terminal Pusingcuk |
| `:batal` | Membatalkan program yang sedang diketik |

Kalau kamu baru saja selesai menjalankan program dan prompt kembali ke `pusingcuk>`, terminal siap menerima program baru.

## 6. Kalau hasilnya beda

- Kalau muncul pesan `Kesalahan:`, simpan teks pesannya; itu petunjuk untuk mencari masalah.
- Kalau layar masih menampilkan prompt `......>`, program mungkin belum ditutup dengan `selesai jancuk`.
- Kalau kamu melihat `~` atau `bash`, kemungkinan kamu sedang di shell Termux, bukan terminal Pusingcuk.
- Jangan hapus file atau jalankan perintah yang belum dipahami. Tanyakan dulu dengan mengirim pesan error-nya.

## 7. Ambil pembaruan terbaru

Keluar dari terminal Pusingcuk dengan `:keluar`. Setelah kembali ke shell Termux, jalankan:

```bash
cd ~/pusingcuk && git pull
```

Lalu buka lagi dengan `python terminal.py`.

> Status: Pusingcuk masih proyek eksperimen. Panduan ini menjelaskan fitur yang ada di kode saat ini; belum berarti seluruh bahasa sudah matang atau aman untuk menjalankan kode dari orang lain.
