# Sistem Modul PusingCuk

Status: **dua mekanisme modul tersedia, tetapi belum satu kontrak lintas-target**. Jangan menyamakan pemuatan dinamis interpreter dengan ekspansi modul pada compiler.

## Mekanisme yang sudah ada

### 1. Pemuatan dinamis pada interpreter referensi: `angkut("file.cuk")`

Evaluator modular memiliki dukungan `angkut()` untuk berkas lokal berekstensi `.cuk` atau `.pusingcuk`, jalur relatif terhadap berkas pemanggil, cache modul, deteksi siklus, dan pembatasan akses direktori proyek. Hasilnya berupa lingkungan modul yang dapat diakses melalui nama anggotanya. Ini kemampuan interpreter referensi, **bukan** bukti dukungan identik pada C, JavaScript, atau VM.

### 2. Ekspansi modul pada compiler: `pakai ... sebagai` dan `ekspor fungsi`

Contoh sumber kanonis:

```cuk
jancuk
pakai "lib/angka.cuk" sebagai angka
hedeh angka.tambah(20, 22)
selesai jancuk
```

Modul yang diekspor:

```cuk
jancuk
ekspor fungsi tambah
fungsi tambah(a, b)
    balek a + b
selesai fungsi
selesai jancuk
```

Resolver `library/module_system.py` mengembangkan sumber secara statis, menyelesaikan jalur relatif, membatasi impor ke direktori proyek, dan menerapkan batas jumlah/kedalaman/ukuran sumber. Format lama `.pusingcuk` tetap didukung demi kompatibilitas. Ini bukan sandbox dan belum menjadi package manager.

## Batas kontrak sekarang

- `angkut()` dan `pakai ... sebagai` adalah dua jalur implementasi berbeda; keduanya belum disatukan ke satu model modul.
- Dukungan ekspansi compiler tidak otomatis berarti target hasilnya menjalankan impor dengan semantik yang sama.
- Paket eksternal, versi paket, lockfile, dan resolusi versi belum tersedia.
- Kegagalan impor harus berupa `ModuleImportError`/diagnostik yang menjelaskan path atau ekspor yang bermasalah; jangan mengubahnya menjadi fallback tersembunyi.
- Jangan menyebut modul portabel lintas-target sampai fixture sumber yang sama lulus pada target yang diklaim.

## Urutan penyatuan

1. Pertahankan kedua mekanisme yang sudah ada tanpa menduplikasi resolver baru.
2. Tetapkan satu kontrak modul yang menyebut sumber, alias, ekspor, cache/evaluasi sekali, root proyek, siklus, dan kelas error.
3. Hubungkan parser/evaluator referensi dengan kontrak ekspor yang sama tanpa mematahkan program lama.
4. Baru setelah itu implementasikan adapter target dan package eksternal berversi; jangan mengklaim fitur yang belum ada.
