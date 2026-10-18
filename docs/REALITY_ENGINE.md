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
- Fungsi pemetaan menerima ID yang dihasilkan oleh `aturan_air()`. ID arbitrer yang tidak dikenal sekarang diarahkan ke keputusan `ID_ATURAN_TIDAK_DIKENAL`, alasan bahwa kebijakan tidak tersedia, dan tindakan untuk menghentikan keputusan otomatis. Regresi memasukkan ID asing dengan mengganti hasil aturan; klaim ini tetap bergantung pada hasil CI commit terbaru.
- `101` lalu `tidak` → masukan ditolak.
- `abc` sebagai cadangan → kegagalan konversi ditangani dan program tidak menampilkan keputusan normal.

Tes batas dan konsistensi Reality Engine berada di `tests/test_reality_engine_boundaries.py`, termasuk jawaban kebutuhan dasar yang tidak valid, teks angka yang gagal dikonversi, nilai non-finite, dan batas 50%. ID arbitrer yang tidak dikenal tercakup oleh regresi `test_unknown_rule_id_fails_closed_for_all_outputs`; hasil kelulusan terbaru tetap harus diperiksa pada CI. Tes contoh umum berada di `tests/test_examples_cuk.py`. Tes yang memeriksa perilaku tertentu membuktikan hanya kasus yang benar-benar dijalankan; keberhasilan satu contoh tidak membuktikan seluruh bahasa atau seluruh backend setara.

## Sejauh mana menuju kemandirian bahasa .cuk

**Penilaian jujur: Reality Engine adalah program pembuktian bahasa, bukan runtime/compiler mandiri.** Ia membantu menguji apakah .cuk cukup ekspresif untuk menulis aturan deterministik yang bisa dijelaskan dan diregresikan. Kemandirian bahasa harus dinilai dari pipeline bahasa dan target runtime, bukan dari nama atau kompleksitas contoh aplikasi ini.

| Tingkat | Status pada branch ini | Bukti / batas |
|---|---|---|
| Aturan bisnis ditulis dalam .cuk | Ada | `aturan_air()` memvalidasi input dan memilih ID aturan berdasarkan ambang yang eksplisit. |
| Keputusan dan penjelasan terhubung | Ada | Satu ID aturan dipakai untuk keputusan, alasan, dan tindakan; pemetaan keluaran masih fungsi terpisah. |
| Interaksi input dan validasi | Ada pada interpreter referensi | CLI meminta input, mengonversi angka, menolak rentang yang tidak valid, dan menangani kegagalan konversi. |
| Regresi perilaku | Ada untuk kasus yang tercakup | Tes batas memeriksa beberapa ambang dan input salah. Tes hanya membuktikan kasus yang benar-benar dijalankan dan lulus di CI. |
| Mandiri dari Python saat runtime | **Belum** | Contoh dijalankan melalui `python pusingcuk_new.py examples/reality_engine.cuk`; blok `coba/ketangkep` yang dipakai contoh belum didukung runtime native C. |
| Pemetaan ID tak dikenal | Implementasi fail-closed + regresi baru | ID asing menghasilkan keputusan `ID_ATURAN_TIDAK_DIKENAL`, alasan tidak tersedia, dan tindakan berhenti; status lulus harus dikonfirmasi dari CI commit terbaru. |
| Paritas target | **Belum dibuktikan penuh** | Regresi baru mencoba source yang sama pada target JavaScript untuk kasus inti; seluruh matriks input dan parity native/VM belum terbukti. Status CI terbaru harus diperiksa. |
| Bahasa dapat membangun toolchain-nya sendiri / self-hosting | **Belum** | Contoh ini tidak mengompilasi compiler .cuk, tidak mengganti implementasi Python, dan tidak membuktikan self-hosting. |

### Apa arti “mandiri” dalam proyek .cuk

Ada beberapa tingkat yang jangan dicampur:

1. **Mandiri sebagai bahasa sumber:** program bisnis ditulis di `.cuk` — Reality Engine sudah menunjukkan ini untuk satu contoh.
2. **Mandiri sebagai executable:** program dikompilasi menjadi executable yang berjalan tanpa Python saat runtime — backend C memiliki kemampuan untuk subset yang didukung, tetapi Reality Engine ini belum dibuktikan pada subset tersebut.
3. **Mandiri sebagai toolchain:** compiler, runtime, diagnostik, dan pustaka inti tidak lagi bergantung pada implementasi Python untuk membangun/menjalankan bahasa — belum tercapai.
4. **Self-hosting:** compiler .cuk ditulis dalam .cuk dan dapat membangun versi dirinya sendiri — belum tercapai dan bukan hasil yang bisa disimpulkan dari contoh ini.

### Urutan kerja yang masuk akal

- Pertama, pertahankan satu ID aturan sebagai hasil kanonis dan tambah tes untuk konsistensi keputusan/alasan/tindakan, termasuk input gagal.
- Kedua, fail-closed untuk ID tak dikenal kini diimplementasikan dengan percabangan yang kompatibel dengan parser, dan regresinya ditambahkan; jangan menyebutnya terverifikasi sebelum CI commit terbaru lulus.
- Ketiga, jalankan source yang sama pada JavaScript (target ini mendukung `coba/ketangkep`) dan native. Native C tetap tidak mendukung blok `coba`; jangan mengklaim parity native untuk program utuh sebelum fitur tersebut tersedia atau contoh sengaja disederhanakan.
- Keempat, bandingkan source yang sama pada interpreter referensi dan JavaScript untuk kasus valid, input kebijakan tidak valid, dan kegagalan konversi; lalu perluas ke seluruh ID, input batas, exit code, dan kelas error. Native memerlukan dukungan `coba/ketangkep` atau subset contoh yang disengaja.
- Setelah bukti parity ada, baru naikkan klaim kemandirian target. Self-hosting adalah tahap terpisah yang jauh lebih lanjut.

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
