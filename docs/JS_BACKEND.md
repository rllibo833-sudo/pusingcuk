# Backend JavaScript PusingCuk v1

Status: backend eksperimental yang menerjemahkan subset AST PusingCuk ke berkas JavaScript mandiri untuk Node.js. Ini kode hasil kompilasi, bukan interpreter yang mem-parsing ulang sumber saat program berjalan.

## Gunakan

\`\`\`sh
python -m compiler.js_backend program.pusingcuk -o program.js
node program.js
\`\`\`

Tanpa \`-o\`, JavaScript ditulis ke stdout. Kesalahan sintaks dan fitur yang belum didukung menghentikan kompilasi dengan exit code bukan nol.

## Fitur saat ini

- variabel, assignment, literal angka/teks/boolean;
- output \`hedeh\`;
- operasi aritmetika, perbandingan, logika short-circuit;
- \`njir\` / \`kampret\`, \`mumet\`, dan \`untuk\`;
- fungsi, parameter, dan \`balek\`;
- daftar, kamus berbasis \`Map\`, akses dan assignment indeks;
- \`panjang()\` dan \`rentang()\`.

Input \`tanya\`, integrasi API/Node.js, module/package import, DOM/browser output, dan interop blockchain belum tersedia pada backend ini. Compiler harus menolak fitur yang belum didukung; jangan menganggap keberadaan backend ini berarti semua fitur PusingCuk sudah portabel.

## Peran dalam arsitektur multi-target

Alur awal:

\`PusingCuk source → parser/IR v1 → backend target → artifact\`

Backend ini adalah target JavaScript pertama. IR v1 juga bisa disimpan sebagai JSON untuk pertukaran alat, tetapi JSON IR bukan bytecode atau program yang dapat langsung dieksekusi. Backend Python, WebAssembly, HTML/browser bundling, dan integrasi blockchain adalah target lanjutan terpisah yang perlu kontrak fitur dan tes kompatibilitas masing-masing.

## Tes

\`\`\`sh
python -m unittest tests.test_js_backend -v
\`\`\`

Tes eksekusi membutuhkan Node.js; tanpa Node.js, tes eksekusi akan dilewati.
