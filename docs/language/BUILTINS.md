# Built-in Pusingcuk

Halaman ini adalah katalog built-in yang dipakai bersama oleh dokumentasi dan pengujian. Jumlah argumen, deskripsi ringkas, dan status setiap target diambil dari `library/builtin_contract.json`; tes memeriksa agar tabel ini tidak menyimpang dari metadata.

Built-in adalah bagian dari kosa kata teknis Pusingcuk, bukan panggilan Python mentah. Misalnya, `teks(benar)` menghasilkan `okelah` dan `teks(salah)` menghasilkan `tidak`, bukan ejaan boolean dari bahasa host. Angka statistik menerima daftar angka finite yang tidak kosong; nilai boolean tidak dianggap sebagai angka.

## Status target

- `supported`: implementasi target tersebut tersedia dan harus memiliki tes yang sesuai.
- `unsupported`: target diketahui tidak mengimplementasikan built-in itu; program yang memerlukannya tidak portabel ke target tersebut.
- `not-claimed`: dukungan belum diverifikasi; jangan menjanjikan kompatibilitas.
- **Python reference** adalah interpreter bahasa utama. **Python transpiler** adalah target compiler yang berbeda dan tidak boleh disamakan dengannya.

## Daftar built-in

| Built-in | Argumen | Perilaku | Python reference | Native C | JS transpiler | Python transpiler | HTML | VM |
|---|---:|---|---|---|---|---|---|---|
| `panjang` | 1 | Jumlah elemen pada teks, daftar, kamus, atau rentang yang didukung runtime. | supported | supported | supported | supported | supported | supported |
| `teks` | 1 | Konversi nilai menjadi teks. | supported | unsupported | unsupported | unsupported | unsupported | unsupported |
| `bilangan` | 1 | Konversi nilai menjadi bilangan bulat. | supported | unsupported | unsupported | unsupported | unsupported | unsupported |
| `desimal` | 1 | Konversi nilai menjadi bilangan desimal. | supported | unsupported | unsupported | unsupported | unsupported | unsupported |
| `logika` | 1 | Konversi nilai menjadi benar/salah. | supported | unsupported | unsupported | unsupported | unsupported | unsupported |
| `rentang` | 1–3 | Rentang bilangan bulat dengan batas akhir eksklusif. | supported | supported | supported | supported | supported | supported |
| `mutlak` | 1 | Nilai absolut angka finite. | supported | supported | supported | supported | supported | supported |
| `minimum` | 2 | Nilai terkecil dari dua angka finite. | supported | supported | supported | supported | supported | supported |
| `maksimum` | 2 | Nilai terbesar dari dua angka finite. | supported | supported | supported | supported | supported | supported |
| `bulatkan` | 1 | Pembulatan ties-to-even ke bilangan terdekat. | supported | supported | supported | supported | supported | supported |
| `akar` | 1 | Akar kuadrat angka non-negatif. | supported | unsupported | supported | supported | supported | unsupported |
| `bawah` | 1 | Pembulatan ke bawah menuju integer. | supported | supported | supported | supported | supported | unsupported |
| `atas` | 1 | Pembulatan ke atas menuju integer. | supported | supported | supported | supported | supported | unsupported |
| `pangkat` | 2 | Pangkat numerik dengan hasil finite. | supported | unsupported | supported | supported | supported | unsupported |
| `sinus` | 1 | Sinus sudut dalam radian. | supported | unsupported | supported | supported | supported | unsupported |
| `kosinus` | 1 | Kosinus sudut dalam radian. | supported | unsupported | supported | supported | supported | unsupported |
| `rata_rata` | 1 | Rata-rata aritmetika daftar angka finite yang tidak kosong. | supported | unsupported | supported | supported | supported | unsupported |
| `median` | 1 | Median daftar angka finite yang tidak kosong. | supported | unsupported | supported | supported | supported | unsupported |

## Contoh penggunaan

```cuk
jancuk
hedeh teks(benar)
hedeh bilangan("42")
hedeh panjang("Pusingcuk")
hedeh mutlak(-8)
hedeh rata_rata([1, 2, 6])
hedeh median([1, 4, 8])
selesai jancuk
```

Simpan sebagai `contoh.cuk` lalu jalankan pada interpreter referensi:

```sh
python pusingcuk_new.py contoh.cuk
```

Built-in `rentang` adalah sumber iterasi inti:

```cuk
jancuk
untuk angka dalam rentang(1, 5, 2)
    hedeh angka
selesai untuk
selesai jancuk
```

## Kesalahan dan batas

- Jumlah argumen di luar rentang yang tercantum harus gagal sebagai error runtime.
- Built-in numerik menolak boolean dan tipe bukan angka kecuali deskripsi secara eksplisit menyatakan konversi.
- `akar` menolak angka negatif; `rentang` menolak langkah nol.
- `rata_rata` dan `median` memerlukan daftar tidak kosong yang hanya berisi angka finite.
- Runtime native C kini mengklaim delapan built-in: `panjang`, `rentang`, `mutlak`, `minimum`, `maksimum`, `bulatkan`, `bawah`, dan `atas`. Setiap klaim didukung oleh fixture sukses dan kasus kegagalan aritas/tipe. Built-in lainnya tetap tidak didukung sampai kontrak numerik, implementasi, dan fixture-nya selaras.
- Kehadiran nama dalam registry tidak dengan sendirinya membuktikan dukungan. Status per target dalam tabel dan tes executable adalah acuan.

Lihat [kontrak semantik](../SEMANTIC_CONTRACT.md), [matriks kompatibilitas](../COMPATIBILITY.md), [registry metadata](../../library/builtin_contract.json), dan [kontrak fixture](../CONFORMANCE_FIXTURES.md) untuk detail lebih lanjut.
