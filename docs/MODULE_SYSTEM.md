# Sistem Modul Pusingcuk

Status: **implementasi awal pada compiler multi-target**. Impor belum didukung oleh interpreter langsung atau runtime native C.

## Sintaks

Impor eksplisit menggunakan alias:

    jancuk
    pakai "util/angka.pusingcuk" sebagai angka
    hedeh angka.tambah(20, 22)
    selesai jancuk

Modul harus menyatakan fungsi mana yang boleh diimpor:

    jancuk
    ekspor fungsi tambah
    fungsi tambah(a, b)
        balek a + b
    selesai fungsi
    selesai jancuk

## Batas versi pertama

- Hanya file .pusingcuk lokal; tidak ada unduhan paket/jaringan.
- Jalur relatif terhadap file pemanggil dan dibatasi pada direktori proyek.
- Menolak traversal, ekstensi salah, ekspor tidak dikenal, siklus, alias ganda, dan benturan nama.
- Batas awal: 128 modul, kedalaman impor 32, total sumber 1 MiB.
- Modul dikembangkan saat kompilasi; fungsi modul diberi namespace deterministik.
- Kompilasi multi-target dapat memakai hasil ekspansi, tetapi semantik belum disatukan dengan interpreter langsung atau runtime native C.
- Ini bukan sandbox. Batas direktori mengurangi salah akses, tetapi tidak membuat kode asing aman dijalankan.

## Tahapan berikutnya

1. Menambahkan konformansi modul pada interpreter langsung.
2. Mengimplementasikan resolver setara di runtime native C dengan batas sumber/alokasi.
3. Memastikan impor berulang dan dependency graph menghasilkan evaluasi sekali.
4. Membakukan sintaks dan diagnostik pada SPEC.md sebelum menyebut sistem modul stabil.
5. Menambahkan tooling paket lokal setelah modul stabil.

Adapter database/server/Web3 host-side dijelaskan di OFFLINE_ADAPTERS.md; adapter itu belum dapat dipanggil langsung dari kode Pusingcuk.
