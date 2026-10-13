# Kontrak Fixture Konformansi Pusingcuk

**Versi bahasa:** `0.4-dev`. Manifest berisi 61 fixture: 61 wajib pada reference; 56 wajib dan 5 eksplisit unsupported pada native C.

Harness konformansi aktif ada di `tools/conformance.py` dan dijalankan oleh CI. Manifest membandingkan perilaku yang terlihat pengguna pada interpreter referensi Python dan runtime native C. Fixture kanonis baru memakai ekstensi `.cuk`; contoh lama berekstensi `.pusingcuk` tetap boleh digunakan untuk kompatibilitas.

## Tujuan

Fixture mengikat empat sumber: spesifikasi bahasa, implementasi, dokumentasi, serta perilaku yang dapat diulang. Sebuah fitur hanya boleh diklaim lintas-runtime jika manifest menandainya `required` pada kedua runtime dan hasilnya lulus pada keduanya.

## Bentuk manifest

Manifest aktif berada di `tests/conformance/manifest.json`. Setiap fixture mendefinisikan ID unik, sumber relatif di direktori fixture, profil, fitur yang diperlukan, hasil yang diharapkan, dan status runtime.

Contoh kasus positif:

```json
{
  "schema_version": 1,
  "id": "core.cuk-source-extension",
  "source": "canonical_extension.cuk",
  "profile": "core",
  "requires": ["source-extension", "variables", "arithmetic", "output"],
  "expected": {
    "exit_code": 0,
    "stdout": "42\n",
    "stderr_class": null
  },
  "runtimes": {
    "reference": "required",
    "native": "required"
  }
}
```

Fixture negatif menambahkan `stderr_class` dan `source_line`. Metadata tidak dapat memilih perintah shell, executable, atau environment.

## Kontrak error

Program sumber menggunakan kode keluar yang sama pada Python referensi dan native C:

| Keadaan | Exit code | Kelas stderr |
|---|---:|---|
| Sukses | `0` | Tidak ada |
| Kesalahan runtime | `1` | `runtime_error` |
| Kesalahan sintaks | `2` | `syntax_error` |
| Berkas sumber tidak ditemukan pada CLI | `3` | Diagnostik CLI, di luar manifest sumber |

Kesalahan sintaks dan runtime ditulis ke stderr dengan nomor baris bila tersedia. Harness membandingkan kelas error dan nomor baris, bukan kalimat lengkap atau kolom yang belum menjadi kontrak bersama. Pesan Python boleh menyertakan kolom tambahan; perbedaan tersebut tidak boleh mengubah kelas maupun exit code.

Manifest tidak mengizinkan `exit_code_by_runtime`. Bila suatu runtime belum mengimplementasikan fitur, tandai `unsupported`; jangan menetapkan hasil yang berbeda pada fixture sama dan menyebutnya konformansi.

## Aturan metadata dan keamanan

- `schema_version` menetapkan versi format manifest; `id` wajib unik dan stabil.
- `source` harus berupa path relatif yang menyelesaikan lokasi di dalam `tests/conformance/`; absolute path dan traversal ditolak.
- `profile` mengelompokkan cakupan fitur, sementara `requires` mencantumkan seluruh fitur yang benar-benar digunakan.
- `expected.exit_code` dan `expected.stdout` selalu eksplisit.
- Fixture error harus menentukan kelas error yang dikenal dan nomor baris sumber yang diharapkan.
- Status runtime dibatasi pada `required`, `optional`, atau `unsupported`. Unsupported tidak dihitung sebagai PASS.
- Harness memakai timeout, direktori root yang ditetapkan, dan daftar command yang dibangun di kode; manifest tidak boleh menjalankan perintah arbitrar.
- Jangan menjalankan fixture tak tepercaya dengan token, kredensial, atau hak akses penting.

## Cakupan yang dijaga

1. Sintaks, alias resmi, komentar, string, ekstensi `.cuk`, dan error parsing.
2. Nilai dan angka: precedence, pembagian lantai/modulo negatif, boolean, short-circuit, dan pembagian nol.
3. Fungsi dan scope: return, aritas, nama belum dikenal, scope lokal tidak bocor, alias koleksi, dan rekursi.
4. List/kamus: identitas kunci, mutasi termasuk melalui parameter, indeks di luar batas, kunci hilang, dan batas kapasitas.
5. Kondisi, loop, iterasi rentang, dan batas eksekusi.
6. Built-in: hasil numerik, ties-to-even, akar kuadrat/pangkat, sinus/kosinus dalam radian, jumlah/rata-rata/median, cancellation, hasil pecahan, sampel duplikat, median ganjil/genap, daftar kosong, aritas salah, boolean/tipe koleksi invalid, batas integer aman inklusif/eksklusif, akumulasi di luar rentang aman, overflow/non-finite, dan status dukungan target.
7. CLI: kelas error, nomor baris, kode keluar, output dan input standar.
8. File, jaringan, browser, FFI, dan kapabilitas platform hanya diuji pada target yang secara eksplisit mendukungnya.

## Sumber kebenaran built-in

Nama, aritas, deskripsi, dan dukungan target harus sejalan di:

- `library/builtin_contract.json` — metadata kanonis.
- `library/stdlib.py` dan implementasi runtime yang memanggilnya.
- `docs/language/BUILTINS.md` — tabel dokumentasi yang diverifikasi oleh tes.
- `tests/test_builtin_contract.py` — perilaku built-in serta pemeriksaan metadata/dokumen.
- `tests/conformance/manifest.json` — perilaku bahasa yang diklaim lintas runtime.

Setiap status `supported` harus memiliki pengujian yang sesuai. Keberadaan fungsi dalam registry internal saja tidak cukup untuk mengklaim dukungan interpreter, native, atau backend.

## Perintah pengujian

```sh
python -m unittest discover -s tests -v
make test-native
python tools/conformance.py
```

## Hubungan dengan dokumen lain

- [Spesifikasi bahasa](../SPEC.md) menetapkan syntax dan semantik.
- [Kontrak semantik](SEMANTIC_CONTRACT.md) menetapkan invariant yang diuji.
- [Kompatibilitas](COMPATIBILITY.md) membatasi klaim portable.
- [Katalog built-in](language/BUILTINS.md) menjelaskan fungsi dan status per target.
- [Runtime native](NATIVE_RUNTIME.md) mencatat kemampuan C yang sudah teruji.
- [Contributing](../CONTRIBUTING.md) menentukan gerbang perubahan dan review.
