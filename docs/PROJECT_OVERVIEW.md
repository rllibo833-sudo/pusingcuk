# PusingCuk — Ikhtisar Proyek

> **Bahasa warung. Mesin serius.**

**Tanggal snapshot dokumentasi:** 18 Oktober 2026  
**Kontrak bahasa:** `0.6-dev`  
**Versi paket Python:** `0.8.0.dev0`  
**Kematangan:** eksperimental / alpha — bukan rilis stabil.

Dokumen ini merangkum fungsi repositori untuk pembaca, kontributor, dan calon pengguna. Status implementasi dapat berubah; gunakan matriks kompatibilitas dan fixture dari commit yang sedang dipakai untuk keputusan teknis.

## Apa itu PusingCuk?

PusingCuk adalah eksperimen bahasa pemrograman dengan ekstensi utama `.cuk`, kata kunci Indonesia, dan identitas kosakata yang terinspirasi bahasa percakapan. Tujuannya adalah membuat proses belajar sintaks terasa akrab sekaligus menjadi laboratorium terbuka untuk interpreter, compiler, runtime, dan alat pengembangan.

Contoh:

```cuk
jancuk
lah nama = "Dunia"
fungsi sapa(orang)
    balek "Halo, " + orang
selesai fungsi
hedeh sapa(nama)
selesai jancuk
```

## Peta fungsi repositori

| Komponen | Kegunaan | Batas penting |
|---|---|---|
| `lexer.py`, `parser.py`, `ast_nodes.py` | Mengubah teks sumber menjadi token dan struktur program | Harus tetap sesuai SPEC dan fixture |
| `evaluator.py`, `pusingcuk_new.py` | Jalur interpreter Python referensi | Membutuhkan Python untuk jalur referensi |
| `compiler/` | IR dan backend eksperimental | Tiap target mendukung subset berbeda |
| `native/` | Runtime C untuk subset yang diuji | Belum setara penuh dengan interpreter referensi |
| `library/` | Kontrak built-in, kosakata mesin, fungsi dan adapter | Registry tidak berarti semua target sudah mendukung semuanya |
| `tests/`, `tools/conformance.py` | Tes unit dan bukti konformansi | Hasil hanya berlaku untuk tes dan commit yang berjalan |
| `examples/` | Contoh untuk belajar dan uji coba | Contoh bukan jaminan kesiapan produksi |
| `library/assistant.py` dan modul terkait | Alat PusingCuk AI untuk membantu alur .cuk | Tidak membuktikan model fondasi dilatih sendiri atau semua output benar |
| `web/`, `site/`, `android-studio/` | UI, situs, dan prototipe distribusi yang ada di repo | Keberadaan kode tidak sama dengan layanan/aplikasi produksi |
| `.github/workflows/` | Otomasi tes, build, dan packaging | Workflow dapat berbeda pemicu dan cakupan; cek hasil terbaru |

## Contoh penggunaan yang masuk akal

- Belajar struktur program, variabel, kondisi, loop, fungsi, koleksi, dan built-in yang tercantum.
- Menguji desain bahasa melalui spesifikasi dan fixture.
- Menghasilkan artefak target eksperimental untuk subset yang didukung.
- Menjalankan subset program melalui runtime C setelah build yang sesuai.
- Menggunakan contoh dan alat AI yang tersedia untuk mempercepat eksperimen .cuk, dengan validasi compiler/runtime sebagai sumber bukti.

## Cara membaca klaim fitur

Gunakan empat tingkat berikut secara konsisten:

1. **Ada di repo** — file atau implementasi ditemukan.
2. **Berfungsi pada jalur tertentu** — ada contoh atau hasil uji yang sesuai.
3. **Terverifikasi** — fixture/pengujian target yang relevan lulus pada commit yang sama.
4. **Siap produksi** — memerlukan bukti tambahan untuk keamanan, ketahanan, deployment, pemantauan, dan lingkungan nyata.

Jangan menyamakan keempat tingkat tersebut. Target compiler, contoh Android, antarmuka web, adapter, dan modul AI masing-masing harus dinilai menurut jalur eksekusinya sendiri.

## Kekurangan dan risiko saat ini

- **Belum stabil:** versi kontrak `0.6-dev` dan paket `0.8.0.dev0` menunjukkan jalur pengembangan, bukan jaminan API stabil.
- **Paritas terbatas:** interpreter referensi, runtime C, JavaScript, Python, HTML, dan VM tidak otomatis memiliki cakupan identik.
- **Jalur referensi bergantung pada Python:** runtime C mandiri hanya mencakup subset bahasa yang dinyatakan dan diuji.
- **Ekosistem belum lengkap:** sistem modul lintas-runtime, ABI/FFI stabil, WebAssembly, binding browser lengkap, serta integrasi database/blockchain produksi tidak boleh dipasarkan sebagai kemampuan yang sudah selesai.
- **Batas keamanan:** eksekusi kode bukan sandbox OS; kode tak tepercaya dapat berisiko mengakses sumber daya proses.
- **AI bukan oracle:** output AI harus diperiksa oleh compiler, tes, dan runtime. Modul asisten tidak sama dengan model fondasi yang dilatih sendiri.
- **Kesiapan distribusi berbeda:** build yang berhasil tidak membuktikan instalasi dan penggunaan berhasil pada semua perangkat sasaran.
- **Dokumentasi historis:** catatan audit/roadmap bertanggal harus dibedakan dari status aktif dan tidak boleh dijadikan klaim tunggal.

## Rekomendasi prioritas

1. Jadikan `SPEC.md`, kontrak semantik, kontrak built-in, fixture, dan matriks kompatibilitas sebagai satu rantai bukti.
2. Perbaiki kegagalan CI yang dapat direproduksi sebelum menambah fitur.
3. Perluas dukungan runtime berdasarkan celah semantik dan tes yang spesifik, bukan jumlah fitur.
4. Pertahankan kamus dan panduan pemula sebagai jalur belajar, sementara detail implementasi ditempatkan di dokumen teknis.
5. Labeli fitur AI, UI, packaging, dan target compiler sesuai bukti terbaru.
6. Jalankan pemeriksaan keamanan workflow dan uji distribusi pada target nyata sebelum membuat klaim produksi.

## Bukan bagian dari janji produk

Dokumen ini tidak menjanjikan bahasa stabil, kompatibilitas penuh semua target, model AI buatan sendiri, sandbox keamanan umum, layanan SaaS siap pakai, atau dukungan produksi untuk integrasi yang masih berupa roadmap.

## Referensi kanonis

- [Spesifikasi bahasa](../SPEC.md)
- [Kontrak semantik](SEMANTIC_CONTRACT.md)
- [Kompatibilitas](COMPATIBILITY.md)
- [Kontrak built-in](../library/builtin_contract.json)
- [Fixture konformansi](CONFORMANCE_FIXTURES.md)
- [Kamus Bahasa Warung](KAMUS_PUSINGCUK.md)
