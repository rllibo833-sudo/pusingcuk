# Audit Kesenjangan Runtime Native Pusingcuk

**Status:** Audit sumber selesai; implementasi kamus/fungsi native belum dilakukan dalam perubahan ini.  
**Basis audit:** `main` setelah PR #10, merge commit `a40e1efe061932643f5135702eceba6ee4908bba`.  
**Tujuan:** Menjadikan executable native dapat menjalankan bahasa Pusingcuk tanpa Python saat runtime, dengan perilaku yang dibuktikan oleh fixture dan CI.

## Temuan terverifikasi dari sumber

1. Runtime native ada di `native/pusingcuk.c`, dikompilasi sebagai C11 melalui Makefile. Executable yang telah dibangun tidak memerlukan Python saat dijalankan.
2. CI `.github/workflows/tests.yml` memiliki job Python 3.11/3.12 dan job native `make test-native`. Tes Python bukan bukti kesetaraan native.
3. PR #10 telah merged. PR tersebut mencatat GitHub Actions run #42 sukses untuk Python 3.11, Python 3.12, dan `make test-native`; cakupan termasuk input stdin dan indeks/iterasi teks UTF-8.
4. Nilai native saat ini: `NUM`, `STR`, `BOOL`, `LIST`, dan `RANGE`. Tidak ada tipe `DICT`, struktur pasangan kunci/nilai, atau implementasi indeks kamus.
5. Pemanggilan `panjang` dan `rentang` ditangani sebagai built-in khusus. Pemanggilan fungsi lain berakhir dengan error `fungsi native belum didukung`.
6. Parser/eksekutor native berbasis baris dan lingkungan variabel global tetap (`vars[NV]`). Fungsi buatan pengguna membutuhkan penyimpanan definisi, lingkungan lokal, aturan resolusi nama, pemulihan variabel setelah panggilan, propagasi `balek`, dan batas rekursi.
7. List memakai alokasi dinamis, tetapi item dibatasi dan teks memakai buffer tetap `SZ`. Kamus native perlu batas kapasitas, penanganan kegagalan alokasi, kesetaraan kunci, kebijakan kunci tidak valid, dan cleanup konsisten.
8. Ada konflik kosakata: `janggal` saat ini alias `bukan` (negasi). Permintaan terbaru menetapkan `jujur` sebagai benar dan `janggal` sebagai salah. Ini harus diselesaikan eksplisit di lexer, native runtime, SPEC, contoh, dan tes sebelum mengganti makna; satu kata tidak boleh menjadi negasi sekaligus literal boolean.

## Keputusan arsitektur yang direkomendasikan

- C adalah target runtime mandiri; Python dipertahankan sementara sebagai referensi perilaku dan alat pengembangan/tes, bukan dependensi runtime final.
- `SPEC.md` adalah kontrak semantik; setiap fitur wajib punya fixture `.pusingcuk` dan ekspektasi hasil/error yang dijalankan melalui `make test-native`.
- Implementasi dibuat bertahap: kamus native terlebih dahulu, kemudian fungsi buatan pengguna, lalu uji konformansi lintas-runtime.
- Tetapkan semantik boolean: `jujur` alias `benar`; `janggal` alias `salah`; negasi tetap `bukan`. Ini mengubah alias `janggal` saat ini dan memerlukan tes serta catatan kompatibilitas.
- Fungsi native perlu lingkungan lokal terpisah, jumlah argumen tepat, return dengan/tanpa nilai, batas kedalaman panggilan, dan pemulihan scope pada semua jalur.
- Kamus perlu literal kosong/nonkosong, baca/tulis, iterasi kunci, `panjang`, kunci hilang, dan penolakan tipe kunci yang tidak didukung.
- Jangan menyebut native setara penuh, aman untuk kode tak tepercaya, atau production-ready sebelum matriks konformansi dan threat model membuktikannya.

## Urutan milestone

1. Kontrak dan fixture konformansi lintas-runtime.
2. Kamus native: nilai, kepemilikan memori, literal, indeks, assignment, iterasi, panjang, serta fixture positif/negatif.
3. Fungsi native: definisi, parameter, scope lokal, pemanggilan, `balek`, rekursi terbatas, arity error, dan fixture.
4. Kosakata boolean: selaraskan `jujur`/`janggal` di lexer modular, C, SPEC, glossary, contoh, dan tes.
5. CI konformansi: tes modular Python 3.11/3.12 dan native pada setiap PR; hasil terikat ke SHA yang diuji.
6. Uji perangkat: setelah CI hijau, build dan jalankan native binary pada Termux/Android nyata.

## Checklist audit sebelum PR implementasi

- Bandingkan branch dengan `main`; pastikan hanya satu milestone berubah.
- Review diff, khususnya cleanup memori, batas indeks, error path, nested blocks, scope, dan batas eksekusi.
- `make test-native` dan seluruh tes modular harus lulus.
- Tambahkan fixture invalid/boundary, bukan hanya contoh sukses.
- Binary, output sementara, cache, dan file build tidak boleh masuk Git.
- README, SPEC, glossary, dan matriks native harus sesuai fitur yang teruji.
- PR menunggu keputusan pemilik; jangan merge otomatis.

## Riset desain

- [LLVM Kaleidoscope: Parser dan AST](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl02.html) menekankan representasi fungsi sebagai struktur/prototype dan body AST, bukan sekadar pengenalan token.
- [LLVM Kaleidoscope: Code generation](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl03.html) memisahkan AST dari backend. Pusingcuk belum perlu langsung memakai LLVM; stabilkan kontrak dan konformansi runtime C lebih dahulu.

## Batas bukti

Audit ini adalah pemeriksaan sumber melalui GitHub. Terminal lokal/Termux tidak dijalankan dalam sesi audit ini. PR #10 mencatat hasil CI untuk SHA PR tersebut, bukan perubahan baru. Tidak ada klaim kamus/fungsi native telah diimplementasikan.
