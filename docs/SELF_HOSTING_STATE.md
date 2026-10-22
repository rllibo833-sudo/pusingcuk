# Self-hosting state — engineering handoff

Dokumen ini adalah satu-satunya handoff aktif menuju compiler .cuk mandiri. SPEC.md tetap menjadi kontrak bahasa; compiler/ir.py menetapkan envelope dan validasi IR v1.

## Arsitektur yang benar-benar ada

- examples/self_hosting/compiler.cuk: lexer/parser .cuk, AST sementara, dan serializer AST → IR v1. Grammar mencakup deklarasi, assignment variabel/indeks, output, ekspresi, pemanggilan fungsi, fungsi/return, kondisi, loop, list, dictionary, index, dan akses member sederhana.
- compiler/self_hosted_frontend.py: menjalankan sumber compiler .cuk melalui `Evaluator` pada `evaluator.py`, mengambil JSON IR, lalu memvalidasinya dengan validator Python. Ini menghindari CLI/launcher tambahan, bukan menghilangkan host Python. Jalur ini tidak boleh fallback ke parser Python referensi.
- compiler/ir.py: IR v1 kanonis beserta validator schema, path, source map dan feature.
- compiler/bytecode.py + compiler/vm.py: backend bytecode dan VM Python untuk IR v1.
- compiler/bootstrap.py: membandingkan dua jalur eksekusi frontend untuk source yang sama. Stage 1 berjalan melalui Python Evaluator; stage 2 menjalankan frontend .cuk yang dikompilasi menjadi bytecode PusingCuk dan dieksekusi oleh VM. IR, bytecode, dan output harus identik.
- Batas stage 2 saat ini: driver frontend masih dibentuk memakai parser referensi Python dan dikompilasi oleh compiler bytecode Python. Runtime frontend sudah diuji di VM, tetapi proses membangun driver belum mandiri.

## Gate pembuktian

1. tests/test_compiled_frontend_vm.py membandingkan IR frontend .cuk dengan parser referensi ketika frontend mem-parsing compiler.cuk itu sendiri; tes yang sama memastikan hasilnya dapat masuk ke bytecode VM.
2. compiler.bootstrap membuktikan parity antara frontend .cuk yang dijalankan via Evaluator dan frontend yang dijalankan dari bytecode VM, untuk subset yang didukung.
3. Setiap IR harus lolos compiler.ir.validate; source map, fitur, bytecode, dan output dibandingkan dari kedua jalur.
4. Tahap berikutnya adalah membuat driver .cuk dapat menghasilkan compiler tahap berikutnya tanpa parser referensi atau compiler bytecode Python. Baru sesudah artefak hasil stage 1 menjalankan stage 2 dan lulus konformansi, status boleh disebut self-hosted penuh.
5. Jangan mengubah kegagalan menjadi fallback. Gunakan manifest dan suite yang ada; jangan membuat branch, daemon, status report per-fitur, atau suite duplikat.

## Kontrak compiler tahap kedua

IR v1 tetap menjadi antarmuka antar-tahap. Stage 1 menerima satu dokumen JSON IR dari stdin, menolak JSON tidak valid atau envelope yang bukan pusingcuk-ir versi 1, lalu mengeluarkan dokumen JSON yang sama secara semantik melalui json_teks. Ini adalah tahap transport/round-trip IR, **bukan** klaim bahwa seluruh schema node sudah divalidasi oleh .cuk; validasi schema penuh masih dilakukan oleh gate kanonis sampai validator mandiri tersedia.

- Sumber prototipe: examples/self_hosting/ir_stage.cuk.
- Input: satu baris JSON berisi envelope IR v1.
- Output sukses: satu baris JSON IR; metadata format, ir_version, dan root program.kind == Program wajib sesuai kontrak.
- Output gagal: IR_STAGE_INVALID_JSON atau IR_STAGE_INVALID_ENVELOPE; jangan fallback ke parser atau compiler lain.
- Stabilitas byte-for-byte belum diasumsikan. Gate harus membandingkan JSON hasil parse secara semantik terlebih dahulu; byte-identical baru diwajibkan setelah serializer .cuk memiliki urutan kunci kanonis.

## Urutan kerja

1. **Phase 1 — IR round-trip:** jalankan prototipe IR stage dengan fixture IR kanonis yang sudah ada; validasi envelope, round-trip semantik, dan penolakan input rusak.
2. **Phase 2 — IR → bytecode:** pindahkan aturan compiler/bytecode.py ke .cuk; keluaran harus lolos compiler.bytecode.validate_bytecode dan dapat dijalankan oleh VM yang sama.
3. **Phase 3 — loop dua tahap:** Compiler₁ membangun Compiler₂ dari sumber compiler yang sama; bandingkan IR/bytecode kanonis dan jalankan konformansi menggunakan artefak Compiler₂.
4. **Phase 4 — gate CI:** tambahkan bootstrap-loop-verify setelah phase 1–3 dapat dieksekusi end-to-end. Jangan membuat gate hijau yang hanya memanggil compiler Python dua kali.
5. Nyatakan self-hosting penuh hanya setelah tahap tersebut lulus di CI dari commit yang sama.

## Klaim yang belum boleh dibuat

IR v1, bytecode VM, backend multi-target, parser source .cuk, dan bukti build berulang bukan bukti terpisah bahwa compiler sudah mandiri penuh. Status tetap belum self-hosted penuh sampai bootstrap dua tahap mandiri benar-benar terverifikasi.
