# PusingCuk

> **Bahasa warung. Mesin serius.**  
> PusingCuk adalah bahasa pemrograman eksperimental dengan ekstensi `.cuk`, kata kunci berbahasa Indonesia, dan kosakata yang punya identitas sendiri.

PusingCuk menggabungkan sintaks yang mudah dikenali penutur Indonesia dengan jalur interpreter, compiler, runtime native, serta alat konformansi.

**[Coba di browser →](https://rllibo833-sudo.github.io/pusingcuk/playground.html)** — playground eksperimental tahap awal; mesin sementaranya Python melalui Pyodide, bukan runtime .cuk asli.

<!-- BEGIN GENERATED PYTHON-FREE SCORE BADGE -->
[![Python-free runtime · native C · 74/77 fixtures](docs/assets/python-free-score.svg)](docs/PYTHON_FREE_SCORE.md)
Python-free runtime, native C: **74 dari 77 fixture aktif lulus**. Ini cakupan fixture runtime native C, bukan klaim bahwa seluruh proyek atau proses build bebas Python.
<!-- END GENERATED PYTHON-FREE SCORE BADGE -->

Proyek ini ditujukan untuk belajar, eksperimen bahasa, dan pengembangan compiler secara terbuka—bukan untuk mengklaim bahwa semua target sudah setara atau siap produksi.

**Status:** kontrak bahasa `0.6-dev`; paket Python `0.8.0.dev0`. **Metadata paket pada `main` adalah `0.8.0.dev0`.** Ini perangkat lunak tahap pengembangan, bukan rilis stabil. Dukungan tiap backend berbeda dan harus diperiksa melalui matriks kompatibilitas serta fixture.

## Tiga komponen ekosistem\n\n- **Bahasa .cuk:** spesifikasi, interpreter, runtime, dan backend. Lihat [IDENTITY.md](IDENTITY.md).\n- **PusingCuk AI:** asisten yang di-ground dengan pengetahuan bahasa; bukan model fondasi yang dilatih dari nol.\n- **Cuk Reality Engine:** alat pembuktian konformansi lintas target; klaim kompatibilitas harus didukung eksekusi fixture.\n\nMulai kontribusi dari HP lewat [START_HERE.md](START_HERE.md). Draft issue rekonstruksi ada di [ISSUES_TO_CREATE.md](ISSUES_TO_CREATE.md); periksa issue yang sudah ada sebelum membuat duplikat.\n\n## Coba program pertama

Persyaratan: Python 3.11 atau 3.12.

Simpan sebagai `halo.cuk`:

```cuk
jancuk
lah nama = "Dunia"
hedeh "Halo, " + nama
selesai jancuk
```

Jalankan dan periksa sintaks:

```sh
python pusingcuk_new.py halo.cuk
python pusingcuk_new.py --check halo.cuk
```

## Apa isi repositori ini?

| Area | Fungsi |
|---|---|
| Bahasa inti | Lexer, parser, AST, interpreter referensi, spesifikasi, dan kontrak semantik |
| Compiler | IR dan target eksperimental JavaScript, Python, HTML, JSON IR, dan VM |
| Runtime native | Implementasi C untuk subset bahasa yang memiliki pengujian |
| Pustaka dan kosakata | Built-in, kontrak mesin, kata kunci, dan alias slang |
| PusingCuk AI | Asisten dan alat bantu untuk alur pengembangan .cuk; bukan bukti bahwa model fondasi dilatih sendiri |
| Konformansi | Tes otomatis dan fixture untuk membuktikan perilaku pada target yang dinyatakan |
| Contoh dan dokumentasi | Program belajar, kamus, panduan runtime, batas kompatibilitas, dan catatan pengembangan |

## Jalur membaca

- **Baru mulai:** [Panduan pemula](docs/PEMULA.md)
- **Aturan bahasa:** [Spesifikasi](SPEC.md) → [Kontrak semantik](docs/SEMANTIC_CONTRACT.md)
- **Dukungan nyata per target:** [Kompatibilitas](docs/COMPATIBILITY.md) dan [fixture konformansi](docs/CONFORMANCE_FIXTURES.md)
- **Kamus:** [Kamus Bahasa Warung](docs/KAMUS_PUSINGCUK.md) · [Dictionary (English)](docs/DICTIONARY.md)
- **Peta dokumentasi:** [docs/README.md](docs/README.md)
- **Gambaran proyek dan batasnya:** [Ikhtisar proyek](docs/PROJECT_OVERVIEW.md) · [Project overview (English)](docs/PROJECT_OVERVIEW_EN.md)
- **Kontribusi dan keamanan:** [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md)

## Status fitur: baca dengan konteks

- **Tersedia** berarti ada implementasi di repositori.
- **Teruji** berarti pengujian tertentu berjalan pada commit dan target yang disebutkan.
- **Eksperimental** berarti perilaku, cakupan, atau antarmukanya masih dapat berubah.
- **Siap produksi** membutuhkan bukti tambahan: keamanan, kompatibilitas, packaging, operasi, dan pengujian pada lingkungan sasaran.

Keberadaan file, contoh, workflow, atau backend tidak otomatis membuktikan kesiapan produksi. Untuk perubahan bahasa, selaraskan spesifikasi, implementasi, fixture, dan matriks kompatibilitas.

## Batas keamanan

Interpreter, compiler, dan VM PusingCuk **bukan sandbox sistem operasi**. Jangan menjalankan kode .cuk atau bytecode yang tidak dipercaya pada perangkat atau lingkungan sensitif. Target native yang dapat berjalan tanpa Python setelah dikompilasi tidak berarti proses build-nya bebas Python, dan tidak menjamin isolasi keamanan.

## Lisensi

PusingCuk menggunakan lisensi MIT. Lihat [LICENSE](LICENSE) untuk ketentuannya.
