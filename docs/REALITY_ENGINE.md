# Cuk Reality Engine

> Dokumen khusus branch `cuk-reality-engine`. Fokusnya adalah mengembangkan dan membuktikan kemampuan bahasa `.cuk` melalui satu program contoh yang bermakna. Ini bukan roadmap aplikasi pengelolaan air.

## Tujuan proyek

Cuk Reality Engine adalah program berbasis aturan yang ditulis dalam `.cuk`. Program menerima masukan, memvalidasinya, memilih ID aturan, lalu menampilkan keputusan, alasan, dan tindakan yang sesuai.

Air dipakai sebagai domain contoh karena aturan ambang batasnya mudah dipahami. Domain ini bisa diganti atau diperluas nanti; yang utama adalah kemampuan bahasa yang dipakai untuk menyatakan dan menjalankan aturan.

Keberhasilan proyek ini diukur dari kualitas program dan bukti perilaku bahasa `.cuk`, bukan dari tersambungnya sensor, kesiapan distribusi air, atau deployment layanan lapangan.

## Hubungannya dengan bahasa `.cuk`

Reality Engine menjadi contoh kerja untuk menguji apakah sintaks dan semantik `.cuk` cukup jelas untuk menulis aturan yang dapat dipelihara.

| Kemampuan yang terlihat | Yang diperlihatkan contoh |
|---|---|
| Struktur program dan fungsi | `jancuk`, `fungsi`, parameter, `balek`, dan penutup blok |
| Masukan dan konversi | `tanya` menerima teks; `desimal()` mengubahnya menjadi angka yang dapat mencakup persentase pecahan |
| Percabangan | `njir` dan `kampret` memilih jalur berdasarkan kondisi |
| Validasi | Menolak cadangan di luar 0–100 dan jawaban selain `ya`/`tidak` |
| Aturan deterministik | Fungsi `aturan_air()` memilih satu ID berdasarkan masukan |
| Penanganan kegagalan | `coba`/`ketangkep` menampilkan pesan untuk masukan angka yang tidak valid |
| Keluaran yang bisa ditinjau | Program mencetak ID aturan, keputusan, alasan, dan tindakan |

Ini adalah demonstrasi dari fitur yang digunakan program; bukan klaim bahwa seluruh fitur bahasa didukung oleh semua backend.

## Aturan yang ada saat ini

| Kondisi | ID aturan | Keputusan |
|---|---|---|
| Cadangan di bawah 0% atau di atas 100% | `AIR-00: INPUT_CADANGAN_TIDAK_VALID` | `MASUKAN_TIDAK_VALID` |
| Jawaban kebutuhan dasar bukan `ya` atau `tidak` | `AIR-00: INPUT_KEBUTUHAN_TIDAK_VALID` | `MASUKAN_TIDAK_VALID` |
| Cadangan ≤ 20% dan kebutuhan dasar = `ya` | `AIR-01: CADANGAN_RENDAH_KEBUTUHAN_DASAR` | `PRIORITASKAN_KEBUTUHAN_DASAR` |
| Cadangan ≤ 20% dan kebutuhan dasar = `tidak` | `AIR-02: CADANGAN_RENDAH_BATASI_NON_ESENSIAL` | `BATASI_PENGGUNAAN_NON_ESENSIAL` |
| Cadangan > 20% sampai dengan 50% | `AIR-03: PENGHEMATAN` | `HEMAT_AIR` |
| Cadangan > 50% sampai dengan 100% | `AIR-04: KONDISI_NORMAL` | `KONDISI_NORMAL` |

Urutan pemeriksaan penting: input divalidasi sebelum ambang kebijakan digunakan. Batas 20%, 50%, 0%, dan 100% adalah contoh kebijakan pada program ini, bukan standar universal untuk pengelolaan air.

## Alur eksekusi

1. Pengguna memasukkan persentase cadangan.
2. Program mengubah teks menjadi angka dan meminta jawaban kebutuhan dasar.
3. `desimal()` mengonversi angka finite, termasuk persentase pecahan; teks yang bukan angka dan nilai non-finite seperti `NaN`/`inf` ditangani sebagai input tidak valid. Setelah konversi berhasil, `aturan_air()` memvalidasi rentang 0–100 dan menentukan ID aturan.
4. Fungsi keluaran menerjemahkan ID itu menjadi keputusan, alasan, dan tindakan.
5. Program menampilkan hasil sehingga pembaca dapat menelusuri alasan keputusan kembali ke aturan yang cocok.

Program sekarang memanggil `aturan_air()` satu kali per masukan. ID hasil itu kemudian dipakai bersama untuk menghasilkan keputusan, alasan, dan tindakan. Ini menghindari evaluasi aturan yang berulang dan membuat hubungan antara keputusan dan penjelasannya lebih eksplisit. Sumber kebijakan tetap berada di `aturan_air()`; fungsi pemetaan keluaran hanya menerjemahkan ID yang sudah dipilih.

## Cara menjalankan dan memeriksa

Dari akar repositori, interpreter referensi dijalankan dengan:

```sh
python pusingcuk_new.py examples/reality_engine.cuk
```

Contoh masukan:

- `15` lalu `ya` → ID `AIR-01`, kebutuhan dasar diprioritaskan.
- `20` lalu `tidak` → ID `AIR-02`, penggunaan non-esensial dibatasi.
- `21` lalu `ya` → ID `AIR-03`, penghematan.
- `51` lalu `tidak` → ID `AIR-04`, kondisi normal.
- `20.5` lalu `ya` → ID `AIR-03`, penghematan.
- `100.1` lalu `tidak` → ID `AIR-00`, masukan di luar rentang ditolak.
- `50` lalu `ya` → ID `AIR-03`; `50.1` lalu `ya` → ID `AIR-04`, membuktikan batas 50% secara eksplisit.
- `NaN`, `inf`, atau `-Infinity` sebagai cadangan → konversi ditolak sebelum keputusan kebijakan.
- Fungsi pemetaan menerima ID yang dihasilkan oleh `aturan_air()`. Penolakan ID arbitrer yang tidak dikenal belum dijamin oleh implementasi saat ini; jangan gunakan fungsi pemetaan sebagai batas validasi untuk ID dari sumber luar.
- `101` lalu `tidak` → masukan ditolak.
- `abc` sebagai cadangan → kegagalan konversi ditangani dan program tidak menampilkan keputusan normal.

Tes batas dan konsistensi Reality Engine berada di `tests/test_reality_engine_boundaries.py`, termasuk jawaban kebutuhan dasar yang tidak valid, teks angka yang gagal dikonversi, nilai non-finite, batas 50%, dan ID aturan tak dikenal yang tidak boleh jatuh ke keputusan normal. Tes contoh umum berada di `tests/test_examples_cuk.py`. Tes yang memeriksa perilaku tertentu membuktikan hanya kasus yang benar-benar dijalankan; keberhasilan satu contoh tidak membuktikan seluruh bahasa atau seluruh backend setara.

## Fokus pengembangan di branch ini

1. **Kebenaran contoh:** aturan, ID, keputusan, alasan, dan tindakan harus tetap saling sesuai.
2. **Kualitas bahasa:** bila penulisan program mengungkap semantik yang membingungkan atau kemampuan yang hilang, periksa akar masalahnya pada spesifikasi, parser, evaluator, runtime, atau built-in.
3. **Bukti perilaku:** tambahkan kasus regresi untuk batas dan kegagalan yang relevan; gunakan hasilnya untuk menemukan celah nyata, bukan untuk memperbanyak hitungan tes.
4. **Dokumentasi branch:** jelaskan tujuan Reality Engine di dokumen ini tanpa mengubah visi umum bahasa atau mengklaim semua target runtime mendukung contoh ini.
5. **Perubahan terarah:** perubahan baru dibuat langsung pada branch ini. Jangan memindahkan pekerjaan Reality Engine ke `main` atau `warungpusingcuk` secara otomatis.

## Bukan tujuan branch ini

- Menghubungkan sensor air sungguhan atau mengendalikan katup/pompa.
- Mengklaim bahwa kebijakan contoh cocok untuk semua wilayah atau kondisi lapangan.
- Menjadikan AI sebagai otoritas yang boleh mengubah keputusan aturan tanpa verifikasi.
- Membuat layanan SaaS atau aplikasi terpisah.
- Mengklaim bahwa kode sudah berjalan di semua compiler/runtime hanya karena interpreter referensi dapat menjalankannya.

## Status klaim

- **Ada di source:** fungsi aturan, validasi, ID, keputusan, alasan, tindakan, dan input interaktif.
- **Dapat dibuktikan melalui tes:** hanya perilaku yang dicakup tes dan benar-benar lulus pada workflow terkait.
- **Tidak disimpulkan dari contoh ini:** integrasi sensor, keselamatan operasional lapangan, parity semua backend, atau kesiapan produksi.

Lihat juga [contoh sumber](../examples/reality_engine.cuk), [tes contoh](../tests/test_examples_cuk.py), [spesifikasi bahasa](../SPEC.md), dan [kontrak semantik](SEMANTIC_CONTRACT.md).
