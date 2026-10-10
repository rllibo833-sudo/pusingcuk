# Kosakata Slang Pusingcuk

Pusingcuk menggunakan slang Indonesia sebagai bagian dari identitas bahasanya. Kata-kata ini bukan hiasan semata: setiap alias punya makna yang konsisten dan tes.

| Slang | Kata kanonis | Makna |
|---|---|---|
| `jir` | `hedeh` | Tampilkan nilai ke keluaran standar. |
| `adooh` | `kampret` | Cabang alternatif dari kondisi `njir`. |
| `gitu` | `selesai` | Penanda penutup blok; tetap diikuti nama blok, misalnya `gitu njir`. |
| `inthiseco` | `jancuk` | Awal program. Program diakhiri dengan `gitu inthiseco`. |
| `janggal` | `bukan` | Negasi logika; membalik nilai benar/salah. |

## Contoh

```pusingcuk
inthiseco
lah angka = 7
njir janggal (angka == 5)
    jir "Angkanya bukan lima."
adooh
    jir "Angkanya lima."
gitu njir
gitu inthiseco
```

## Aturan desain

- Kata slang adalah alias resmi, bukan pengganti wajib; kata kanonis lama tetap berlaku.
- Ejaan alias peka huruf besar/kecil, sama seperti kata kunci lain.
- Alias dinormalisasi pada tahap leksikal sehingga parser dan evaluator tetap punya satu makna kanonis.
- Runtime native C hanya dijamin untuk subset yang memiliki tes native eksplisit. Ini bukan klaim kesetaraan penuh C dan Python.
- Kata slang baru harus ditambahkan bersama spesifikasi, contoh, tes Python, dan tes native jika fitur itu termasuk subset native.

## Kosakata inti dan fungsi bawaan

| Kata/fungsi | Arti | Status runtime native C |
|---|---|---|
| `lah` | Membuat variabel baru | Didukung |
| `jir` / `hedeh` | Menampilkan nilai | Didukung |
| `njir` / `adooh` | Kondisi dan cabang alternatif | Didukung |
| `mumet` | Perulangan selama kondisi benar | Didukung |
| `untuk ... dalam ...` | Mengunjungi elemen koleksi | List dan `rentang()` didukung |
| `panjang(nilai)` | Menghitung jumlah item/karakter | List, teks, rentang didukung |
| `rentang(...)` | Membuat rentang bilangan bulat dengan batas akhir eksklusif | Didukung; 1–3 argumen bulat |
| `tanya` | Membaca masukan pengguna | Belum didukung native |
| `fungsi` / `balek` | Mendefinisikan dan mengembalikan nilai fungsi | Belum didukung native |
| Kamus `{kunci: nilai}` | Menyimpan pasangan kunci-nilai | Belum didukung native |

## Contoh runtime native

```pusingcuk
inthiseco
lah angka = [2, 4, 6]
untuk nilai dalam angka
    jir nilai
gitu untuk
untuk i dalam rentang(1, 5, 2)
    jir i
gitu untuk
gitu inthiseco
```

Kamus ini membedakan **fitur bahasa modular** dari **fitur native yang sudah diuji**. Status native hanya boleh dinaikkan setelah ada fixture dan CI yang membuktikannya.
