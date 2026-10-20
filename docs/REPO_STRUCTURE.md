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
| `datacenter_v6.py`, `V6_CLEAN.py`, `fix_parser_all.py` | DRY-RUN/review-only compatibility wrappers; do not mutate vocabulary, parser, or `app.cuk`, and do not commit/push |
| `lexer.orig.py`, `interpreter.py.bak`, `token_patch.py` | Root-level legacy backup/patch files; not the canonical lexer or active CLI entry point |
| `app.cuk`, `next_prompt.txt` | Mutable scratch artifacts used by the legacy V6 loop; not canonical language examples or conformance fixtures |
| `pusingcuk/` | Compatibility package facade; `pusingcuk/cli.py` imports the maintained root interpreter/parser, while `pusingcuk/lexer.py` is a mirrored lexer kept in sync by `scripts/check_alias_sync.py` |

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

## Experimental PVM v1

`src/` contains a separate draft PVM v1 toolchain; it is not the same runtime as `compiler/vm.py` and does not make the full `.cuk` language portable or sandboxed.

| Location | Function and boundary |
|---|---|
| `src/c-core/main.c` | C11 line-oriented PVM v1 assembler; format and opcode limitations are documented in `docs/PVM_SPEC.md` |
| `src/backends/python/compiler.py`, `src/backends/js/compiler.js` | PVM v1 readers/restricted transpilers with explicit file-I/O policy; these consume PVM records, not the compiler's JSON bytecode artifact |
| `compiler/vm.py` | Separate executable JSON bytecode VM for the regular compiler pipeline; instruction budgets are not an OS security sandbox |

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

## AI repair and language-evolution tools

| Location | Actual behavior on `main` | Limit to preserve in claims |
|---|---|---|
| `tools/diagnostic_repair_loop.py` | Reads an in-repository `.cuk`/`.pusingcuk` file and validates lexer/parser syntax | Does not execute source or apply repairs; expected-output checks fail closed without an isolated runtime |
| `tools/local_ai_adapter.py` | Separate Ollama/heuristic loop writes a sibling `*.proposal.cuk` file and asks the Reality Engine to validate it | Not the same path as `library/assistant.py`; a proposal must match a successful manifest fixture and pass all five target checks |
| `tools/reality_engine.py` | Deterministic fail-closed acceptance gate | Has reference/native/JavaScript/Python/VM execution paths; acceptance requires exact manifest source, exit 0, expected stdout, no stderr, and matching outputs |
| `tools/evolve_daemon.py` and `tools/evolve_language.py` | Explicit, review-only alias proposals | No automatic vocabulary edits, commits, or pushes |

**Important execution boundary:** the legacy V6 entry points are now dry-run/review-only wrappers. The canonical flow is proposal → human review → Reality Engine validation → separately reviewed Git change; no evolution helper pushes automatically.

## Generated documentation ownership

To avoid conflicting snapshots, each generated section has one writer:

- `scripts/gen_docs_from_spec.py` owns the SPEC-derived alias table in `README.md` and the generated language-contract section in `docs/AI_ENGINE_READINESS.md`.
- `tools/generate_compatibility.py` owns the conformance summary in `docs/COMPATIBILITY.md`, active fixture counts in `docs/CONFORMANCE_FIXTURES.md`, the Python-Free Score history in `docs/PYTHON_FREE_SCORE.md`, the README score badge, and its SVG.

Do not make both generators write the same markers. Run both `--check` modes after updating their respective source contracts.

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
