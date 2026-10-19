# Identitas PusingCuk — Tiga Komponen, Satu Ekosistem

Dokumen ini adalah referensi resmi untuk membedakan tiga komponen utama ekosistem PusingCuk.

## 1. Bahasa .cuk (PusingCuk Language)

Bahasa pemrograman eksperimental dengan ekstensi `.cuk`, keyword berbahasa Indonesia, spesifikasi tertulis, interpreter referensi, runtime native C, dan backend JavaScript.

**Tujuan:** bahasa yang bisa dipelajari dari HP, berjalan lokal, dan memiliki jalur menuju executable native.

Prinsip:
- Spesifikasi adalah sumber kebenaran; implementasi harus mengikutinya.
- Kosakata dibekukan. Alias baru memerlukan keputusan Founder.
- Tidak ada klaim siap produksi tanpa bukti fixture konformansi.

Lokasi: `SPEC.md`, `lexer.py`, `parser.py`, `evaluator.py`, `ast_nodes.py`, `pusingcuk_new.py`, `library/`, `native/`, `compiler/`, `tests/`, `examples/`, `site/`.

## 2. PusingCuk AI

Lapisan asisten yang di-ground dengan spesifikasi, kosakata, kontrak built-in, dan fixture .cuk. Ini bukan model fondasi yang dilatih dari nol dan bukan sumber kebenaran bahasa; SPEC tetap berwenang.

Tujuannya membantu menjawab pertanyaan tentang .cuk, menghasilkan contoh valid, dan menjelaskan diagnostic dengan konteks proyek. Provider AI dapat diganti; klaim kemampuan harus sesuai implementasi yang benar-benar tersedia.

Lokasi terkait: `library/assistant.py`, `library/ai_tools.py`, `library/knowledge_grounding.py`, `library/knowledge_index.json`, `library/local_memory.py`, provider AI yang tersedia, dan `examples/ai/`.

## 3. Cuk Reality Engine

Perangkat pembuktian kompatibilitas lintas target: menjalankan fixture, membandingkan output, mencatat perbedaan, dan menghasilkan laporan yang bisa direproduksi. Laporan harus berasal dari eksekusi nyata; file statis atau badge saja bukan bukti bahwa generator berfungsi.

Lokasi terkait: `tests/conformance/`, `tools/`, `reports/`, `docs/COMPATIBILITY.md`, serta workflow CI terkait.

## Hubungan ketiganya

Bahasa .cuk adalah fondasi dan menentukan semantik. PusingCuk AI membantu manusia menggunakan dan mengembangkan bahasa dengan konteks yang benar. Cuk Reality Engine memeriksa apakah klaim kompatibilitas didukung bukti.

Tidak satu pun dari AI atau Reality Engine boleh mengubah spesifikasi bahasa secara diam-diam. Status target harus dibatasi oleh hasil konformansi yang benar-benar tersedia.
