# Pusingcuk — The Indonesian Gen Z Programming Language. Coding tapi bahasa warung.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11 | 3.12](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![CI Status](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/tests.yml)
[![Termux Supported](https://img.shields.io/badge/Android-Termux%20supported-brightgreen.svg)](https://termux.dev/)

Pusingcuk is an experimental programming language with Indonesian-friendly keywords and local slang aliases. It aims to make coding approachable while building a testable interpreter, native C runtime, and experimental compiler backends.

> **Project status:** experimental, version 0.4-dev. Runtime and compiler support varies by feature. Pusingcuk is **not a security sandbox**; jangan jalanin program gak jelas di perangkat yang nyimpen data penting.

## Kenapa Pusingcuk?

- **Bahasa warung, bukan bahasa robot.** `wadah` = variable (tempat naro data), `balek` = return (balikin hasil), `kepo` = input (nanya ke user). Ngoding tetap serius, bahasanya aja santai.
- **Jalan di HP.** Bisa mulai dari Python di Android lewat Termux atau Pydroid 3. Laptop bukan syarat buat belajar.
- **Error ramah, gak bikin pusing.** Pesan error diarahkan biar lu bisa nemu lokasi masalah dan lanjut ngoding.

Slang itu lapisan gaya, bukan aturan buat semua orang. Kontribusi dalam bahasa Indonesia maupun English welcome.

## Quick start

Di Termux atau terminal yang punya Python 3.11/3.12:

```sh
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
python pusingcuk_new.py examples/modular.pusingcuk
```

Belum punya Termux? Install Python dan Git dulu. Contoh di atas memakai file contoh modul yang memang tersedia di repo. Interpreter Python memakai standard library; gak perlu API key atau paket Python pihak ketiga.

### Pilihan jalanin di Android

**Termux (Python interpreter)**

```sh
pkg update
pkg install python git
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
python pusingcuk_new.py examples/modular.pusingcuk
```

**Pydroid 3**

1. Download atau salin repository ke folder di HP.
2. Buka folder itu di Pydroid 3.
3. Jalankan `pusingcuk_new.py` dengan file sumber sebagai argumen, atau gunakan terminal Pydroid jika tersedia.

**Native runtime di Termux**

Runtime native butuh C compiler dan Make untuk proses build. Setelah selesai dibangun, executable native bisa jalan tanpa Python.

```sh
pkg update
pkg install git clang make
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
bash scripts/install-termux.sh
pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

**Penting soal binary Release:** asset `pusingcuk` pada [GitHub Releases](https://github.com/rllibo833-sudo/pusingcuk/releases) dibangun di Ubuntu x86-64 sebagai executable PyInstaller untuk Linux. Itu **bukan** binary Android/Termux ARM64. Untuk Termux AArch64, build runtime native dari source memakai `bash scripts/install-termux.sh` seperti contoh di atas. Runtime native memiliki subset fitur berbeda dari interpreter Python; lihat [matriks runtime](docs/NATIVE_RUNTIME.md).

## Contoh kode pertama

```pusingcuk
jancuk
hedeh "Hello, world!"
selesai jancuk
```

Run kode yang disimpan sebagai `program.pusingcuk`:

```sh
python pusingcuk_new.py program.pusingcuk
```

## Examples buat dicoba

| Contoh | File / cara | Isinya |
|---|---|---|
| Hello, world | Kode singkat di atas | Salam pembuka; program pertama lu, gak pake drama. |
| Internet | [`examples/internet.pusingcuk`](examples/internet.pusingcuk) | Kepo ke HTTP API; demo ini butuh internet dan bukan bagian dari tes offline CI. |
| Viral bot | [`examples/viral_bot.pusingcuk`](examples/viral_bot.pusingcuk) | Simulasi bikin konten viral; gas ide, bukan jaminan FYP. |
| Module | [`examples/modular.pusingcuk`](examples/modular.pusingcuk) | Pecah kode ke modul biar proyek gak jadi mie kusut. |

## Bahasa dasar / Language basics

| Keyword | English meaning | Guna |
|---|---|---|
| `jancuk` | Start program | Mulai program |
| `lah` | Declare variable | Bikin variabel |
| `hedeh` | Print | Tampilkan output |
| `njir` | Conditional / if | Mulai percabangan |
| `kampret` | Else branch | Jalur alternatif |
| `mumet` | While loop | Ulang selama kondisi benar |
| `tanya` / `kepo` | Read input | Minta input user |
| `fungsi` | Define function | Bikin fungsi |
| `balek` | Return value | Balikin hasil fungsi |
| `angkut` / `impor` | Import module | Muat kode dari modul |
| `coba` / `ketangkep` | Try / catch | Tangani error |
| `selesai jancuk` | End program | Akhiri program |

Contoh percabangan:

```pusingcuk
jancuk
lah name = "Budi"
lah age = 20
hedeh "Hello, " + name
njir age >= 18
    hedeh "Adult"
kampret
    hedeh "Under 18"
selesai njir
selesai jancuk
```

Lihat [spesifikasi bahasa](SPEC.md), [panduan pemula](docs/PEMULA.md), dan [panduan keyword slang](docs/KOSAKATA_GENZ.md) untuk sintaks lengkap.

## Fitur Level 5.1 / 4.1 / 2.1

- **Level 5.1 — HTTP & JSON hardening:** HTTP/HTTPS scheme validation, batas ukuran respons dan payload, timeout, dan penanganan JSON yang lebih aman. Ini bukan klaim bahwa runtime adalah sandbox atau perlindungan SSRF penuh.
- **Level 4.1 — Module system:** impor relatif terhadap file pemanggil untuk nested modules, cache hasil impor, deteksi siklus, batas kedalaman dan ukuran file, serta penolakan path absolut/traversal di luar root proyek.
- **Level 2.1 — Developer experience:** error lebih ramah dengan konteks file/baris/kolom dan pointer kode, exit code CLI yang konsisten, dan bantuan `--help`.

Fitur dan dukungan backend tetap berbeda-beda; cek matriks kompatibilitas sebelum mengandalkan fitur di target selain interpreter Python.

## Development dan tes

Jalankan tes Python secara offline dari root repository:

```sh
python -m unittest discover -s tests -v
```

Tes runtime native (butuh C compiler dan Make):

```sh
make test-native
```

Cek konformansi lintas runtime:

```sh
python tools/conformance.py
```

Interpreter referensi adalah jalur Python modular yang dijalankan dengan `python pusingcuk_new.py program.pusingcuk` (`lexer.py`, `parser.py`, dan `evaluator.py`); semantiknya wajib mengikuti `SPEC.md`. `interpreter.py` adalah implementasi legacy yang terpisah. Runtime native C, compiler Python/JavaScript, dan PVM masih eksperimental, dapat mendukung subset yang lebih kecil, dan bukan sumber otoritatif semantik bahasa. Sintaks dan alias slang dibekukan; penambahan keyword atau alias butuh persetujuan Founder. Lihat [matriks kompatibilitas](docs/COMPATIBILITY.md), [catatan native runtime](docs/NATIVE_RUNTIME.md), dan [target compiler](docs/COMPILER_TARGETS.md).

## Offline-first policy

Interpreter inti, runtime native, compiler, dan tes dirancang berjalan lokal tanpa akses jaringan keluar, API key, layanan hosted, atau paket Python pihak ketiga. Perintah setup pertama seperti `git clone` dan `pkg install` tetap butuh koneksi untuk mengunduh source dan tools. Setelah setup, menjalankan Pusingcuk tidak butuh internet kecuali lu memilih contoh integrasi internet. Untuk setup sepenuhnya offline, pindahkan repository dan pastikan Python (serta C compiler dan Make jika membangun runtime native) sudah terpasang. Tes baru harus memakai resource lokal. Workbench browser opsional hanya bind ke `127.0.0.1` pada perangkat ini.

Jangan tambahkan `os.system`, Python `eval` atau `exec`, dependensi OpenAI SDK, kebutuhan API key, atau panggilan jaringan otomatis ke core runtime. Integrasi eksternal harus tetap opsional dan fitur baru perlu tes offline.

**Security note:** backend JavaScript dan Python PVM memakai parsing ekspresi terbatas. URL jaringan eksternal ditolak; hanya payload lokal `data:text/plain,` yang didukung. Operasi file PVM belum dikurung oleh sandbox tingkat OS, jadi jangan jalankan bytecode dari sumber yang gak dipercaya. Baca [SECURITY.md](SECURITY.md) untuk batasan terbaru.

## Arsitektur

Jalur aktif yang jadi acuan pengembangan:

- `evaluator.py` — interpreter Python modular; gunakan `pusingcuk_new.py` sebagai CLI.
- `compiler/` — jalur compiler utama.
- `native/pusingcuk.c` — runtime interpreter native C.
- `src/c-core/main.c` — **bukan duplikat** runtime native; ini assembler PVM v1 yang terpisah, jadi belum ditandai deprecated.

`interpreter.py` dan `compiler_ir.py` adalah jalur legacy/eksperimental; jangan jadikan keduanya sumber utama fitur baru.

## Dokumentasi dan peta repository

Katalog dokumentasi lengkap ada di [docs/README.md](docs/README.md). Reviewer teknis independen bisa mulai dari [docs/INDEPENDENT_REVIEW.md](docs/INDEPENDENT_REVIEW.md).

- [Visi proyek dan prinsip komunitas](docs/VISION.md)
- [Struktur repository dan status fitur](docs/REPO_STRUCTURE.md)
- [Panduan pemula](docs/PEMULA.md)
- [Kamus teknis bahasa Inggris](docs/DICTIONARY.md)
- [Kamus bahasa Indonesia](docs/KAMUS_PUSINGCUK.md)
- [Desain slang dan alias](docs/KOSAKATA_GENZ.md)
- [Registry kosakata dan contoh](library/README.md)
- [Spesifikasi bahasa](SPEC.md)
- [Kompatibilitas runtime](docs/COMPATIBILITY.md)
- [Native runtime](docs/NATIVE_RUNTIME.md)
- [Target compiler](docs/COMPILER_TARGETS.md)
- [Python importer dan subset standard library](docs/IMPORT_PYTHON.md)
- [Roadmap native runtime dan ekosistem](docs/NATIVE_SECURE_ECOSYSTEM_ROADMAP.md)
- [Panduan kontribusi](CONTRIBUTING.md)
- [Kebijakan keamanan](SECURITY.md)
- [Kode etik komunitas](CODE_OF_CONDUCT.md)

## Cara Kontribusi 10 Menit

Baru mulai? Pilih satu task kecil—gak harus langsung jadi ahli. Bahasa Indonesia dan English welcome; pemula, Gen Z/Gen Alpha, dan kontributor internasional boleh ikut.

- [Kalkulator pemula: contoh `examples/kalkulator.pusingcuk` dengan `tanya` + `jika` (#78)](https://github.com/rllibo833-sudo/pusingcuk/issues/78)
- [Bikin pesan error parser lebih ramah Gen Z / Gen Alpha di `parser.py` (#79)](https://github.com/rllibo833-sudo/pusingcuk/issues/79)
- [Desain logo sederhana untuk Pusingcuk (#80)](https://github.com/rllibo833-sudo/pusingcuk/issues/80)

Pilih satu, baca acceptance criteria, lalu tinggalkan komentar kalau mau mengerjakannya. Lihat juga [Good First Issues](https://github.com/rllibo833-sudo/pusingcuk/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) dan [CONTRIBUTING.md](CONTRIBUTING.md).

## Kontribusi dan kontak proyek

Pusingcuk terbuka buat pemula maupun developer berpengalaman. Lu gak harus langsung jago coding untuk bantu: dokumentasi, terjemahan, contoh, bug report yang bisa direproduksi, dan masukan desain juga berguna. Baca [CONTRIBUTING.md](CONTRIBUTING.md), jelaskan masalahnya, sertakan contoh kecil kalau bisa, dan tambahkan tes untuk perubahan perilaku. Kontribusi harus mempertahankan operasi offline dan menjelaskan dukungan Android secara jujur.

Kontak proyek dan masukan review: **pusingcukdevprog@gmail.com**. Jangan kirim password, access token, data pribadi, atau detail celah keamanan yang belum ditangani lewat email biasa; ikuti [SECURITY.md](SECURITY.md) untuk laporan keamanan.

## Ekstensibilitas komunitas

Pusingcuk dirancang agar bisa dikembangkan oleh komunitas di luar Founder, termasuk Ecoslang.org serta komunitas bahasa, pendidikan, dan open-source lain. Spesifikasi bahasa bersama, conformance fixtures, dan intermediate representation menjadi fondasi untuk runtime kompatibel, library, target compiler, dan integrasi masa depan. Database adapters, server/API tooling, frontend bindings, WebAssembly, stable FFI/ABI, kosakata regional yang bisa dikonfigurasi, dan blockchain masih merupakan target pengembangan—bukan klaim bahwa semuanya sudah siap produksi. Lihat [kamus Inggris](docs/DICTIONARY.md), [kamus Indonesia](docs/KAMUS_PUSINGCUK.md), dan [roadmap ekosistem](docs/NATIVE_SECURE_ECOSYSTEM_ROADMAP.md).

## Lisensi

Pusingcuk dirilis di bawah MIT License. Baca [LICENSE](LICENSE).

## Builtin contract dan roadmap offline-first

Nama builtin, jumlah argumen, mapping import Python, helper backend, dan status kompatibilitas didefinisikan di [`library/builtin_contract.json`](library/builtin_contract.json). Ini membantu menjaga registry referensi, importer, compiler backend, dan tes tetap konsisten. Lihat [`library/README.md`](library/README.md) untuk cara memperluasnya.
