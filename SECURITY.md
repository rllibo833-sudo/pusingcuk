# Kebijakan Keamanan Pusingcuk

## Melaporkan kerentanan

Jangan membuka issue publik untuk kerentanan yang belum diperbaiki atau menyertakan exploit, token, kata sandi, data pribadi, maupun kode yang dapat membahayakan pengguna.

Jika fitur **Report a vulnerability** tersedia pada tab Security repositori GitHub ini, gunakan pelaporan privat tersebut. Jika fitur itu tidak tersedia, hubungi pemilik repositori melalui profil GitHub dan minta kanal pelaporan privat sebelum mengirim rincian teknis.

Sertakan versi atau commit yang terdampak, platform, langkah reproduksi minimal, dampak yang diperkirakan, dan mitigasi sementara bila ada. Jangan mengirim rahasia aktif; cabut atau rotasi kredensial yang mungkin sudah terungkap.

## Cakupan dan batas keamanan

Pusingcuk masih eksperimental. Runtime native dan Pusingcuk Studio saat ini **bukan sandbox keamanan** dan tidak boleh dipakai untuk menjalankan kode tak tepercaya dengan akses ke data atau akun penting.

Laporan yang relevan meliputi eksekusi kode di luar batas yang dimaksud, akses file atau jaringan tanpa izin, kebocoran kredensial, kerusakan memori, bypass batas resource, serta workflow CI yang dapat mengekspos token atau menjalankan kode berbahaya dengan hak istimewa.

## Dukungan versi

Versi pengembangan terbaru pada branch `main` adalah fokus utama perbaikan. Belum ada janji dukungan keamanan untuk rilis lama atau versi pra-rilis tertentu. Status perbaikan dan advisori akan dipublikasikan setelah mitigasi tersedia.
