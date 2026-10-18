# Peta Dokumentasi PusingCuk

Dokumen ini adalah **satu pintu masuk** ke dokumentasi. Pilih berdasarkan pekerjaan yang ingin dilakukan; tidak perlu membaca semuanya.

## 1. Mulai menggunakan .cuk

- [Panduan pemula](PEMULA.md) — sintaks dan contoh dasar.
- [Spesifikasi bahasa](../SPEC.md) — aturan sintaks/fitur yang dinyatakan didukung.
- [Kontrak semantik](SEMANTIC_CONTRACT.md) — perilaku yang harus konsisten.
- [Gaya bahasa](GAYA_BAHASA.md), [kamus](KAMUS_PUSINGCUK.md), dan [kosakata Gen Z](KOSAKATA_GENZ.md) — istilah, keyword, serta alias.
- [Contoh program](examples/) — contoh yang dapat dipakai sebagai titik awal.

## 2. Compiler, runtime, dan library

- [Kompatibilitas](COMPATIBILITY.md) — batas fitur antar-target.
- [Target compiler](COMPILER_TARGETS.md) — C, JavaScript, Python, Android, dan VM.
- [Bytecode VM](BYTECODE_VM.md) dan [spesifikasi PVM](PVM_SPEC.md) — format serta batas VM eksperimental.
- [Kontrak semantik](SEMANTIC_CONTRACT.md), [IR v1](IR_V1.md), dan [kontrak konformansi](CONFORMANCE_FIXTURES.md) — untuk perubahan compiler/runtime.
- [Sistem modul](MODULE_SYSTEM.md) dan [impor Python](IMPORT_PYTHON.md) — integrasi impor yang memang tersedia.
- [Peta struktur repo](REPO_STRUCTURE.md) — lokasi kode berdasarkan fungsi.
- [Panduan library](../library/README.md) — built-in, registri kosakata, adapter, dan contoh.

## 3. PusingCuk AI

- [Kesiapan engine AI](AI_ENGINE_READINESS.md) — batas kemampuan yang telah dicatat.
- [Grounding pengetahuan](AI_KNOWLEDGE_GROUNDING.md) — sumber dan konteks jawaban.
- [Jembatan AI ke evolusi bahasa](AI_LANGUAGE_EVOLUTION_BRIDGE.md) — siklus usulan → diagnostik → fixture.
- [Layanan AI lokal](AI_LOCAL_SERVICE.md) — menjalankan layanan lokal yang didukung.

AI adalah alat bantu, bukan otoritas semantik. Kode yang dihasilkan harus diperiksa compiler dan runtime. Jangan menganggap konfigurasi prototipe sebagai layanan publik yang siap produksi.

## 4. Frontend, backend, dan integrasi

- [Web workbench](WEB_WORKBENCH.md) — UI editor berbasis web.
- [Studio localhost](STUDIO_LOCALHOST.md) — layanan studio lokal.
- [Integrasi CukAccount](CUKACCOUNT_INTEGRATION.md) — kontrak integrasi aplikasi contoh.
- [Distribusi Android](ANDROID_DISTRIBUTION.md) dan [Android Studio](ANDROID_STUDIO.md) — prototipe/build Android.
- [Compiler C](C_BACKEND.md), [backend JavaScript](JS_BACKEND.md), dan [interoperabilitas compiler](COMPILER_INTEROP.md).

UI, API, backend, compiler, dan runtime adalah lapisan berbeda. Dokumen integrasi tidak membuktikan bahwa deployment atau build target telah lulus.

## 5. Pengujian dan keamanan

- [Fixture konformansi](CONFORMANCE_FIXTURES.md) — cara mengunci perilaku lintas-runtime.
- [Panduan tooling](TOOLING.md) — alat pengembangan dan validasi.
- [Keamanan runner](CORE_SANDBOX_RUNNER.md) dan [review keamanan](SECURITY_REVIEW_2026-10-13.md) — baca sebagai catatan terbatas pada cakupan/tanggalnya.
- [Uji native di Termux](NATIVE_TERMUX.md) — termasuk hal yang perlu diverifikasi pada perangkat fisik.

**Peringatan:** PusingCuk belum menyediakan sandbox OS yang menjamin kode tidak tepercaya aman. Jangan jalankan program atau bytecode yang tidak dipercaya.

## 6. Status dan keputusan proyek

- [Status dan prioritas aktif](PROJECT_STATUS_AND_ROADMAP.md) — ringkasan pendek, bukan arsip setiap langkah.
- [Vision](VISION.md) — tujuan dan prinsip jangka panjang.
- [Changelog](../CHANGELOG.md) — perubahan yang telah dicatat.
- [Tinjauan independen](INDEPENDENT_REVIEW.md) — temuan/rekomendasi pada cakupan tinjauan tersebut.

## Cara menjaga dokumentasi tetap ringan

- Ubah dokumen yang sudah ada sebelum membuat dokumen baru.
- Simpan **satu sumber kanonis** untuk setiap kontrak; dokumen lain harus merujuk, bukan menyalin seluruh isi.
- Catatan audit bertanggal adalah snapshot historis, bukan status HEAD terkini.
- Hapus atau arsipkan dokumen hanya setelah memeriksa tautan masuk, workflow, dan apakah masih menjadi bukti historis.
