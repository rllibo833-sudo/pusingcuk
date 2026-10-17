# Warung Bahasa .cuk — paket pembelajaran

Paket ini mengumpulkan empat contoh program untuk membantu PusingCuk AI mempelajari pola aturan deterministik dalam bahasa .cuk.

## Berkas

- `warung_kontrak.cuk`: validasi rentang, klasifikasi status source, pemetaan diagnostik.
- `warung_bukti.cuk`: pembedaan bukti kompilasi, runtime, fixture, dan paritas target.
- `warung_prioritas.cuk`: triase perbaikan berdasarkan urgensi, dampak, risiko, dan regresi.
- `warung_evolusi.cuk`: gerbang keputusan untuk spesifikasi, implementasi, fixture, dan klaim rilis.

## Tujuan pembelajaran

1. Menggunakan aturan deterministik yang hasilnya dapat diprediksi.
2. Memisahkan hasil compiler, runtime, dan fixture agar tidak membuat klaim yang berlebihan.
3. Menolak nilai di luar rentang dan status yang tidak dikenal.
4. Menjadikan hasil pengujian sebagai bukti sebelum menyatakan fitur bahasa kompatibel.
5. Mengembangkan contoh ini menjadi fixture konformansi setelah sintaks dan hasil aktual diverifikasi.

## Batasan penting

Paket ini adalah contoh pembelajaran, bukan fitur inti compiler dan bukan integrasi otomatis ke PusingCuk AI. Menaruh file di repositori tidak otomatis membuat AI mengindeks atau menggunakannya; pipeline retrieval/indeks PusingCuk AI harus dikonfigurasi terpisah untuk memasukkan direktori ini.

Kode belum diklaim lolos compiler. Jalankan pemeriksaan sintaks dan runtime yang benar-benar tersedia pada branch ini sebelum menjadikan file sebagai fixture normatif. Beberapa operasi logika dan ekspresi pada contoh mungkin memerlukan penyesuaian terhadap implementasi parser aktual.

Tidak ada kode yang mengakses jaringan, rahasia, filesystem, shell, atau layanan produksi.
