# Pusingcuk

Pusingcuk is an experimental programming language built around Indonesian-friendly keywords and readable examples. Its near-term goal is not to support every compiler target; it is to make one language behave predictably across its **Python reference interpreter** and **native C runtime**.

**Canonical language version:** `0.5-dev`. Development package metadata is `0.8.0.dev0` (PEP 440 spelling for the `0.8.0-dev` line). New programs use `.cuk`; `.pusingcuk` remains a compatibility extension.

### Runtime capability matrix

| Target | Contracted built-ins | Status |
|---|---:|---|
| Reference Python | 21 | Full contracted built-in set; additional reference-only intrinsics are separate |
| Native C | 17 fully claimed + 4 scalar conversion subsets | Tested C11 runtime; no file I/O, HTTP, or module system. Full parity for the four conversion built-ins is not claimed; `teks()` does not stringify collections |
| JS transpiler | 14 | Subset |
| Python transpiler | 14 | Subset |
| VM | 6 | Experimental |


[![Core CI](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/tests.yml)
[![Packaging](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/build-test.yml/badge.svg?branch=main)](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/build-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Status:** experimental. Python defines the reference behavior; native C implements a tested subset. A feature is portable between them only when the same conformance fixture passes on both. Pusingcuk is not a security sandbox.
>
> **Security warning:** Eksekusi PusingCuk tidak ter-sandbox OS. Jangan jalankan kode tidak terpercaya. Execution runs with the current process's operating-system permissions; do not run untrusted code or bytecode.
>
> **Status & roadmap (16 Oct 2026):** lihat [audit status bahasa, AI dan Supabase](docs/PROJECT_STATUS_AND_ROADMAP.md). Bahasa `.cuk` dan aplikasi PusingCuk AI mempunyai tingkat kematangan berbeda. AI adalah aplikasi di atas Ollama atau Gemini, bukan foundation model yang dilatih sendiri. Supabase project PusingCuk saat ini belum menjadi koneksi runtime.

## Try Pusingcuk on Termux

Install Python and Git, then run the example directly from the source tree:

```sh
pkg update
pkg install python git
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
python pusingcuk_new.py halo.cuk
```

The same Python command works on Linux and other systems with Python 3.11 or 3.12 installed. The optional `pusingcuk` CLI can be installed with `python -m pip install .`; see the [Termux guide](docs/termux/README.md) for setup details.

## Asisten AI lokal (eksperimental)

PusingCuk sekarang memiliki MVP asisten lokal yang menggabungkan Ollama, indeks pengetahuan terkurasi, memori percakapan sementara, sitasi sumber tervalidasi, dan dua tool yang diizinkan. Ini belum setara dengan layanan foundation-model seperti Gemini dan belum menjadi layanan publik/produksi.

Untuk jalur lokal tanpa API key, siapkan Ollama dan jalankan CLI:

```sh
ollama pull qwen3:4b
python -m pip install .
pusingcuk-ai --provider ollama --model qwen3:4b
```

Ollama harus berjalan di perangkat yang sama dan mendengarkan di loopback port 11434. Tidak diperlukan API key, tetapi model memerlukan ruang penyimpanan dan RAM.

Sebagai opsi provider terpisah, PusingCuk juga menyediakan adapter independen untuk Gemini GenerateContent API. Atur `GEMINI_API_KEY` di environment (jangan simpan kunci di repository), lalu jalankan `pusingcuk-ai --provider gemini`. Model default adalah `gemini-3.8-flash` dan dapat diganti dengan `--model`. Pemakaian API tunduk pada ketersediaan model, kuota, dan ketentuan akun Google. Kunci dikirim melalui header HTTPS, tidak ditulis ke URL atau log. Provider ini opsional dan memakai layanan eksternal; bukan jalur model lokal tanpa biaya. Ketik `/reset` untuk menghapus konteks sesi atau `/keluar` untuk berhenti. Riwayat chat tidak disimpan ke disk. Catatan proyek yang ingin dipertahankan harus disimpan secara eksplisit dengan `/ingat <catatan>`, dilihat melalui `/memori [kueri]`, dan dihapus dengan `/hapus-memori <id>`. Catatan tersimpan berada di file lokal pengguna, dibatasi jumlah/ukuran, dan pola kredensial umum ditolak.

Tool yang tersedia mencakup pencarian dokumen read-only (`knowledge_search`), aturan anggaran (`budget_threshold`), pemeriksaan jurnal (`journal_balance_check`), persamaan akuntansi (`accounting_equation_check`), rencana penutupan periode (`period_close_plan`), serta diagnosis klasifikasi laporan (`report_classification_check`) melalui `ToolRegistry` internal. Diagnosis klasifikasi menerima hitungan agregat dan menandai kategori arus kas/ekuitas yang hilang; ia tidak membaca atau mengubah buku pengguna. Semua rule `.cuk` dipatok dengan SHA-256 dan menerima input sesuai skema; model tidak dapat mengirim source code arbitrer untuk dieksekusi. Eksekusi runtime referensi lokal tetap **bukan sandbox OS**, sehingga hanya artefak tetap yang telah ditinjau boleh didaftarkan. `tools/core-rule-runner.mjs` masih dipertahankan sebagai harness kompatibilitas/integrasi terpisah untuk pengujian lintas-repo dan regresi sandbox; runner tersebut bukan dependensi runtime assistant. Jangan mengekspos runner lama atau layanan lokal AI ke internet.

### Layanan HTTP AI lokal (eksperimental)

Paket ini juga menyediakan `pusingcuk-ai-service` untuk klien lokal melalui `POST /v1/chat`. Service mewajibkan bearer token kuat, menolak bind non-loopback, membatasi payload/sesi/konkurensi, dan tidak menyimpan chat ke disk. Ini belum punya TLS, identitas per pengguna, rate limit produksi, streaming, atau deployment publik. Jangan melakukan port-forward atau menaruh token di JavaScript browser. Lihat [kontrak dan cara menjalankan](docs/AI_LOCAL_SERVICE.md).

## First program

```cuk
jancuk
lah angka = 40
hedeh angka + 2
selesai jancuk
```

Run it with:

```sh
python pusingcuk_new.py program.cuk
python pusingcuk_new.py --check program.cuk
```

### Build a standalone JavaScript program

The experimental JavaScript backend can compile supported `.cuk` programs into a `.js` file that runs with Node.js. Install the project first with `python -m pip install .`, then:

```sh
pusingcuk-build examples/halo_dunia.cuk --output halo_dunia.js
node halo_dunia.js
```

The build command validates the source and stops with a compilation error when it encounters unsupported syntax or features. The generated file does not need Python at runtime, but it does need Node.js. This is an experimental JavaScript target—not an Android APK, Windows EXE, or browser application package.


The `.cuk` extension is Pusingcuk's canonical source-file identity for new programs. The distinctive identity comes from its Indonesian-readable syntax and tested language rules—not the suffix alone. Existing `.pusingcuk` files remain supported for compatibility.

Metadata paket pada `main` adalah `0.8.0.dev0` (`pyproject.toml`, `Makefile`, `library/kosakata.json`, dan fallback runtime native); kontrak bahasa tetap `0.5-dev` (`lexer.py`, `SPEC.md`). Tag rilis yang lebih lama tetap menunjuk snapshot historis; metadata pengembangan saat ini menggunakan versi paket PEP 440 `0.8.0.dev0`. Gunakan `make version` dan `make language-version` untuk memeriksa keduanya.

After installing the CLI, run `pusingcuk script.cuk` directly. Executable scripts can start with `#!/usr/bin/env pusingcuk` and use `chmod +x script.cuk`; the CLI must be installed and on `PATH`.

For Linux desktop MIME registration, install `pusingcuk.xml` into `~/.local/share/mime/packages/` and run `update-mime-database ~/.local/share/mime`. MIME registration is a desktop/Linux facility; Termux shell execution uses the shebang and `PATH`.


## Menjalankan skrip .cuk

Mulai dari [indeks contoh](examples/README.md), termasuk kalkulator dasar yang memakai keyword inti `njir` dan `kampret`.

Gunakan CLI Python dari direktori repositori:

```sh
pusingcuk examples/halo_dunia.cuk
# atau jalankan langsung setelah CLI terpasang dan ada di PATH:
./examples/halo_dunia.cuk
```

Contoh keuangan meminta pemasukan dan pengeluaran, lalu menyimpan catatan relatif `keuangan_sederhana.txt` di direktori project. Operasi berkas interpreter dibatasi ke project root; jangan jalankan program yang tidak dipercaya.

## Two maintained execution paths

| Path | What it is | Important limit |
|---|---|---|
| Python reference | The modular interpreter launched by `pusingcuk_new.py`; reference for language behavior | Requires Python; host file/network capabilities are not a sandbox |
| Native C | A standalone C11 runtime built with GCC or Clang; no Python needed at runtime | Seventeen built-ins are verified, including logarithms, trigonometry, summation, and statistics, alongside arithmetic, collection, scope, numeric-domain, and error fixtures; the native module system is not available |

For the native C runtime on Termux:

```sh
pkg install git clang make
bash scripts/install-termux.sh
pusingcuk-native examples/rekap_anggaran.cuk
```

The native runtime and its limits are documented in the [native runtime guide](docs/NATIVE_RUNTIME.md). The existing Linux `pusingcuk` release asset is not a Termux ARM64 binary. Choose an explicitly named Android ARM64 native asset when available, or build from source; physical Termux device compatibility must not be inferred from Ubuntu CI alone.

## Documentation map

- **Start and learn:** [Beginner guide](docs/PEMULA.md) · [Termux quick start](docs/termux/README.md) · [Examples index](examples/README.md)
- **Language reference and dictionary:** [Language reference index](docs/language/README.md) · [Built-in catalogue](docs/language/BUILTINS.md) · [Syntax specification](SPEC.md) · [English dictionary](docs/DICTIONARY.md) · [Kamus Indonesia](docs/KAMUS_PUSINGCUK.md)
- **Consistency and runtime support:** [Semantic contract](docs/SEMANTIC_CONTRACT.md) · [Compatibility matrix](docs/COMPATIBILITY.md) · [Conformance fixtures](docs/CONFORMANCE_FIXTURES.md)
- **AI Engine:** [Status & roadmap](docs/PROJECT_STATUS_AND_ROADMAP.md) · [Grounding contract](docs/AI_KNOWLEDGE_GROUNDING.md) · [Readiness gates](docs/AI_ENGINE_READINESS.md) · [Knowledge migration ledger](docs/AI_ENGINE_MIGRATION_LEDGER.md) · [Local HTTP service](docs/AI_LOCAL_SERVICE.md)
- **Development:** [Contributor guide](CONTRIBUTING.md) · [Development and test gates](docs/development/README.md) · [Repository map](docs/REPO_STRUCTURE.md)
- **Security:** [Security policy](SECURITY.md) · [Security review guide](docs/security/README.md)
- **Registered-rule compatibility harness (historical naming):** [Tool contract and trust boundary](docs/integrations/CORE_TOOL_CONTRACT.md) · [Legacy runner used only by regression/security tests](tools/core-rule-runner.mjs). These are PusingCuk-owned test artifacts, not a live CORE repository or Supabase connection.
- **Complete documentation index:** [docs/README.md](docs/README.md)

## Quality gates

Run the same checks used by the maintained Python/C baseline:

```sh
python -m unittest discover -s tests -v
make test-native
python tools/conformance.py
python tests/conformance/runner.py
```

CI tests the reference interpreter on Python 3.11 and 3.12 and builds the native runtime with GCC and Clang. The manifest distinguishes required, optional, and unsupported runtime behavior; unsupported features are not counted as parity.

## Development status and next steps

PusingCuk is still experimental. The current language contract is `0.5-dev`; the Python package version `0.8.0.dev0` is separate. The active conformance manifest contains **67 fixtures**: all 67 are required on the Python reference interpreter, 62 are required on native C, and 5 are explicitly unsupported on native C. Unsupported fixtures are not counted as passes or cross-runtime parity.

Recent engineering work has added regression coverage for the local AI path from HTTP chat handling through the allowlisted tool registry and a registered `.cuk` rule to a generated JavaScript artifact. The CukAccount shared synthetic acceptance dataset now feeds both the Dart/SQLite report-and-close tests and the registered `period_close_plan` rule. That rule classifies profit/loss/zero and returns a deterministic role-based closing-line plan for comparison with SQLite's actual closing journal; it never posts transactions. These deterministic checks do not post real transactions and are not proof of general live-model quality or production readiness.

The next work follows [the project vision](docs/VISION.md):

1. Check parser diagnostics and boundary/error fixtures; add tests only where a real gap is found.
2. Keep the AI tool path deterministic: allowlisted tools, validated inputs, pinned rule/artifact provenance, and trustworthy citations.
3. Review Indonesian retrieval failures using the existing curated benchmark before changing ranking or expanding the index.
4. Continue accounting-rule validation after the language and AI acceptance paths remain reproducible.

The Python interpreter is the behavior reference; native C compatibility is claimed only for shared fixtures that pass on both. Transpilers and VM remain experimental. CI success means configured checks passed, not that every feature is supported or that the runtime is a security sandbox. See the [technical status and roadmap](docs/PROJECT_STATUS_AND_ROADMAP.md) for the broader component-by-component status.

## What is deliberately deferred

Transpiler backends, PVM extensions, and Android Studio APK development are experimental and are not the current compatibility baseline. Existing code and design notes are retained for future work, but their presence does not mean production support. The current priority is to align the specification, vocabulary registry, Python interpreter, native C runtime, and executable conformance tests.

## Security

Do not run code or bytecode from an untrusted source with access to important files, credentials, or accounts. Runtime limits and restricted expression parsers are not operating-system isolation. Read [SECURITY.md](SECURITY.md) before using Pusingcuk in a security-sensitive context.

## License

MIT. See [LICENSE](LICENSE).

## Integrasi CukAccount dan siklus evaluasi AI — 16 Oktober 2026

CukAccount menggunakan PusingCuk sebagai runtime ber-pin untuk menjalankan fixture keuangan sintetis di CI. Pin yang dipakai bridge adalah `5732076cb04b90b259b7e9d6beba8ff72b3ad117`; perubahan versi harus diikuti pengujian ulang bridge dan pembaruan kontrak pada kedua repositori. Fixture kini memiliki pemeriksaan senyap untuk penutupan laba/rugi/hasil nol agar output sukses lama tetap stabil; jika rumus meleset, marker kegagalan tambahan membuat perbandingan output gagal. Jangan menganggap output fixture sebagai posting transaksi atau sumber kebenaran ledger.

Siklus peningkatan PusingCuk AI yang dapat diverifikasi:
1. Gunakan dokumentasi terkurasi dan contoh finansial sintetis, bukan data keuangan pribadi.
2. Minta AI menjelaskan aturan atau mengusulkan contoh .cuk; jangan jalankan kode yang dihasilkan tanpa tinjauan.
3. Jalankan `--check`, tes interpreter referensi, serta konformansi native C bila fixture mengklaim dukungan lintas-runtime.
4. Bandingkan output dan diagnostik dengan expected result, lalu simpan kegagalan yang direproduksi sebagai regresi.
5. Nilai perubahan dengan suite yang sama sebelum mengubah kontrak bahasa atau pin integrasi.

Ini adalah peningkatan berbasis konteks, aturan deterministik, dan evaluasi regresi—bukan bukti bahwa bobot model telah dilatih ulang. Bahasa masih eksperimental; native C, transpiler, dan VM memiliki cakupan yang berbeda. Eksekusi .cuk bukan sandbox OS, jadi jangan jalankan kode tak tepercaya.

Acuan aplikasi: [CukAccount — spesifikasi dan roadmap](https://github.com/rllibo833-sudo/Cukaccount/blob/main/CUKACCOUNT_SPEC_AND_ROADMAP.md). Status APK CukAccount saat ini adalah APK uji, bukan rilis produksi.


## Siklus penerimaan CukAccount ↔ PusingCuk AI ↔ `.cuk` — 16 Oktober 2026

CukAccount menyediakan kebutuhan akuntansi dan fixture sintetis; aturan `.cuk` serta `ToolRegistry` PusingCuk AI menganalisis kasus deterministik; hasilnya dibandingkan kembali dengan output Dart/SQLite. Workflow CukAccount mem-pin commit PusingCuk `862402c1e8243394ecbc3d3c469a15a5e19a0c95` dan membandingkan dataset bersama, termasuk rencana penutupan laba/rugi/nol serta input tidak valid.

**Batas bukti:** [tes upstream PusingCuk](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/38826340175) pada pin tersebut sukses. Itu tidak membuktikan Flutter checks CukAccount pada head UI terbaru lulus; perubahan UI terbaru belum terverifikasi dan pemeriksaan format gagal. Sukses upstream saja tidak menutup siklus.
