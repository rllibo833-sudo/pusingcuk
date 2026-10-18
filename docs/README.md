# Dokumentasi PusingCuk

Peta ringkas untuk bahasa pemrograman .cuk. Dokumentasi berstatus historis atau eksperimen tidak berarti fitur terkait merupakan bagian dari jalur utama.

## Mulai menggunakan .cuk

- [README utama](../README.md) — jalankan program pertama.
- [Panduan pemula](PEMULA.md) — sintaks dasar.
- [Spesifikasi bahasa](../SPEC.md) — kontrak sintaks.
- [Kontrak semantik](SEMANTIC_CONTRACT.md) — perilaku bahasa.
- [Contoh program](../examples/README.md) — contoh yang tersedia.
- [Kamus PusingCuk](KAMUS_PUSINGCUK.md) dan [gaya bahasa](GAYA_BAHASA.md).

## Implementasi bahasa

- [Struktur repository](REPO_STRUCTURE.md).
- [Kontrak built-in](../library/builtin_contract.json) dan [panduan library](../library/README.md).
- [Matriks kompatibilitas](COMPATIBILITY.md) dan [fixture konformansi](CONFORMANCE_FIXTURES.md).
- [Backend C](C_BACKEND.md), [backend JavaScript](JS_BACKEND.md), [VM bytecode](BYTECODE_VM.md), dan [runtime native](NATIVE_RUNTIME.md).
- [Tooling](TOOLING.md) dan [dukungan editor](EDITOR_SUPPORT.md).

## Kontribusi dan keamanan

- [Panduan kontribusi](../CONTRIBUTING.md).
- [Kebijakan keamanan](../SECURITY.md).
- [Code of Conduct](../CODE_OF_CONDUCT.md).

## Membaca catatan lama

Dokumen audit bertanggal dan roadmap adalah rekam jejak, bukan bukti bahwa fitur masih aktif atau sudah siap dipakai. Verifikasi implementasi dan fixture yang ada sebelum mengandalkan klaim kompatibilitas. Interpreter dan backend bukan sandbox sistem operasi; jangan jalankan kode tak tepercaya pada lingkungan sensitif.
