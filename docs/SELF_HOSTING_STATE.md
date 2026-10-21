# Self-hosting state — engineering handoff

Dokumen ini adalah satu-satunya handoff aktif menuju compiler .cuk mandiri. SPEC.md tetap menjadi kontrak bahasa; compiler/ir.py menetapkan envelope dan validasi IR v1.

## Arsitektur yang benar-benar ada

- examples/self_hosting/compiler.cuk: lexer/parser .cuk, AST sementara, dan serializer AST → IR v1. Grammar mencakup deklarasi, assignment variabel/indeks, output, ekspresi, pemanggilan fungsi, fungsi/return, kondisi, loop, list, dictionary, index, dan akses member sederhana.
- compiler/self_hosted_frontend.py: menjalankan frontend .cuk melalui host pusingcuk_new.py, mengambil JSON IR dari stdout, lalu memvalidasinya dengan validator Python. Jalur ini tidak boleh fallback ke parser Python referensi.
- compiler/ir.py: IR v1 kanonis beserta validator schema, path, source map dan feature.
- compiler/bytecode.py + compiler/vm.py: backend bytecode dan VM Python untuk IR v1.
- compiler/bootstrap.py: menjalankan build identik dua kali melalui fungsi frontend yang sama. Ini membuktikan reproduksibilitas pada host yang sama, belum compiler mandiri.

## Gate pembuktian

1. tests/test_compiled_frontend_vm.py membandingkan IR frontend .cuk dengan parser referensi saat frontend mem-parsing compiler.cuk itu sendiri; tes terpisah mengirim collections/control flow ke VM.
2. Setiap dokumen IR harus lolos compiler.ir.validate, termasuk feature terurut dan source_map yang mengikuti traversal node.
3. Host Python dan backend Python disebutkan dengan jujur sampai bootstrap dua tahap benar-benar menjalankan artefak compiler tahap pertama sebagai compiler tahap kedua.
4. Jangan mengubah kegagalan menjadi fallback; perbaiki parser/serializer .cuk atau catat batasan yang nyata.
5. Gunakan runner konformansi, manifest dan tes yang sudah ada. Jangan membuat branch, PR, daemon, status report per-fitur, atau suite duplikat bila tes yang ada sudah menyatakan kontrak.

## Urutan kerja

1. Luluskan parser frontend untuk mem-parsing examples/self_hosting/compiler.cuk sendiri dan menyamai AST IR kanonis tanpa fallback.
2. Pastikan control-flow/collection mencapai bytecode VM dan jalur CLI tetap lulus.
3. Bangun bootstrap sungguhan: stage 1 harus menghasilkan artefak compiler yang bisa dijalankan tanpa interpreter/frontend Python untuk parsing source; stage 2 menggunakan artefak itu untuk membangun ulang compiler, lalu membandingkan artefak dan menjalankan konformansi.
4. Nyatakan self-hosting penuh hanya setelah tahap tersebut lulus di CI dari commit yang sama.

## Klaim yang belum boleh dibuat

IR v1, bytecode VM, backend multi-target, parser source .cuk, dan bukti build berulang bukan bukti terpisah bahwa compiler sudah mandiri penuh. Status tetap belum self-hosted penuh sampai bootstrap dua tahap mandiri benar-benar terverifikasi.
