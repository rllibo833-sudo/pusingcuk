# PusingCuk

PusingCuk adalah bahasa pemrograman eksperimental dengan ekstensi `.cuk`, kata kunci berbahasa Indonesia, dan identitas sintaks sendiri. Proyek ini berfokus pada bahasa, interpreter, compiler, runtime, dan contoh program yang bisa dijalankan serta dikembangkan oleh kontributor.

**Status:** kontrak bahasa `0.6-dev`; paket Python `0.8.0.dev0`. Ini masih tahap pengembangan, bukan rilis stabil. Dukungan tiap backend berbeda; jangan menganggap semua program berjalan identik di semua target.

## Coba .cuk

Persyaratan: Python 3.11 atau 3.12.

```sh
python pusingcuk_new.py halo.cuk
```

Contoh isi `halo.cuk`:

```cuk
jancuk
lah nama = "Dunia"
hedeh "Halo, " + nama
selesai jancuk
```

Periksa sintaks tanpa menjalankan:

```sh
python pusingcuk_new.py --check halo.cuk
```

## Jalur proyek

- `lexer.py`, `parser.py`, `evaluator.py`: jalur referensi bahasa.
- `compiler/`: IR dan backend compiler dengan batas dukungan masing-masing.
- `native/`: runtime C untuk subset bahasa yang dinyatakan didukung.
- `library/`: built-in dan kontrak bahasa.
- `examples/`: program contoh.
- `tests/conformance/`: fixture untuk mengunci perilaku bahasa.

Mulai dari [spesifikasi bahasa](SPEC.md), [kontrak semantik](docs/SEMANTIC_CONTRACT.md), dan [panduan kontribusi](CONTRIBUTING.md). Pilih fixture konformansi saat mengubah perilaku bahasa.

## Batas keamanan

Interpreter dan backend bukan sandbox sistem operasi. Jangan menjalankan kode .cuk atau bytecode yang tidak dipercaya pada lingkungan sensitif. VM eksperimental tidak otomatis memberikan isolasi keamanan.

## Lisensi

MIT. Kontribusi untuk memperbaiki bahasa, runtime, compiler, contoh, dan kompatibilitas sangat diterima.
