# PusingCuk

PusingCuk adalah bahasa pemrograman **experimental** dengan ekstensi utama `.cuk`, kata kunci Indonesia, dan identitas bahasa lokal. Tujuannya adalah memudahkan pemrograman tanpa mengorbankan semantik yang jelas, diagnostik yang berguna, dan hasil yang bisa dibuktikan.

**Status versi:** kontrak bahasa `0.6-dev`; versi paket Python `0.8.0.dev0`. Keduanya berbeda dan bukan klaim rilis stabil. Metadata paket pada `main` adalah `0.8.0.dev0`; branch ini tetap menggunakan metadata paket yang sama sampai kontrak rilis diperbarui.

## Fokus khusus branch `cuk-reality-engine`

Branch ini memuat **Cuk Reality Engine**, contoh program berbasis aturan yang dipakai untuk mengembangkan dan membuktikan kemampuan bahasa `.cuk`. Contoh domainnya adalah keputusan berdasarkan persentase cadangan air, tetapi tujuan utamanya adalah bahasa: fungsi, validasi masukan, percabangan, keputusan deterministik, ID aturan, penjelasan, dan penanganan kesalahan.

Dokumen kanonis branch ini: [Cuk Reality Engine](docs/REALITY_ENGINE.md). Batas yang diketahui: fungsi pemetaan belum menjamin penolakan ID aturan arbitrer yang tidak dikenal; jangan gunakan pemetaan sebagai validasi untuk ID dari sumber luar. Ini bukan proyek integrasi sensor atau sistem pengelolaan air produksi. Perubahan pada branch ini tidak otomatis mengubah `main` atau `warungpusingcuk`.

## Mulai cepat

Jalur referensi saat ini memerlukan Python 3.11+:

```sh
python pusingcuk_new.py path/ke/program.cuk
```

Contoh program ada di [examples](examples/). Pustaka dan kontraknya dijelaskan di [library](library/README.md); panduan perangkat ada di [Termux](docs/termux/README.md).

## Struktur proyek

| Area | Tanggung jawab |
|---|---|
| `.cuk` | Program pengguna, contoh, fixture, dan aturan bisnis |
| `lexer.py`, `parser.py`, `evaluator.py` | Jalur referensi untuk parsing dan eksekusi |
| `compiler/`, `native/` | IR, VM eksperimental, dan backend dengan cakupan berbeda |
| `library/` | Built-in, kontrak, kosakata, adapter, dan pengetahuan PusingCuk AI |
| `apps/`, `web/`, `site/`, `supabase/` | Prototipe aplikasi/integrasi; bukan bukti otomatis bahwa SaaS siap produksi |
| `tests/`, `tests/conformance/` | Regresi dan kontrak perilaku target |
| `docs/` | Panduan pengguna, arsitektur, kompatibilitas, dan status |

Indeks dokumentasi: [docs/README.md](docs/README.md). Visi: [docs/VISION.md](docs/VISION.md). Spesifikasi: [SPEC.md](SPEC.md). Kontrak semantik: [docs/SEMANTIC_CONTRACT.md](docs/SEMANTIC_CONTRACT.md).

## Bukti dukungan, bukan klaim

Manifest saat ini memuat **78 fixtures**: all 78 are required on the Python reference interpreter, 75 are required on native C, and 3 are explicitly unsupported on native C. Fixture native dijalankan pada GCC dan Clang di CI. Ini membuktikan hanya perilaku yang tercakup fixture, bukan seluruh bahasa atau semua platform.

- **Python reference:** implementasi pembanding utama saat ini; masih membutuhkan Python.
- **Native C:** dapat menghasilkan executable yang berjalan tanpa Python untuk subset yang didukung; ini belum berarti semua sintaks/built-in sudah mandiri.
- **JavaScript, Python transpiler, dan VM:** cakupan target berbeda. Fitur yang belum didukung harus ditandai, bukan diasumsikan setara.
- **PusingCuk AI:** membantu menulis dan memperbaiki program melalui engine/provider yang tersedia. Ini bukan foundation model yang dilatih sendiri oleh PusingCuk.
- **PusingCuk AI local service:** `pusingcuk-ai-service` adalah adapter HTTP lokal eksperimen. Baca [docs/AI_LOCAL_SERVICE.md](docs/AI_LOCAL_SERVICE.md); layanan ini bukan public hosted service dan tidak boleh dianggap deployment SaaS.
- **Web, Android, dan SaaS:** prototipe sampai build, autentikasi, integrasi, dan alur utama benar-benar diverifikasi pada target yang sama.

Matriks: [kompatibilitas](docs/COMPATIBILITY.md), [target compiler](docs/COMPILER_TARGETS.md), serta [kontrak built-in](library/builtin_contract.json).

## Program nyata yang diuji lintas runtime

Contoh [kasir warung](examples/kasir_warung.cuk) menghitung subtotal Rp40.000, diskon Rp4.000, nilai setelah diskon Rp36.000, pajak 11% Rp3.960, dan total Rp39.960. Program yang sama wajib menghasilkan output identik di interpreter referensi Python dan runtime native C; hasilnya diverifikasi oleh suite konformansi CI, bukan sekadar klaim dokumentasi.

Jalankan interpreter referensi dengan `python pusingcuk_new.py examples/kasir_warung.cuk`. Untuk runtime native, bangun `pusingcuk-native` lalu jalankan `./pusingcuk-native examples/kasir_warung.cuk`.

## Prinsip pengembangan

1. Satu kontrak semantik; setiap target yang belum mendukung fitur harus menolaknya dengan jelas.
2. Fitur baru harus memperlihatkan program nyata, hasil yang dapat diperiksa, dan fixture regresi.
3. AI boleh mengusulkan kode, tetapi compiler dan runtime menentukan validitasnya.
4. Runtime bukan sandbox OS untuk kode tidak tepercaya.
5. Jangan menambah kata kunci atau dokumen tanpa kebutuhan pengguna dan bukti perilaku.

## Kontribusi dan keamanan

- [Panduan kontribusi](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Kebijakan keamanan](SECURITY.md)
- [Catatan perubahan](CHANGELOG.md)

Lisensi: MIT.
