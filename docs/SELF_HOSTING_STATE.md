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

## Urutan kerja

1. Luluskan parser frontend untuk mem-parsing examples/self_hosting/compiler.cuk sendiri dan menyamai AST IR kanonis tanpa fallback.
2. Pastikan control-flow/collection mencapai bytecode VM dan jalur CLI tetap lulus.
3. Bangun bootstrap sungguhan: stage 1 harus menghasilkan artefak compiler yang bisa dijalankan tanpa interpreter/frontend Python untuk parsing source; stage 2 menggunakan artefak itu untuk membangun ulang compiler, lalu membandingkan artefak dan menjalankan konformansi.
4. Nyatakan self-hosting penuh hanya setelah tahap tersebut lulus di CI dari commit yang sama.

## Klaim yang belum boleh dibuat

IR v1, bytecode VM, backend multi-target, parser source .cuk, dan bukti build berulang bukan bukti terpisah bahwa compiler sudah mandiri penuh. Status tetap belum self-hosted penuh sampai bootstrap dua tahap mandiri benar-benar terverifikasi.
