# Kebijakan Keamanan Pusingcuk

## Melaporkan kerentanan

Jangan membuka issue publik untuk kerentanan yang belum diperbaiki atau menyertakan exploit, token, kata sandi, data pribadi, maupun kode yang dapat membahayakan pengguna.

Jika fitur **Report a vulnerability** tersedia pada tab Security repositori GitHub ini, gunakan pelaporan privat tersebut. Jika fitur itu tidak tersedia, hubungi pemilik repositori melalui profil GitHub dan minta kanal pelaporan privat sebelum mengirim rincian teknis.

Sertakan versi atau commit yang terdampak, platform, langkah reproduksi minimal, dampak yang diperkirakan, dan mitigasi sementara bila ada. Jangan mengirim rahasia aktif; cabut atau rotasi kredensial yang mungkin sudah terungkap.

## Cakupan dan batas keamanan

Pusingcuk masih eksperimental. Runtime native, Pusingcuk Studio, dan backend PVM **bukan sandbox keamanan** dan tidak boleh dipakai untuk menjalankan kode tak tepercaya dengan akses ke data atau akun penting.

**Peringatan aktif (prioritas tinggi):** backend JavaScript PVM (`src/backends/js/compiler.js`) menggunakan `Function()` bersama `with` untuk mengevaluasi ekspresi. Ini bukan batas isolasi: ekspresi yang dibuat penyerang dapat berpotensi mencapai kemampuan JavaScript/Node.js. Backend PVM juga menyediakan operasi file dan jaringan; path dan resource belum dibatasi sebagai sandbox OS. Jangan menganggap bytecode PVM sebagai format aman untuk distribusi atau eksekusi dari pihak lain. Pelacakan internal yang sudah ada: [#75](https://github.com/rllibo833-sudo/pusingcuk/issues/75). Jangan membuka issue publik duplikat untuk temuan ini.

Laporan yang relevan meliputi eksekusi kode di luar batas yang dimaksud, akses file atau jaringan tanpa izin, traversal path atau symlink, kebocoran kredensial, kerusakan memori, bypass batas resource, serta workflow CI yang dapat mengekspos token atau menjalankan kode berbahaya dengan hak istimewa.

## Gerbang keamanan sebelum rilis

- [ ] Evaluasi ekspresi memakai parser/evaluator dengan grammar terbatas; tidak menggunakan `eval`, `Function`, atau `vm` sebagai sandbox.
- [ ] Akses file dan jaringan nonaktif secara default atau dibatasi melalui isolasi OS dan kebijakan capability eksplisit.
- [ ] Tes negatif membuktikan bahwa ekspresi tidak dapat mengakses `process`, global host, constructor/prototype escape, path traversal, symlink escape, atau jaringan tanpa izin.
- [ ] Batas ukuran input, payload, respons jaringan, waktu tunggu, dan penggunaan resource diuji.
- [ ] CI tidak diberi secret yang tidak diperlukan dan permission token tetap minimum.

## Dukungan versi

Versi pengembangan terbaru pada branch `main` adalah fokus utama perbaikan. Belum ada janji dukungan keamanan untuk rilis lama atau versi pra-rilis tertentu. Status perbaikan dan advisori akan dipublikasikan setelah mitigasi tersedia.
