# Status teknis dan roadmap PusingCuk

**Audit:** 15 Oktober 2026  
**Cakupan:** repositori `rllibo833-sudo/pusingcuk`, runtime bahasa `.cuk`, aplikasi AI, dokumentasi, CI, dan proyek Supabase yang dipetakan.  
**Status audit:** pembaruan dikerjakan langsung di `main`; periksa hasil Actions terbaru pada commit yang hendak dipakai. Tes utama kini mengunci versi bahasa/paket, alias, fixture konformansi, benchmark retrieval, serta batas klaim rilis.

> **Kesimpulan utama:** PusingCuk adalah bahasa pemrograman eksperimental dengan jalur Python referensi dan runtime native C yang diuji untuk subset fitur. PusingCuk AI adalah aplikasi/orchestrator MVP di atas model provider yang dapat diganti, bukan model dasar yang dilatih sendiri. Supabase Free sudah memiliki skema catatan proyek pribadi dengan RLS yang diuji di database, tetapi runtime aplikasi PusingCuk masih belum terhubung.

## 1. Status komponen

| Komponen | Status yang dapat dibuktikan | Belum boleh diklaim |
|---|---|---|
| Sintaks `.cuk` | Bahasa dengan grammar, spesifikasi, semantik, contoh, dan tes. Gunakan `.cuk` untuk program baru; `.pusingcuk` tetap kompatibel. | Bahasa stabil/produksi atau kompatibel penuh dengan bahasa lain. |
| Interpreter Python | Implementasi referensi utama yang menentukan perilaku yang dimaksudkan. | Eksekusi kode tidak tepercaya aman hanya karena dibatasi oleh interpreter. |
| Runtime native C | Runtime C11 mandiri yang dibangun dan diuji dengan GCC dan Clang; subset perilaku dipatok lewat fixture. | Semua fitur Python tersedia di native C. |
| Transpiler Python/JavaScript | Target eksperimental dengan subset built-in. | Kesetaraan lintas-target tanpa fixture yang sama. |
| VM/PVM | Eksperimen; mempunyai beberapa regresi keamanan serta batas path tersendiri. | Runtime utama atau sandbox umum. |
| PusingCuk AI CLI | MVP lokal: provider Ollama sebagai default, Gemini sebagai pilihan eksplisit, retrieval leksikal, sitasi tervalidasi, memori lokal opt-in, serta registry tool terbatas. | Foundation model buatan sendiri, chatbot cloud publik, atau kualitas jawaban umum yang sudah tervalidasi secara luas. |
| HTTP AI lokal | Adapter eksperimental ber-token, dibatasi ke loopback, `POST /v1/chat`. | API publik/produksi, multi-tenant, atau sudah memiliki autentikasi per pengguna. |
| Supabase | Dua project Supabase aktif terpisah telah ditemukan; project PusingCuk bersih dan belum terhubung ke runtime. | Chat, user, memori, atau file lokal tersinkron ke database. |

## 2. Bahasa pemrograman `.cuk`

### Versi dan baseline

- **Versi bahasa kontraktual:** `0.5-dev`.
- **Versi paket Python:** `0.8.0.dev0`. Ini metadata paket, bukan versi bahasa.
- **Kontrak built-in:** 21 built-in terkontrak; 17 berstatus didukung oleh native C sebagai built-in penuh. Beberapa konversi skalar memiliki cakupan terbatas; lihat matriks resmi, jangan menghitung semuanya sebagai paritas.
- **Fixture konformansi:** 66 fixture memiliki hasil referensi yang wajib; 59 berstatus wajib pada native C dan 5 secara eksplisit tidak didukung native. Status ini bukan klaim bahwa setiap backend mendukung semua fitur.
- **Jalur yang dipelihara:** `lexer.py → parser.py → ast_nodes.py → evaluator.py` dan runtime `native/pusingcuk.c`.
- **Targets eksperimental:** `compiler/`, `src/`, VM/PVM, dan aplikasi `android-studio/`. Folder atau workflow yang ada bukan bukti rilis stabil.

### Kelebihan

1. Kata kunci berbahasa Indonesia, sintaks yang khas, dan contoh yang membantu pemula.
2. Spesifikasi dan kontrak built-in membuat semantik bisa diperdebatkan, diuji, dan ditingkatkan secara eksplisit.
3. Konformansi Python/C menguji kasus batas, tipe, kesalahan, dan keluaran, bukan hanya contoh sukses.
4. Runtime C memungkinkan penggunaan tanpa Python setelah executable dibangun; Python tetap menjadi acuan perilaku.
5. CI telah menjalankan suite pada Python 3.11/3.12 dan mengompilasi native C dengan GCC/Clang.

### Kekurangan dan batasan

1. Versi bahasa masih development/eksperimental; ekosistem paket, IDE, debugger, dan dokumentasi pihak ketiga belum setara bahasa mapan.
2. Native C adalah subset; file I/O, HTTP, dan sistem modul tidak sepenuhnya tersedia di native sesuai dokumentasi saat ini.
3. Transpiler dan VM bukan baseline kompatibilitas. Jangan memilih target hanya karena direktori atau workflow tersedia.
4. Runtime tidak otomatis menjadi sandbox OS. Jangan menjalankan program tidak tepercaya dengan akses ke rahasia atau data penting.
5. Alias/slang bisa memudahkan ekspresi lokal, tetapi memperbesar beban konsistensi kosakata dan pemahaman pembaca.

### Arah teknis bahasa

**Prioritas tinggi:** pertahankan spesifikasi `0.5-dev` sebagai sumber perilaku; pertahankan kontrak built-in sebagai satu metadata mesin; buat semua perubahan semantik memiliki fixture positif/negatif; pastikan hasil fixture yang sama lulus pada setiap runtime yang diklaim didukung.

**Prioritas berikutnya:** tambah diagnostik konsisten, rapikan onboarding, dan terbitkan artefak Android/Termux hanya setelah binary diuji pada arsitektur yang benar. Jangan memperluas grammar baru untuk AI jika pola `fungsi` + data yang ada mencukupi.

## 3. PusingCuk AI: apa yang sudah dibangun?

### Arsitektur saat ini

```text
pusingcuk-ai CLI / adapter HTTP lokal
                 |
          assistant.py
       /        |        \
  provider   retrieval   ToolRegistry
    |            |         |
  Ollama      indeks 20    aturan .cuk tetap
    |          sumber      budget_threshold
 lokal / loopback
                 |
  sitasi dari source record yang tervalidasi
```

- **Provider lokal:** adapter Ollama, default model `qwen3:4b`, endpoint `127.0.0.1:11434`. Model dan runtime Ollama harus dipasang terpisah dan berjalan pada mesin yang sama. Model Qwen3 4B yang tercantum di Ollama memerlukan unduhan sekitar 2,5 GB; RAM, kecepatan, dan kualitas hasil bergantung perangkat serta konfigurasi.
- **Provider alternatif:** Gemini GenerateContent API, dipilih eksplisit dengan `--provider gemini` dan `GEMINI_API_KEY`. Provider ini mengirim prompt/konteks ke layanan pihak ketiga dan bergantung pada model yang tersedia, kuota, ketentuan akun, serta biaya yang berlaku.
- **Grounding:** indeks berisi **20 dokumen sumber terkurasi**. Seluruh entri tercatat milik repositori PusingCuk, memakai visibility `public-safe`, dan mematok path/commit. Runtime tidak melakukan crawl otomatis terhadap repo lain.
- **Benchmark retrieval:** terdapat **20 kasus benchmark** bahasa Indonesia dengan sumber teratas yang diharapkan. Ini regression set kecil, bukan bukti akurasi umum atau benchmark semantik yang luas.
- **Sitasi:** URL yang ditempel ke jawaban diambil dari sumber tervalidasi, bukan dipercaya dari teks model. Sitasi membuktikan asal sumber, bukan otomatis kebenaran seluruh klaim.
- **Tool:** `knowledge_search` untuk pencarian read-only dan `budget_threshold` untuk menjalankan artefak `.cuk` tetap yang di-hash. Model tidak diberi akses bebas untuk mengirim source code, shell command, path, atau capability arbitrer.
- **Memori:** konteks percakapan aktif bersifat sementara. Catatan proyek harus disimpan secara eksplisit oleh pengguna di penyimpanan lokal; chat tidak otomatis dipersistenkan ke Supabase.
- **HTTP lokal:** adapter loopback dengan bearer token dan batas input/sesi/konkurensi. `/healthz` hanya membuktikan proses hidup, bukan model siap melayani.

### Kelebihan

1. Provider bisa diganti tanpa mengubah bahasa atau semantik runtime.
2. Jalur Ollama tidak membutuhkan API key berbayar, dan permintaan default dibatasi ke loopback.
3. Pengetahuan proyek dikurasi, memiliki provenance, dan tidak digabungkan otomatis dari sumber luar.
4. Tool yang diizinkan memiliki skema input, batas nilai, ID/hash artefak, dan keluaran yang dibatasi.
5. Sebagian besar regresi dapat diuji tanpa model berjalan atau API berbayar menggunakan provider tiruan.

### Kekurangan dan risiko yang tersisa

1. **Bukan model foundation yang dilatih oleh PusingCuk.** PusingCuk mengatur model pihak lain/terinstal, retrieval, memori, sitasi dan tool.
2. Retrieval saat ini adalah pencarian leksikal deterministik, bukan embeddings/vector search. Typo, pertanyaan ambigu, dan paraphrase dapat menurunkan relevansi.
3. 20 kasus benchmark terlalu kecil untuk mengklaim jawaban Indonesia selalu tepat. Butuh evaluasi top-1/top-3, citation precision, penolakan pertanyaan di luar korpus, dan unsupported-claim rate.
4. Keberhasilan CI provider tiruan tidak membuktikan kualitas hasil model Ollama/Gemini yang benar-benar dijalankan di perangkat.
5. Model lokal memerlukan storage/RAM dan runtime tersendiri; belum ada bukti kinerja atau kenyamanan menjalankan model pada setiap HP Android.
6. Adapter HTTP saat ini bukan service publik: belum memiliki identitas per pengguna, TLS terminasi, quota multi-user, observabilitas produksi, incident response, atau mekanisme backup/restore untuk service state.
7. Eksekusi program PusingCuk bukan sandbox OS. Hash tetap dan validasi input adalah safeguard penting, tetapi tidak menggantikan isolasi sistem operasi.

## 4. Hubungan dengan Supabase Free

### Project yang telah diperiksa

| Peran | Project ref | Status saat audit | Keadaan aplikasi |
|---|---|---|---|
| Catatan proyek pribadi (DB schema applied) | `vcvejjpzklpvknxmymgy` | `ACTIVE_HEALTHY`, region `ap-southeast-2` | Tidak ditemukan tabel aplikasi, migration history, atau Edge Function pada pemeriksaan terakhir. |
| Data lama Kawasan Masjid/CORE | `lnpzgrodwnhthcwudebk` | `ACTIVE_HEALTHY`, region `ap-southeast-2` | Database lama memiliki schema/records dan tidak boleh dianggap sudah dimigrasikan ke project PusingCuk. |

Keduanya tetap merupakan database project terpisah meskipun berada dalam organisasi Supabase yang sama. Organisasi terpisah bernama `Pusingcuk` yang muncul pada koneksi akun lain tidak perlu dipakai agar kedua project tetap terisolasi.

### Batas Free yang relevan

Menurut dokumentasi resmi Supabase yang diperiksa pada tanggal audit:

- Maksimal **2 project Free aktif** lintas organisasi tempat pemilik/admin terdaftar; project yang paused tidak dihitung.
- **500 MB database per project**. Ketika ukuran database melewati kuota ini, project Free dapat masuk read-only sampai ukurannya kembali di bawah limit atau rencana diubah.
- **1 GB file storage**, **5 GB egress** pada kuota organisasi, **50.000 monthly active users**, **500.000 Edge Function invocations**, serta **2 juta Realtime messages** dengan batas peak connections yang tercantum pada halaman billing.
- Project Free berpotensi dipause otomatis setelah sekitar **7 hari aktivitas database yang rendah**.
- Free tidak menyertakan backup database otomatis seperti fitur backup berjadwal di paket berbayar. Untuk data penting, rencanakan ekspor privat serta uji restore sendiri.

Sumber primer: [Pricing Supabase](https://supabase.com/pricing), [Billing dan kuota](https://supabase.com/docs/guides/platform/billing-on-supabase), [Free project pausing](https://supabase.com/docs/guides/platform/free-project-pausing), dan [database size limit](https://supabase.com/docs/guides/platform/database-size).

### Peran yang tepat untuk PusingCuk

- Supabase dapat dipakai kelak untuk persistensi terpusat, autentikasi, sinkronisasi lintas perangkat, atau data service setelah kasus penggunaan dan model izinnya ditetapkan.
- Supabase **bukan model AI**, bukan tempat menjalankan Ollama, dan bukan metode melatih model.
- Saat ini aplikasi PusingCuk masih memakai adapter SQLite lokal untuk database abstraction. Project Supabase PusingCuk belum terhubung ke runtime; belum ada data chat/user lokal yang otomatis tersinkron.
- Jangan membuat tabel generik tanpa kebutuhan produk. Untuk fitur pertama, tentukan data minimum, aktor, izin baca/tulis, retensi/penghapusan, lalu buat migration versioned dan kebijakan RLS yang sesuai.
- Jangan pernah menaruh password database, service-role key, atau secret Supabase di repo publik, browser JavaScript, APK, CLI, atau log. Browser hanya boleh memakai publishable key bersama auth/RLS yang benar.
- Project Kawasan/CORE jangan dihapus sebagai efek samping dari integrasi PusingCuk. Pemindahan atau penghapusan repo GitHub tidak dengan sendirinya mematikan Edge Function, cron, database atau webhook yang pernah dideploy.

## 5. Pengelompokan repo agar jelas bagi pengembang baru

| Kelompok | Lokasi | Panduan |
|---|---|---|
| Bahasa dan runtime utama | `SPEC.md`, `lexer.py`, `parser.py`, `ast_nodes.py`, `evaluator.py`, `pusingcuk_new.py`, `native/pusingcuk.c` | Inilah baseline yang dipelihara. |
| Kontrak dan bukti | `library/builtin_contract.json`, `library/kosakata.json`, `tests/conformance/`, `tests/native/`, `tools/conformance.py` | Perubahan bahasa harus mengubah kontrak, implementasi, dan tes yang relevan bersama-sama. |
| AI aplikasi | `library/assistant.py`, `library/local_ai_provider.py`, `library/gemini_ai_provider.py`, `library/knowledge_grounding.py`, `library/ai_tools.py`, `library/local_memory.py`, `library/ai_service.py` | Model provider, retrieval, memori, service, dan tool tetap dipisahkan. |
| Pengetahuan AI | `library/knowledge_index.json`, `docs/AI_KNOWLEDGE_GROUNDING.md`, `docs/AI_ENGINE_READINESS.md`, `docs/AI_ENGINE_MIGRATION_LEDGER.md` | Indeks terkurasi dan tes benchmark; jangan menambahkan crawler repo otomatis. |
| Onboarding dan referensi | `docs/PEMULA.md`, `docs/termux/README.md`, `docs/language/README.md`, `docs/README.md` | Titik awal bagi pembaca baru, termasuk pengguna Android/Termux. |
| Eksperimen/deferred | `compiler/`, `src/`, `android-studio/`, `web/`, `tools/web_workbench.py`, `archive/legacy/` | Label eksperimen, bukan parity/produksi. Jangan dicampur dengan baseline. |
| CI | `.github/workflows/tests.yml`, `.github/workflows/build-test.yml`, workflow Android/release | Tes inti berjalan pada push; workflow Android dan eksperimen tertentu bersifat manual atau terpisah. |

Nama `CORE` pada file historis seperti `docs/integrations/CORE_TOOL_CONTRACT.md` atau `tools/core-rule-runner.mjs` merujuk pada harness kontrak/regresi kompatibilitas yang tersimpan di repo PusingCuk. File ini bukan koneksi ke repo CORE atau ke Supabase lama; harness masih dites CI dan jangan dihapus sebelum fungsi regresinya diganti.

## 6. Roadmap teknis yang disarankan

### P0 — sinkronisasi dan source of truth

- Pertahankan satu entry point bahasa di README dan satu peta status/roadmap.
- Jaga angka indeks sumber, benchmark retrieval, versi paket/bahasa, dan fixture konformansi melalui tes otomatis.
- Koreksi referensi dokumentasi yang mengklaim adapter/runner lama masih berada di jalur runtime AI.
- Pisahkan jelas baseline stabil yang diuji dari eksperimen compiler/VM/APK.

### P1 — kualitas bahasa

- Lanjutkan regression tests untuk nilai batas, diagnostik, error code/exit code, dan kompatibilitas alias.
- Setiap klaim parity harus berdasarkan fixture yang `required` di Python dan native C.
- Jangan menambah grammar, keyword, atau built-in baru sebelum ada spesifikasi, metadata, tes positif/negatif, dan status setiap target.

### P1 — kualitas AI yang terukur

- Tambahkan kueri bahasa Indonesia sehari-hari, typo/slang, kueri ambigu, pertanyaan di luar korpus, dan kasus prompt injection dalam dokumen.
- Ukur retrieval top-1/top-3, citation precision, unsupported-claim rate, refusal behavior, serta kegagalan timeout/kuota/tool-call. Simpan fixture dan hasilnya di repo.
- Tambahkan uji manual pada perangkat yang memang menjalankan Ollama; tandai hasil model/provider dan perangkat secara spesifik.
- Hindari mengeksekusi source code dari model. Tool hanya boleh menerima input sesuai skema terhadap artefak tetap yang direview.

### P2 — integrasi Supabase opsional

- Pilih satu fitur yang benar-benar perlu data lintas perangkat atau autentikasi; jangan hubungkan semua memori tanpa kebutuhan.
- Buat migration versioned untuk project `vcvejjpzklpvknxmymgy`; aktifkan RLS dan tes izin read/write least-privilege.
- Buat integrasi server-side untuk rahasia/operasi privileged. Lakukan smoke test dan security advisors sebelum menyebutnya tersambung.
- Siapkan ekspor privat dan uji restore sebelum data Supabase menjadi satu-satunya penyimpanan penting.

### P3 — layanan AI publik (hanya bila memang diperlukan)

- Tambahkan autentikasi per pengguna, kuota/rate limiting, TLS, deadline/cancellation, monitoring, alerting, incident response, backup/restore, serta rollout/rollback.
- Tentukan batas privasi dan retensi; Gemini secara eksplisit mengirimkan konten prompt ke pihak ketiga.
- Uji keamanan runtime dan model provider sebelum menerima kode atau tindakan yang berasal dari pengguna internet.

## 7. Gates rilis

Jangan menyebut bahasa stabil, AI akurat, service produksi, database terhubung, atau deployment Android tervalidasi kecuali bukti yang sesuai tersedia.

1. CI utama, evaluasi retrieval offline, dan build paket lulus pada commit yang dirilis.
2. Matriks konformansi mencerminkan fixture yang benar-benar lulus.
3. Benchmark AI mempunyai fixture, metrik, serta hasil yang dapat ditinjau.
4. Secret scan dan review keamanan selesai untuk perubahan yang menyentuh provider, memori, database, dan tool.
5. Supabase hanya dinyatakan terhubung setelah smoke test aplikasi nyata sukses; status project `ACTIVE_HEALTHY` saja tidak cukup.
6. Uji perangkat Android fisik dipisahkan dari hasil build/tes Ubuntu.

## 8. Rujukan cepat

- [README proyek](../README.md)
- [Peta struktur repo](REPO_STRUCTURE.md)
- [Spesifikasi bahasa](../SPEC.md)
- [Matriks kompatibilitas](COMPATIBILITY.md)
- [Readiness AI Engine](AI_ENGINE_READINESS.md)
- [Kontrak grounding AI](AI_KNOWLEDGE_GROUNDING.md)
- [Peta project Supabase](integrations/SUPABASE_PROJECTS.md)
- [CI utama](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/tests.yml)
- [Build CLI](https://github.com/rllibo833-sudo/pusingcuk/actions/workflows/build-test.yml)
