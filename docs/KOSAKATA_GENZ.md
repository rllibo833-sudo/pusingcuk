# Kosakata Slang Pusingcuk

Pusingcuk menggunakan slang Indonesia sebagai bagian dari identitas bahasanya. Kata-kata ini bukan hiasan semata: setiap alias punya makna yang konsisten dan tes.

## Alias resmi

| Slang | Kata kanonis | Makna |
|---|---|---|
| jir | hedeh | Tampilkan nilai ke keluaran standar. |
| adooh | kampret | Cabang alternatif dari kondisi njir. |
| gitu | selesai | Penanda penutup blok; tetap diikuti nama blok, misalnya gitu njir. |
| inthiseco | jancuk | Awal program. Program diakhiri dengan gitu inthiseco. |
| janggal | bukan | Negasi logika; membalik nilai benar/salah. |
| gas | jancuk | Memulai program. |
| spill | hedeh | Menampilkan nilai. |
| bestie | lah | Mendeklarasikan variabel. |
| valid | benar | Nilai boolean benar. |
| zonk | salah | Nilai boolean salah. |
| skip | kampret | Cabang alternatif kondisi. |
| kelar | selesai | Menutup blok; tetap diikuti nama blok. |

## Kosakata kondisi dan logika

| Kata/operator | Makna | Contoh |
|---|---|---|
| njir | Memulai kondisi | njir skor >= 5 |
| kampret | Cabang alternatif (opsional) | kampret |
| selesai njir | Menutup kondisi | selesai njir |
| benar | Nilai boolean benar; outputnya okelah | hedeh benar |
| salah | Nilai boolean salah; outputnya tidak | hedeh salah |
| dan | Logika AND dengan short-circuit | skor >= 5 dan benar |
| atau | Logika OR dengan short-circuit | skor < 5 atau salah |
| bukan | Negasi logika | bukan salah |
| ==, != | Sama / tidak sama | skor == 5 |
| <, <=, >, >= | Perbandingan urutan | skor >= 5 |

Operator aritmetika yang terdokumentasi: +, -, *, /, //, dan %. Ketersediaan setiap operator bergantung pada runtime; lihat matriks runtime native dan backend C.

## Contoh

    inthiseco
    lah skor = 7
    njir skor >= 5 dan benar
        jir skor
    adooh
        jir 0
    gitu njir
    jir benar == 1
    jir janggal salah
    gitu inthiseco

Hasil yang diharapkan pada interpreter modular:

    7
    tidak
    okelah

## Loop dan fungsi pada backend C

Backend C kini memiliki dukungan teruji untuk loop `mumet` dan fungsi tingkat atas dengan parameter serta nilai balik integer. Fungsi dapat dipanggil sebelum definisinya dan mendukung rekursi dengan batas kedalaman 100; setiap loop dibatasi 10.000 iterasi. Backend menolak `lah` di dalam loop, parameter/nilai balik boolean, `untuk`, teks, koleksi, dan input. Lihat [panduan backend C](C_BACKEND.md).

## Contoh kosakata Gen Z/Gen Alpha

Contoh runnable tersedia di `library/loops_functions_genz.pusingcuk`. Untuk mencoba seluruh contoh termasuk teks, gunakan `python pusingcuk_new.py library/loops_functions_genz.pusingcuk`. Daftar kanonis dan status runtime tetap tercatat di `library/kosakata.json`.

## Aturan desain

- Kata slang adalah alias resmi, bukan pengganti wajib; kata kanonis lama tetap berlaku.
- Ejaan alias peka huruf besar/kecil, sama seperti kata kunci lain.
- Alias dinormalisasi pada tahap leksikal sehingga parser dan evaluator tetap punya satu makna kanonis.
- Runtime native C dan backend compiler memiliki subset yang berbeda. Hanya fitur dengan tes eksplisit yang boleh diberi status didukung.
- Kata slang/alias baru harus ditambahkan bersama spesifikasi, contoh, tes Python, dan tes native/compiler yang relevan.

## Kosakata inti dan fungsi bawaan

| Kata/fungsi | Arti | Status runtime native C |
|---|---|---|
| jancuk / inthiseco | Memulai program | Teruji |
| selesai / gitu | Menutup blok | Teruji |
| lah | Membuat variabel baru | Teruji |
| hedeh / jir | Menampilkan nilai | Teruji |
| njir / kampret / adooh | Kondisi dan cabang alternatif | Teruji |
| mumet | Perulangan selama kondisi benar | Teruji |
| untuk ... dalam ... | Mengunjungi elemen koleksi | List, teks UTF-8, kamus (menghasilkan kunci), dan rentang() didukung |
| panjang(nilai) | Menghitung jumlah item/karakter/entri | List, teks, kamus, dan rentang didukung |
| rentang(...) | Membuat rentang bilangan bulat dengan batas akhir eksklusif | Didukung; 1–3 argumen bulat |
| tanya | Membaca masukan pengguna | Didukung melalui stdin; diuji lewat fixture native |
| fungsi / balek | Mendefinisikan dan mengembalikan nilai fungsi | Didukung pada subset native teruji |
| Kamus {kunci: nilai} | Menyimpan pasangan kunci-nilai | Didukung pada subset native teruji; batas 256 entri |

## Backend compiler C eksperimental

Backend C kini memiliki subset teruji untuk integer, boolean, perbandingan, logika short-circuit, dan kondisi njir/kampret. Ini berbeda dari runtime C mandiri: backend C masih menolak teks, koleksi, input, loop, dan fungsi. Lihat panduan backend C sebelum mengandalkannya.

Untuk glossary yang bisa dibaca mesin, lihat library/kosakata.json. Contoh yang siap dicoba ada di library/conditional_logic.pusingcuk.
