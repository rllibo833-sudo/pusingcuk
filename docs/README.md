# Peta Dokumentasi PusingCuk

Dokumentasi ini disusun berdasarkan kebutuhan pembaca, bukan berdasarkan urutan file dibuat. Catatan bertanggal dan dokumen eksperimen tetap berguna sebagai jejak, tetapi bukan otomatis status fitur terkini.

## 1. Baru mengenal PusingCuk?

1. [README utama](../README.md) — gambaran singkat dan cara menjalankan.
2. [Panduan pemula](PEMULA.md) — belajar sintaks dasar.
3. [Kamus Bahasa Warung](KAMUS_PUSINGCUK.md) — kata kunci, fungsi, istilah teknis, dan peta folder.
4. [Contoh program](../examples/README.md) — contoh yang tersedia.

English readers: start with [README_EN.md](../README_EN.md) and [the technical dictionary](DICTIONARY.md).

## 2. Aturan bahasa dan pustaka

- [Spesifikasi bahasa](../SPEC.md) — sintaks dan perilaku yang tampak bagi pengguna.
- [Kontrak semantik](SEMANTIC_CONTRACT.md) — perilaku yang harus bisa diuji.
- [Built-in](language/BUILTINS.md) dan [kontrak built-in mesin](../library/builtin_contract.json).
- [Kamus alias Gen Z/Gen Alpha](KOSAKATA_GENZ.md) dan [gaya bahasa](GAYA_BAHASA.md).
- [Struktur repositori](REPO_STRUCTURE.md).

## 3. Compiler, runtime, dan kompatibilitas

- [Matriks kompatibilitas](COMPATIBILITY.md) — batas dukungan per implementasi.
- [Fixture konformansi](CONFORMANCE_FIXTURES.md) — bukti perilaku yang diuji.
- [Target compiler](COMPILER_TARGETS.md), [IR v1](IR_V1.md), [backend C](C_BACKEND.md), [backend JavaScript](JS_BACKEND.md), dan [VM bytecode](BYTECODE_VM.md).
- [Runtime native](NATIVE_RUNTIME.md) dan [panduan Termux](NATIVE_TERMUX.md).
- [Tooling](TOOLING.md) dan [dukungan editor](EDITOR_SUPPORT.md).

## 4. PusingCuk AI dan integrasi

- [Kesiapan engine AI](AI_ENGINE_READINESS.md).
- [Grounding pengetahuan AI](AI_KNOWLEDGE_GROUNDING.md).
- [Jembatan evolusi bahasa](AI_LANGUAGE_EVOLUTION_BRIDGE.md).
- [Layanan AI lokal](AI_LOCAL_SERVICE.md).
- [Ikhtisar proyek](PROJECT_OVERVIEW.md) dan [Project overview (English)](PROJECT_OVERVIEW_EN.md).

Keberadaan modul AI atau adapter tidak membuktikan model dilatih sendiri, kualitas umum, atau layanan SaaS siap produksi. Klaim harus ditautkan ke pengujian dan konfigurasi yang benar-benar tersedia.

## 5. Kontribusi, keamanan, dan status

- [Panduan kontribusi](../CONTRIBUTING.md).
- [Kebijakan keamanan](../SECURITY.md).
- [Code of Conduct](../CODE_OF_CONDUCT.md).
- [Changelog](../CHANGELOG.md).

Dokumen audit bertanggal, roadmap, arsip, dan catatan migrasi dibaca sebagai konteks historis kecuali statusnya diverifikasi ulang. Untuk klaim kompatibilitas, prioritaskan spesifikasi, kontrak, implementasi, fixture, dan hasil CI dari commit yang sama.

## Catatan keamanan

Interpreter, compiler, dan VM bukan sandbox sistem operasi. Jangan menjalankan kode tak tepercaya di lingkungan sensitif. CI hijau hanya membuktikan job yang benar-benar dijalankan.
