# Kontrak Semantik Inti Pusingcuk

Status: kontrak kerja yang dibuktikan sebagian oleh interpreter referensi dan runtime native. Fixture konformansi di `tests/conformance/manifest.json` adalah bukti eksekusi untuk subset yang tercantum, bukan klaim bahwa semua fitur bahasa sudah setara.

## Invarian yang harus dipertahankan

| Area | Aturan kontrak | Bukti otomatis saat ini |
|---|---|---|
| Struktur program | `jancuk` membuka program; `selesai jancuk` menutupnya | Fixture seluruh suite |
| Output | `hedeh` menghasilkan satu nilai per baris | Aritmetika, list, fungsi, alias |
| Boolean | `benar` dan `salah` adalah boolean, bukan angka | Identitas kunci kamus dan short-circuit |
| Kesetaraan | Boolean tidak setara dengan angka yang tampak serupa | Fixture identitas kunci kamus; suite native tambahan |
| Evaluasi logika | Interpreter referensi melakukan short-circuit; runtime native belum dinyatakan setara | Fixture short-circuit wajib pada reference, `UNSUPPORTED` pada native |
| Fungsi | Parameter diteruskan, `balek` mengembalikan nilai | Fixture fungsi penjumlahan |
| Daftar | Indeks dimulai dari nol; assignment indeks memperbarui elemen | Fixture list/index/mutasi |
| Kamus | Boolean dan angka adalah jenis kunci berbeda; `panjang` menghitung entri | Fixture identitas kunci |
| Rentang | Batas akhir `rentang` tidak termasuk hasil | Fixture loop rentang |
| Alias slang | Alias dan kata kanonis harus mempertahankan makna | Fixture alias slang |
| Diagnostik | Program gagal harus memiliki exit code non-zero dan stderr | Fixture sintaks salah |

## Menambah fixture

1. Buat program minimal `.pusingcuk` yang hanya menguji satu perilaku.
2. Tambahkan ID unik, `requires`, hasil yang diharapkan, dan status setiap runtime ke manifest.
3. Tandai runtime `required` hanya jika implementasi dan spesifikasinya memang menuntut dukungan; gunakan `unsupported` secara eksplisit untuk target yang belum mengimplementasikannya.
4. Jalankan `python tools/conformance.py` dan `python -m unittest discover -s tests -v`.
5. Jangan mengubah output harapan hanya agar tes hijau. Jika perilaku tidak sesuai, tentukan apakah implementasi atau spesifikasi yang keliru, lalu perbaiki dengan tes regresi.

## Batas yang diketahui

- Harness saat ini membandingkan stdout byte-for-byte, exit code, dan kelas error umum. Ia belum menetapkan katalog kode error publik yang stabil.
- Fixture awal bukan bukti parity lengkap; runtime native saat ini belum lulus uji short-circuit terhadap variabel tak dikenal di cabang yang semestinya tidak dievaluasi. Statusnya dicatat `UNSUPPORTED`, bukan disamarkan sebagai lulus. Perbaikan semantik native adalah prioritas berikutnya.
- Tes harus bertambah untuk scope, rekursi, overflow, input, koleksi kompleks, error lokasi, dan tiap backend baru.
- `native` berarti runtime C langsung yang diuji pada CI Linux GCC/Clang. Ini tidak otomatis membuktikan kompatibilitas Windows, macOS, atau perangkat Android/Termux.
- Compiler IR, backend C hasil generasi, WebAssembly, JavaScript, serta ABI/FFI tetap pekerjaan terpisah sampai ada implementasi dan fixture yang menjalankannya.
