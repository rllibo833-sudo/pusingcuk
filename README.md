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

Tool yang tersedia hanya pencarian dokumen read-only dan aturan anggaran terdaftar melalui runner Docker lokal yang dilindungi token. Tanpa runner tersebut, tool anggaran gagal dengan aman. Model tidak dapat mengirim source code arbitrer untuk dieksekusi. Jangan mengekspos runner ke internet.

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
- **AI Engine:** [Grounding contract](docs/AI_KNOWLEDGE_GROUNDING.md) · [Production readiness gates and knowledge migration policy](docs/AI_ENGINE_READINESS.md)
- **Development:** [Contributor guide](CONTRIBUTING.md) · [Development and test gates](docs/development/README.md) · [Repository map](docs/REPO_STRUCTURE.md)
- **Security:** [Security policy](SECURITY.md) · [Security review guide](docs/security/README.md)
- **CORE integration:** [Tool contract and trust boundary](docs/integrations/CORE_TOOL_CONTRACT.md) · [Local registered-rule runner](tools/core-rule-runner.mjs)
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

## What is deliberately deferred

Transpiler backends, PVM extensions, and Android Studio APK development are experimental and are not the current compatibility baseline. Existing code and design notes are retained for future work, but their presence does not mean production support. The current priority is to align the specification, vocabulary registry, Python interpreter, native C runtime, and executable conformance tests.

## Security

Do not run code or bytecode from an untrusted source with access to important files, credentials, or accounts. Runtime limits and restricted expression parsers are not operating-system isolation. Read [SECURITY.md](SECURITY.md) before using Pusingcuk in a security-sensitive context.

## License

MIT. See [LICENSE](LICENSE).
