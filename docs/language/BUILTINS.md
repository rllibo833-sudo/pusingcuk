# Built-in Pusingcuk

Halaman ini adalah katalog built-in yang dipakai bersama oleh dokumentasi dan pengujian. Jumlah argumen, deskripsi ringkas, dan status setiap target diambil dari `library/builtin_contract.json`; tes memeriksa agar tabel ini tidak menyimpang dari metadata.

**Versi bahasa:** `0.6-dev`. Bagian pertama berisi tepat 25 built-in terkontrak; fungsi tambahan yang langsung ditangani evaluator reference dipisahkan dan tidak masuk hitungan built-in lintas target.

Status `not-claimed` pada native C berarti scalar subset telah diuji, tetapi kesetaraan penuh dengan interpreter referensi belum diklaim. Built-in `json_teks`, `json_baca`, `html_aman`, dan `csv_baris` kini berstatus `supported` setelah fixture nested JSON, JSON valid/invalid/null, escaping, quoting, dan numeric normalization lulus di matriks konformansi. Backend JS mengikuti kontrak built-in bersama: `desimal()` menerima angka atau teks desimal finite (bukan boolean/null), `logika()` memakai truthiness bahasa, dan `logaritma()`, `log10()`, serta `jumlah()` memvalidasi domain, tipe, finite values, dan rentang integer aman. Built-in adalah bagian dari kosa kata teknis Pusingcuk, bukan panggilan Python mentah. Misalnya, `teks(benar)` menghasilkan `okelah` dan `teks(salah)` menghasilkan `tidak`, bukan ejaan boolean dari bahasa host. Statistik `rata_rata` dan `median` menerima daftar angka finite non-boolean yang tidak kosong; `jumlah` menerima daftar termasuk daftar kosong yang menghasilkan nol. Nilai integer di luar rentang aman dan hasil non-finite ditolak.

## Status target

- `supported`: implementasi target tersebut tersedia dan harus memiliki tes yang sesuai.
- `unsupported`: target diketahui tidak mengimplementasikan built-in itu; program yang memerlukannya tidak portabel ke target tersebut.
- `not-claimed`: dukungan belum diverifikasi; jangan menjanjikan kompatibilitas.
- **Python reference** adalah interpreter bahasa utama. **Python transpiler** adalah target compiler yang berbeda dan tidak boleh disamakan dengannya.

## 25 Built-in Terkontrak

| Built-in | Argumen | Perilaku | Python reference | Native C | JS transpiler | Python transpiler | HTML | VM |
|---|---:|---|---|---|---|---|---|---|
| `panjang` | 1 | Jumlah elemen pada teks, daftar, kamus, atau rentang yang didukung runtime. | supported | supported | supported | supported | supported | supported |
| `teks` | 1 | Konversi nilai menjadi teks. | supported | not-claimed | supported | supported | unsupported | supported |
| `bilangan` | 1 | Konversi nilai menjadi bilangan bulat. | supported | not-claimed | supported | supported | unsupported | supported |
| `desimal` | 1 | Konversi nilai menjadi bilangan desimal. | supported | not-claimed | supported | supported | unsupported | supported |
| `logika` | 1 | Konversi nilai menjadi benar/salah. | supported | not-claimed | supported | supported | unsupported | supported |
| `rentang` | 1–3 | Rentang bilangan bulat dengan batas akhir eksklusif. | supported | supported | supported | supported | supported | supported |
| `mutlak` | 1 | Nilai absolut angka finite. | supported | supported | supported | supported | supported | supported |
| `minimum` | 2 | Nilai terkecil dari dua angka finite. | supported | supported | supported | supported | supported | supported |
| `maksimum` | 2 | Nilai terbesar dari dua angka finite. | supported | supported | supported | supported | supported | supported |
| `bulatkan` | 1 | Pembulatan ties-to-even ke bilangan terdekat. | supported | supported | supported | supported | supported | supported |
| `akar` | 1 | Akar kuadrat angka finite non-negatif; hasil bulat dalam rentang aman dikembalikan sebagai integer. | supported | supported | supported | supported | supported | supported |
| `bawah` | 1 | Pembulatan ke bawah menuju integer. | supported | supported | supported | supported | supported | supported |
| `atas` | 1 | Pembulatan ke atas menuju integer. | supported | supported | supported | supported | supported | supported |
| `pangkat` | 2 | Pangkat dua angka finite; domain tidak valid dan hasil non-finite ditolak. | supported | supported | supported | supported | supported | supported |
| `logaritma` | 1 | Logaritma natural untuk angka finite positif. | supported | supported | supported | supported | unsupported | supported |
| `log10` | 1 | Logaritma basis 10 untuk angka finite positif. | supported | supported | supported | supported | unsupported | supported |
| `sinus` | 1 | Sinus sudut finite dalam radian; hasil integral aman dinormalisasi dan hasil non-finite ditolak. | supported | supported | supported | supported | supported | supported |
| `kosinus` | 1 | Kosinus sudut finite dalam radian; hasil integral aman dinormalisasi dan hasil non-finite ditolak. | supported | supported | supported | supported | supported | supported |
| `jumlah` | 1 | Jumlah berurutan angka finite non-boolean dalam daftar; daftar kosong bernilai nol dan setiap hasil integral antara/akhir dibatasi rentang aman lintas target. | supported | supported | supported | supported | unsupported | supported |
| `rata_rata` | 1 | Rata-rata aritmetika daftar nonkosong angka finite non-boolean dalam rentang aman lintas target. | supported | supported | supported | supported | supported | supported |
| `median` | 1 | Median daftar nonkosong angka finite non-boolean dalam rentang aman lintas target. | supported | supported | supported | supported | supported | supported |
| `json_teks` | 1 | Serialisasi nilai JSON dengan tipe dan kunci yang aman lintas target. | supported | supported | supported | supported | supported | supported |
| `json_baca` | 1 | Membaca teks JSON menjadi nilai PusingCuk. | supported | supported | supported | supported | supported | supported |
| `html_aman` | 1 | Meloloskan karakter khusus untuk teks HTML. | supported | supported | supported | supported | supported | supported |
| `csv_baris` | 1 | Menyerialisasi daftar nilai skalar menjadi satu baris CSV RFC 4180 tanpa terminator baris. | supported | supported | supported | supported | supported | supported |

## Intrinsics Tambahan Python (reference only)

Fungsi berikut ditangani langsung oleh evaluator Python dan bukan bagian dari 25 built-in terkontrak. Ketersediaannya tidak boleh diasumsikan pada runtime native C, transpiler, HTML, atau VM.

- **Berkas/JSON:** `baca`, `tulis`, `baca_json`, `tulis_json`
- **Modul dan waktu:** `angkut`, `jam`, `tanggal`
- **HTTP:** `kepo_internet` (GET), `kirim_api` (POST)
- **Nilai/terminal/JSON tambahan:** `jadi_json`, `jadi_teks`, `warna`
- **Input:** `tanya` (statement/input intrinsic; juga punya alias slang reference)

API di daftar ini reference-only kecuali implementasi dan fixture membuktikan dukungan per target. `jadi_json` kini memiliki implementasi native dan fixture terpisah dari `json_baca`: invalid JSON menghasilkan `salah`, sedangkan `json_baca` menghasilkan kesalahan runtime.

## Contoh penggunaan

```cuk
jancuk
hedeh teks(benar)
hedeh bilangan("42")
hedeh panjang("Pusingcuk")
hedeh mutlak(-8)
hedeh jumlah([1, 2, 6])
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
- `jumlah` menerima satu daftar angka finite non-boolean; daftar kosong bernilai nol. Input integer-valued dan hasil penjumlahan integral dibatasi pada rentang aman `±(2^53 - 1)`.
- `rata_rata` dan `median` memerlukan daftar tidak kosong berisi angka finite non-boolean dalam rentang aman. Fixture mengunci batas inklusif, cancellation, angka negatif, nilai duplikat, hasil pecahan, aritas, tipe, dan rentang invalid.
- Native C mendukung built-in yang ditandai `supported` pada registry dan dibuktikan fixture lintas-runtime; built-in konversi scalar tetap berstatus `not-claimed`.
- Kehadiran nama dalam registry tidak dengan sendirinya membuktikan dukungan. Status per target dalam tabel dan tes executable adalah acuan.

Lihat [kontrak semantik](../SEMANTIC_CONTRACT.md), [matriks kompatibilitas](../COMPATIBILITY.md), [registry metadata](../../library/builtin_contract.json), dan [kontrak fixture](../CONFORMANCE_FIXTURES.md) untuk detail lebih lanjut.
