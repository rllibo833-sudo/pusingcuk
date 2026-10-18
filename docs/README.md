# Peta Dokumentasi PusingCuk

Ini indeks kanonis. Pilih bagian sesuai pekerjaan; **jangan membaca semua dokumen sekaligus**. Nama dokumen historis dipertahankan untuk jejak keputusan, bukan berarti seluruh isinya masih berlaku untuk HEAD.

## A. Pengguna .cuk dan program contoh

- [Panduan utama Indonesia](../README.md) dan [English README](../README_EN.md) — pengantar dan cara menjalankan.
- [Changelog](../CHANGELOG.md) — perubahan yang dicatat.
- [Panduan pemula](PEMULA.md) — belajar sintaks.
- [Spesifikasi bahasa](../SPEC.md) — kontrak sintaks dan perilaku.
- [Vision](VISION.md) — tujuan dan prinsip proyek.
- [Cuk Reality Engine](REALITY_ENGINE.md) — tujuan dan status contoh program berbasis aturan pada branch `cuk-reality-engine`; fokus pada pembuktian kemampuan bahasa `.cuk`, bukan sistem air produksi.
- [Gaya bahasa](GAYA_BAHASA.md), [kamus](KAMUS_PUSINGCUK.md), [kosakata Gen Z](KOSAKATA_GENZ.md), dan [referensi istilah](DICTIONARY.md).
- [Referensi bahasa](language/README.md) dan [built-in](language/BUILTINS.md).
- [Contoh program](../examples/README.md), [kompatibilitas contoh](../examples/compat/README.md), dan [contoh bahasa warung](../examples/warung_bahasa/README.md).
- [Contoh CukAccount](examples/CUKACCOUNT_TARGET.md) dan [aplikasi akuntansi untuk pelajar](ACCOUNTING_STUDENT_APP.md).
- [Masterplan dan model operasi Kawasan Masjid](knowledge/KAWASAN_MASJID_MASTERPLAN_AND_OPERATING_MODEL.md) — dokumen pengetahuan/integrasi, bukan spesifikasi bahasa.

## B. Bahasa, library, compiler, dan runtime

- [Peta struktur repo](REPO_STRUCTURE.md) — lokasi berdasarkan tanggung jawab.
- [Panduan library](../library/README.md) — registri, built-in, dan contoh .cuk.
- [Kompatibilitas target](COMPATIBILITY.md) dan [target compiler](COMPILER_TARGETS.md).
- [Kontrak semantik](SEMANTIC_CONTRACT.md), [IR v1](IR_V1.md), [konformansi fixture](CONFORMANCE_FIXTURES.md), [sistem modul](MODULE_SYSTEM.md), [impor Python](IMPORT_PYTHON.md), dan [tipe/stdlib compiler](compiler-type-system-and-stdlib.md).
- [Backend C](C_BACKEND.md), [backend JavaScript](JS_BACKEND.md), [interop compiler](COMPILER_INTEROP.md), [bytecode VM](BYTECODE_VM.md), dan [spesifikasi PVM](PVM_SPEC.md).
- [Runtime native C](NATIVE_RUNTIME.md) dan [uji native Termux](NATIVE_TERMUX.md).
- [Tooling](TOOLING.md), [dukungan editor](EDITOR_SUPPORT.md), dan [panduan pengembangan](development/README.md).

## C. PusingCuk AI dan grounding

- [Kesiapan engine AI](AI_ENGINE_READINESS.md) — kemampuan dan batas yang perlu diverifikasi.
- [Ledger migrasi engine](AI_ENGINE_MIGRATION_LEDGER.md) — catatan transisi historis.
- [Grounding pengetahuan](AI_KNOWLEDGE_GROUNDING.md) dan [jembatan AI → evolusi bahasa](AI_LANGUAGE_EVOLUTION_BRIDGE.md).
- [Layanan AI lokal](AI_LOCAL_SERVICE.md), [kontrak otoritas dan bukti](ai/DECISION_AUTHORITY_AND_EVIDENCE.md), dan [keamanan model lokal](ai/LOCAL_MODEL_AND_RULE_SAFETY.md).
- [Kontrak tool CORE](integrations/CORE_TOOL_CONTRACT.md) dan [integrasi CukAccount](integrations/CUKACCOUNT.md) — kontrak integrasi.
- [Peta proyek Supabase](integrations/SUPABASE_PROJECTS.md) — catatan pemetaan proyek, bukan bukti koneksi runtime aktif.

## D. Frontend, backend, aplikasi, dan integrasi

- **Web/frontend:** [web workbench](WEB_WORKBENCH.md), [studio localhost](STUDIO_LOCALHOST.md), dan [README site](../site/README.md).
- **AI SaaS/backend:** [aplikasi PusingCuk AI SaaS](../apps/pusingcuk-ai-saas/README.md), [peta proyek Supabase](integrations/SUPABASE_PROJECTS.md), dan [adapter offline](OFFLINE_ADAPTERS.md).
- **CukAccount:** [README aplikasi](../apps/accounting/README.md), [panduan .cuk](../apps/accounting/README_CUK.md), [kontrak platform bridge](../apps/accounting/PLATFORM_BRIDGE_CONTRACT.md), dan [integrasi](CUKACCOUNT_INTEGRATION.md).
- **Android/platform:** [distribusi Android](ANDROID_DISTRIBUTION.md), [Android Studio](ANDROID_STUDIO.md), [ruang kerja mobile](SANDBOXOS_MOBILE_WORKSPACE.md), dan [dashboard Termux](TERMUX_DASHBOARD.md).
- [Peta migrasi FounderOS/CORE](migration/FOUNDER_OS_CORE_RETIREMENT_MANIFEST.md) — catatan migrasi historis, bukan dependensi runtime otomatis.

## E. Keamanan, kontribusi, dan bukti

- [Kebijakan keamanan](../SECURITY.md), [Code of Conduct](../CODE_OF_CONDUCT.md), [panduan kontribusi](../CONTRIBUTING.md), dan [review keamanan](SECURITY_REVIEW_2026-10-13.md).
- [Runner/sandbox CORE](CORE_SANDBOX_RUNNER.md) dan [peta keamanan ekosistem native](NATIVE_SECURE_ECOSYSTEM_ROADMAP.md).
- [Catatan tinjauan independen](INDEPENDENT_REVIEW.md).
- [Pustaka keamanan](security/README.md).

## F. Catatan audit/roadmap historis — jangan dianggap status HEAD

- [Audit native 11 Okt 2026](NATIVE_AUDIT_2026-10-11.md).
- [Audit parity native](NATIVE_PARITY_AUDIT.md).
- [Roadmap compiler lintas-repo](THREE_REPO_COMPILER_ROADMAP.md).
- [Status dan prioritas aktif](PROJECT_STATUS_AND_ROADMAP.md) adalah ringkasan status; untuk klaim baru, periksa commit dan Actions terkait.
- [README arsip legacy](../archive/legacy/README.md).
- [Panduan Termux umum](termux/README.md) — setup perangkat, bukan jaminan uji fisik lulus.
- [README pengembangan](development/README.md) dan [README dokumentasi](README.md) adalah titik masuk; hindari membuat indeks tambahan.

## Aturan merawat Markdown

1. **Satu fungsi, satu dokumen kanonis.** README untuk orientasi, SPEC untuk bahasa, semantic contract untuk perilaku, builtin contract untuk metadata mesin.
2. Dokumen frontend tidak mendefinisikan aturan bisnis; dokumen backend tidak mendefinisikan tampilan; library menjelaskan API/kontrak dan contoh yang memang ada.
3. Dokumen audit bertanggal adalah snapshot. Jangan menyalin status lamanya ke README atau menyebutnya kondisi terbaru.
4. Sebelum menghapus/memindahkan dokumen, cari tautan masuk dan rujukan workflow. Jika isi tumpang tindih, ringkas dokumen turunan dan tautkan ke sumber kanonis.
5. Perubahan bahasa harus memperbarui spesifikasi, implementasi target yang didukung, tes/fixture, dan matriks kompatibilitas bersama-sama.
