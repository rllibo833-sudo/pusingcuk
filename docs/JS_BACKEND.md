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

Backend ini adalah target JavaScript pertama. IR v1 juga bisa disimpan sebagai JSON untuk pertukaran alat, tetapi JSON IR bukan bytecode atau program yang dapat langsung dieksekusi. Backend Python, HTML mandiri, dan VM JSON tersedia sebagai target eksperimental terpisah dengan cakupan berbeda. WebAssembly, bundling frontend yang lengkap, dan integrasi blockchain adalah target lanjutan yang memerlukan kontrak fitur dan tes kompatibilitas masing-masing.

## Tes

\`\`\`sh
python -m unittest tests.test_js_backend -v
\`\`\`

Tes eksekusi membutuhkan Node.js; tanpa Node.js, tes eksekusi akan dilewati.


## Standard-library subset

The Python importer maps only `statistics.mean` and `statistics.median` to `rata_rata` and `median`. These are implemented in the JS runtime and therefore also available in HTML output. Empty lists, booleans, non-numeric values, and non-finite numbers fail at runtime. This is not full Python `statistics` compatibility; VM and native C support are not claimed.
