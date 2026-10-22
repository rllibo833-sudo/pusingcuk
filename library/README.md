# Library PusingCuk

Folder ini berisi beberapa jenis aset yang berbeda. **Tidak semua berkas di sini adalah pustaka standar .cuk yang mandiri.**

| Kelompok | Lokasi | Fungsi |
|---|---|---|
| Kontrak built-in | `builtin_contract.json`, `builtin_contract.py` | Nama, aritas, metadata, dan status dukungan per target |
| Implementasi referensi | `stdlib.py` | Implementasi built-in yang dipakai interpreter Python |
| Kosakata | `kosakata.json` | Registri keyword/alias dan status |
| Program .cuk | `*.cuk`, `*.pusingcuk` | Contoh dan aturan yang ditulis dalam bahasa |
| AI dan grounding | `assistant.py`, `ai_tools.py`, `knowledge_grounding.py`, `knowledge_index.json`, `local_memory.py` | Asisten, tool, indeks, dan konteks pengetahuan |
| Adapter | `*_provider.py`, `adapters/` | Konektor/adapter model; bukan bagian wajib runtime .cuk |

## Jalankan contoh

Dari root repository:

```sh
python pusingcuk_new.py library/conditional_logic.pusingcuk
python pusingcuk_new.py library/loops_functions_genz.pusingcuk
```

## Aturan perubahan

1. Periksa `SPEC.md` dan `docs/SEMANTIC_CONTRACT.md` sebelum mengubah perilaku.
2. Ubah `builtin_contract.json` hanya jika metadata/dukungan kontrak memang berubah; jangan menganggap nama terdaftar berarti implementasi tersedia.
3. Untuk perubahan keyword/alias, selaraskan lexer, parser bila perlu, `kosakata.json`, contoh, dan tes.
4. Untuk klaim dukungan target, tambahkan tes/fixture yang benar-benar menjalankan target tersebut.
5. Database, jaringan, browser, Web3, dan FFI bukan API lintas-runtime hanya karena disebut di metadata; setiap kapabilitas memerlukan adapter, izin, dan bukti target.

## Batas runtime

Interpreter referensi Python mendukung kontrak built-in lebih luas daripada beberapa backend. Native C, JavaScript, transpiler Python/HTML, dan VM memiliki cakupan berbeda. Lihat [kompatibilitas](../docs/COMPATIBILITY.md), [katalog built-in](../docs/language/BUILTINS.md), dan `builtin_contract.json`.

PusingCuk tidak menjamin sandbox OS untuk kode tidak tepercaya.


## String literal escapes

String literals on the native C runtime accept `\\n`, `\\t`, `\\r`, `\\"`, and `\\\\`. The self-hosting lexer uses carriage-return escapes when scanning source text, so native execution must preserve this contract.


## Self-hosting frontend driver

`examples/self_hosting/compiler.cuk` contains the reusable lexer/parser/IR implementation and remains parseable by its own frontend. `examples/self_hosting/compiler_driver.cuk` is the stdin JSON entrypoint. `tools/run_native_selfhost_frontend.sh` joins them at execution time, so driver-only input syntax does not contaminate the compiler source being self-parsed.
false