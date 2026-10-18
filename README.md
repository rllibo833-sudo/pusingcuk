# PusingCuk

PusingCuk adalah proyek bahasa pemrograman eksperimental dengan ekstensi utama `.cuk`, kata kunci Indonesia, dan identitas bahasa lokal. Tujuannya: membuat pemrograman mudah dipelajari tanpa mengorbankan aturan yang jelas, diagnostik yang berguna, dan perilaku yang bisa diuji.

**Status versi:** kontrak bahasa `0.6-dev`; versi paket Python `0.8.0.dev0`. Keduanya berbeda. Status ini bukan klaim rilis stabil.

## Mulai cepat

Persyaratan jalur referensi saat ini: Python 3.11+.

```sh
python pusingcuk_new.py halo.cuk
```

Untuk melihat contoh lain, mulai dari [examples](examples/) dan [library](library/README.md). Petunjuk perangkat tersedia di [panduan Termux](docs/termux/README.md).

## Struktur proyek

| Bagian | Kegunaan |
|---|---|
| `.cuk` | Program pengguna, contoh, dan aturan bisnis yang ditulis dalam bahasa PusingCuk |
| `lexer.py`, `parser.py`, `evaluator.py` | Jalur referensi saat ini untuk membaca, memvalidasi sintaks, dan menjalankan program |
| `compiler/` | IR, bytecode/VM eksperimental, serta backend C, JavaScript, Python, dan Android dengan cakupan berbeda |
| `library/` | Built-in, kontrak mesin, kosakata, adapter, dan modul contoh; bukan semua komponen di sini merupakan modul PusingCuk yang bisa diimpor |
| `web/`, `site/`, `apps/`, `supabase/` | Prototipe UI, layanan, dan integrasi; tidak otomatis berarti siap produksi |
| `tests/` | Tes regresi, fixture konformansi, dan pemeriksaan kontrak |
| `docs/` | Dokumentasi yang dikelompokkan menurut kebutuhan pengguna dan fungsi teknis |

Peta lengkap: [indeks dokumentasi](docs/README.md). Tujuan bahasa: [Vision](docs/VISION.md). Perilaku bahasa yang berlaku: [SPEC.md](SPEC.md) dan [kontrak semantik](docs/SEMANTIC_CONTRACT.md).

## Apa yang sudah dan belum mandiri?

- **Jalur referensi:** interpreter Python adalah implementasi pembanding utama saat ini.
- **Native C:** dapat menghasilkan program native tanpa interpreter Python saat program hasil kompilasi dijalankan, tetapi dukungan fiturnya masih subset.
- **JavaScript/Python transpiler dan bytecode VM:** memiliki batas dukungan tersendiri; jangan menganggap semua fitur setara.
- **PusingCuk AI:** aplikasi bantu yang memakai engine/provider yang tersedia untuk membantu menulis dan memperbaiki kode. Ini **belum** berarti PusingCuk memiliki foundation model yang dilatih sendiri.
- **Web, Android, dan layanan SaaS:** sebagian merupakan prototipe. Build, runtime, login, dan integrasi harus dinyatakan siap hanya jika telah dibuktikan pada target yang bersangkutan.

Matriks dukungan yang rinci: [kompatibilitas](docs/COMPATIBILITY.md), [target compiler](docs/COMPILER_TARGETS.md), dan kontrak built-in di `library/builtin_contract.json`.

## Prinsip pengembangan

1. Satu kontrak bahasa; backend yang belum mendukung fitur harus menolaknya dengan jelas.
2. Perubahan semantik disertai tes/fixture yang menunjukkan perilaku yang diharapkan.
3. AI boleh mengusulkan kode, tetapi compiler dan runtime yang menentukan apakah kode valid dan berperilaku benar.
4. Jangan menyebut eksekusi kode tidak tepercaya aman: runtime saat ini bukan sandbox OS.
5. Pertahankan bahasa sederhana, ringan, dan ramah pemula; jangan menambah fitur atau dokumen tanpa kegunaan nyata.

## Kontribusi dan keamanan

- [Panduan kontribusi](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Kebijakan keamanan](SECURITY.md)
- [Catatan perubahan](CHANGELOG.md)

Lisensi: MIT.
