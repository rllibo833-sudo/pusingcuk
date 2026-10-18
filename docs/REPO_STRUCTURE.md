# Struktur Repo Berdasarkan Fungsi

Gunakan peta ini untuk menemukan lokasi yang benar sebelum mengubah kode. Ini bukan daftar setiap berkas.

## Bahasa .cuk

| Lokasi | Fungsi |
|---|---|
| `lexer.py` | Membaca token dan alias keyword |
| `parser.py`, `ast_nodes.py` | Sintaks dan AST |
| `evaluator.py` | Interpreter referensi dan semantik runtime utama |
| `SPEC.md` | Kontrak sintaks/fitur yang terlihat oleh pengguna |
| `docs/SEMANTIC_CONTRACT.md` | Perilaku yang harus konsisten |
| `examples/`, `*.cuk`, `library/*.cuk` | Program contoh dan aturan yang ditulis dalam .cuk |

## Compiler dan runtime

| Lokasi | Fungsi |
|---|---|
| `compiler/ir.py`, `compiler_ir.py` | Representasi perantara dan validasi |
| `compiler/bytecode.py`, `compiler/vm.py` | Kompilasi bytecode dan VM eksperimental |
| `compiler/c_backend.py`, `native/` | Backend/runtime C; periksa batas dukungan sebelum mengklaim parity |
| `compiler/js_backend.py` | Backend JavaScript |
| `compiler/python_backend.py`, `compiler/import_python.py` | Transpilasi dan interoperabilitas Python |
| `compiler/android_backend.py`, `android-studio/` | Eksperimen target Android |
| `tests/conformance/`, `tools/conformance.py` | Fixture dan pemeriksaan perilaku lintas-target |

## Library dan PusingCuk AI

| Lokasi | Fungsi |
|---|---|
| `library/stdlib.py` | Implementasi built-in untuk jalur referensi |
| `library/builtin_contract.json`, `builtin_contract.py` | Metadata kontrak built-in dan status dukungan target |
| `library/kosakata.json` | Registri keyword/alias yang dapat dibaca mesin |
| `library/assistant.py`, `library/ai_tools.py` | Asisten, orkestrasi tool, dan jembatan ke compiler |
| `library/knowledge_grounding.py`, `knowledge_index.json` | Grounding dan indeks pengetahuan |
| `library/*_provider.py` | Adapter model yang tersedia; jangan menganggap semuanya wajib/aktif |
| `library/*.cuk`, `*.pusingcuk` | Contoh atau aturan bahasa, bukan implementasi Python |

**Penting:** folder bernama `library` mencampur runtime Python, metadata, adapter, dan contoh .cuk. Tidak semua file di folder tersebut adalah pustaka standar mandiri untuk program .cuk.

## Frontend, backend, dan layanan

| Lokasi | Fungsi |
|---|---|
| `web/`, `site/` | UI web/prototipe frontend |
| `apps/` | Aplikasi dan prototipe terpisah |
| `supabase/` | Skema/fungsi integrasi Supabase yang tersedia di repo |
| `tools/`, `scripts/` | Utilitas pengembangan, konformansi, dan packaging |
| `.github/workflows/` | Otomasi CI/build; hasilnya hanya membuktikan job yang benar-benar berjalan |

## Dokumentasi: mana yang harus dibaca?

- Pengguna baru: [README](../README.md) → [PEMULA](PEMULA.md) → [SPEC](../SPEC.md).
- Mengubah sintaks/semantik: [SPEC](../SPEC.md) → [kontrak semantik](SEMANTIC_CONTRACT.md) → tes/fixture → matriks [kompatibilitas](COMPATIBILITY.md).
- Mengubah backend: dokumen backend terkait → tes backend → fixture target.
- Mengubah AI: [kesiapan engine](AI_ENGINE_READINESS.md) → [jembatan evolusi bahasa](AI_LANGUAGE_EVOLUTION_BRIDGE.md) → tes AI.
- Mengubah UI/API: dokumentasi workbench atau integrasi yang sesuai; jangan mencampur logika bisnis ke frontend.

## Aturan perubahan

1. Perubahan bahasa memperbarui spesifikasi, implementasi, fixture, dan status dukungan secara bersamaan.
2. Jangan menambah alias/built-in hanya untuk memperbanyak jumlah fitur.
3. Jangan menyatakan target kompatibel jika fixture target belum lulus.
4. Catatan audit bertanggal tetap historis. Status aktif harus ditulis hanya berdasarkan commit dan hasil pemeriksaan yang benar-benar tersedia.
