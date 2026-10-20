# Status dan roadmap kanonis PusingCuk

Dokumen ini adalah **satu-satunya roadmap aktif**. README menjelaskan proyek; SPEC mendefinisikan bahasa; kontrak mesin dan manifest mendefinisikan dukungan; dokumen audit bertanggal adalah catatan historis, bukan status terbaru.

**Status rilis: experimental / development.** Jangan mengubah README atau deskripsi repositori menjadi stable sebelum acceptance criteria rilis pada Fase 3 lulus di commit yang sama.

## Sumber kebenaran

| Pertanyaan | Sumber kanonis |
|---|---|
| Apa semantik dan sintaks bahasa? | [SPEC.md](../SPEC.md), [kontrak semantik](SEMANTIC_CONTRACT.md) |
| Built-in apa yang tersedia dan tipe/arity-nya? | [Kontrak built-in](../library/builtin_contract.json) |
| Fixture apa yang wajib diuji? | [Manifest konformansi](../tests/conformance/manifest.json) |
| Hasil fixture dan status target? | [Matriks kompatibilitas](COMPATIBILITY.md), baseline di `tests/conformance/baseline_summary.json`, serta artefak CI untuk commit yang sama |
| Bagaimana cara kerja compiler dan AI? | [Compiler targets](COMPILER_TARGETS.md), [AI readiness](AI_ENGINE_READINESS.md) |
| Roadmap apa yang aktif? | Dokumen ini saja |

Jangan menyalin tabel jumlah fixture ke banyak dokumen. Ringkasan yang dibuat generator harus tetap berada di marker generatornya; angka manual yang bertentangan tidak boleh ditambahkan.

## Status yang sudah dibuktikan

Run core terbaru yang terlihat saat dokumen ini diperbarui adalah [PusingCuk core #39427633974](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39427633974), sukses pada commit `1ec4fc39babf58bdf737d44a8df5ef4dc7c91f31`. Run matriks [#39427208732](https://github.com/rllibo833-sudo/pusingcuk/actions/runs/39427208732) sukses pada commit lebih lama `9a87a7d32dd147ec36056bee4088002392d029a6`; hasilnya tidak boleh dianggap sebagai bukti bahwa perubahan sesudah commit itu ikut diuji oleh matriks tersebut.

Snapshot matriks tersebut menunjukkan reference, JS, Python transpiler, dan VM 77/77; native C 74/77 dengan tiga fixture unsupported; HTML 0/77. Ini baseline historis yang berguna, bukan bukti bahwa gap native C telah ditutup pada HEAD sekarang. Periksa [COMPATIBILITY.md](COMPATIBILITY.md) dan artefak workflow sebelum menyatakan status yang lebih baru.

## Fase menuju v1.0

### Fase 1 — Kontrak inti dan runtime native
- [ ] Implementasikan JSON parse/serialize, HTML escaping, dan CSV quoting pada native C.
- [ ] Tambahkan tes unit untuk nilai valid/invalid, nested list/dictionary, escaping, arity, dan batas ukuran.
- [ ] Ubah tiga fixture native dari `unsupported` ke `required` hanya setelah native/reference cocok.
- [ ] Jalankan matrix dan differential test pada commit yang sama; hasil wajib tanpa mismatch, incomplete, atau unsupported pada fixture rilis yang diwajibkan.
- [ ] Matikan auto-push evolusi dari Termux; perubahan bahasa harus melalui diff yang ditinjau dan tes wajib.

### Fase 2 — Browser dan perluasan target
- [ ] Playground GitHub Pages menjalankan subset .cuk yang didukung melalui backend JS/browser yang nyata, bukan sekadar menampilkan kode atau mengandalkan terminal Python eksternal tanpa diagnostik.
- [ ] Browser tests membuktikan output, error, dan contoh yang ditampilkan; kegagalan runtime tidak boleh tampil sebagai traceback mentah.
- [ ] Tentukan kontrak lintas target dari fixture bersama sebelum menambah backend C++, Kotlin/JVM, atau target lain.
- [ ] Target yang belum menjalankan fixture dilaporkan `unsupported/not yet verified`, bukan hijau secara implisit.

### Fase 3 — Release v1.0
- [ ] Bekukan spesifikasi dan kontrak semantik yang didukung.
- [ ] Manifest konformansi menjadi acceptance suite wajib dan dapat direproduksi.
- [ ] Setiap target yang diklaim stabil lulus suite wajib pada commit rilis yang sama; pengecualian didokumentasikan per fitur.
- [ ] Dokumentasi pengguna, quickstart, built-ins, compiler targets, website, package metadata, dan release notes konsisten.
- [ ] CI wajib hijau untuk semua workflow rilis yang relevan; tidak ada run wajib yang masih berjalan atau dilewati.

## Aturan perubahan

1. Satu perubahan bahasa harus menyentuh implementasi, kontrak, fixture, dokumentasi relevan, dan generator yang terkait dalam satu perubahan terulas.
2. Jangan ubah baseline agar CI hijau; baseline hanya diperbarui dari hasil runner yang sukses dan ditinjau.
3. Jangan pakai penggantian teks global, `|| true` untuk tes wajib, atau loop otomatis yang commit/push ke `main`.
4. Jangan menambah dokumen status duplikat. Audit bertanggal tetap sebagai sejarah; update dokumen ini dan sumber kanonis.
5. CI hijau membuktikan job yang benar-benar berjalan pada commit tersebut saja—bukan semua fitur atau target.
