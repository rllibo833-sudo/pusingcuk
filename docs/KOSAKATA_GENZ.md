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
