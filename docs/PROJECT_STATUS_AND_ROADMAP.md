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
| Supabase | Dua project terpisah; tabel catatan proyek PusingCuk sudah memiliki empat policy RLS dan lolos smoke SQL. Runtime tetap belum terhubung. | Chat, user, memori, atau file lokal tersinkron otomatis ke database. |

## 2. Bahasa pemrograman `.cuk`

### Versi dan baseline

- **Versi bahasa kontraktual:** `0.5-dev`.
- **Versi paket Python:** `0.8.0.dev0`. Ini metadata paket, bukan versi bahasa.
- **Kontrak built-in:** 21 built-in terkontrak; 17 berstatus didukung oleh native C sebagai built-in penuh. Beberapa konversi skalar memiliki cakupan terbatas; lihat matriks resmi, jangan menghitung semuanya sebagai paritas.
- **Fixture konformansi:** 67 fixture: 67 wajib pada interpreter referensi Python, 62 wajib pada native C, dan 5 secara eksplisit tidak didukung native. Status ini bukan klaim bahwa setiap backend mendukung semua fitur.
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
  Ollama      indeks 21    aturan .cuk tetap
    |          sumber      budget_threshold
 lokal / loopback
                 |
  sitasi dari source record yang tervalidasi
```

- **Provider lokal:** adapter Ollama, default model `qwen3:4b`, endpoint `127.0.0.1:11434`. Model dan runtime Ollama harus dipasang terpisah dan berjalan pada mesin yang sama. Model Qwen3 4B yang tercantum di Ollama memerlukan unduhan sekitar 2,5 GB; RAM, kecepatan, dan kualitas hasil bergantung perangkat serta konfigurasi.
- **Provider alternatif:** Gemini GenerateContent API, dipilih eksplisit dengan `--provider gemini` dan `GEMINI_API_KEY`. Provider ini mengirim prompt/konteks ke layanan pihak ketiga dan bergantung pada model yang tersedia, kuota, ketentuan akun, serta biaya yang berlaku.
- **Grounding:** indeks berisi **22 dokumen sumber terkurasi**. Seluruh entri tercatat milik repositori PusingCuk, memakai visibility `public-safe`, dan mematok path/commit. Runtime tidak melakukan crawl otomatis terhadap repo lain.
- **Benchmark retrieval:** 22 kasus baseline menghasilkan top-1 **21/21 (100%)** dan top-3 **21/21 (100%)** pada kueri terkurasi. Pada 8 dari 12 kasus adversarial yang memiliki expected source, top-1 **5/8 (62,5%)** dan top-3 **6/8 (75%)**. Metrik ini menilai retrieval leksikal atas fixture kecil, bukan akurasi jawaban model.
- **Sitasi:** URL yang ditempel ke jawaban diambil dari sumber tervalidasi, bukan dipercaya dari teks model. Sitasi membuktikan asal sumber, bukan otomatis kebenaran seluruh klaim.
- **Tool:** `knowledge_search` untuk pencarian read-only dan `budget_threshold` untuk aturan anggaran dan `journal_balance_check` untuk pemeriksaan sekunder total debit/kredit dari artefak `.cuk` tetap yang di-hash. Pemeriksaan jurnal tidak membaca atau memposting buku; model tidak diberi akses bebas ke source code, shell command, path, atau capability arbitrer.
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
3. Benchmark masih kecil. Evaluator offline saat ini mendapatkan citation precision struktural **1/1 (100%)** pada satu kasus uji tautan berbahaya dan menolak tool injection **2/2**. Empat kasus ditandai sebagai perlu klarifikasi/off-topic, tetapi **live model refusal rate belum diukur**; jangan simpulkan model benar-benar menolak tanpa tes provider/model nyata.
4. Keberhasilan CI provider tiruan tidak membuktikan kualitas hasil model Ollama/Gemini yang benar-benar dijalankan di perangkat.
5. Model lokal memerlukan storage/RAM dan runtime tersendiri; belum ada bukti kinerja atau kenyamanan menjalankan model pada setiap HP Android.
6. Adapter HTTP saat ini bukan service publik: belum memiliki identitas per pengguna, TLS terminasi, quota multi-user, observabilitas produksi, incident response, atau mekanisme backup/restore untuk service state.
7. Eksekusi program PusingCuk bukan sandbox OS. Hash tetap dan validasi input adalah safeguard penting, tetapi tidak menggantikan isolasi sistem operasi.

## 4. Hubungan dengan Supabase Free

### Project yang telah diperiksa

| Peran | Project ref | Status saat audit | Keadaan aplikasi |
|---|---|---|---|
| Catatan proyek pribadi (schema applied) | `vcvejjpzklpvknxmymgy` | `ACTIVE_HEALTHY`, region `ap-southeast-2` | `pusingcuk_project_notes` diterapkan; empat policy RLS, smoke SQL lulus, zero advisor lints setelah hardening helper. Runtime belum terhubung. |
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
- Schema versioned `pusingcuk_project_notes` untuk catatan pribadi lintas perangkat sudah diterapkan dan diuji pada tingkat SQL/RLS. Tahap berikutnya adalah klien autentikasi/API yang aman, uji REST end-to-end menggunakan user sungguhan, lalu integrasi opt-in ke aplikasi; runtime SQLite belum tersambung.
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

**Selesai pada audit ini:** `SPEC.md` tetap menjadi kontrak semantik; tes sekarang membandingkan alias terdaftar di spesifikasi dengan lexer Python, alias inti native C, dan metadata kosakata. Tes dokumentasi mengunci versi bahasa/paket, built-in, provenance dan hitungan fixture/index. Peta struktur dan status `ToolRegistry` telah diselaraskan.

**Berikutnya:** pertahankan tes ini sebagai gate setiap perubahan semantik; pisahkan dengan jelas baseline Python/native dari eksperimen compiler/VM/APK.

### P1 — kualitas bahasa

**Selesai pada audit ini:** manifest bertambah menjadi 66 fixture (66 reference-required, 61 native-required, 5 native-unsupported). Dua fixture baru mengunci `bulatkan(2.5/3.5)` ties-to-even dan penolakan boolean sebagai angka, termasuk kelas error, exit code, dan nomor baris.

**Berikutnya:** tambah fixture untuk bug semantik yang benar-benar ditemukan; jangan menambah grammar/keyword/built-in sebelum SPEC, metadata, implementasi, fixture dan label dukungan target diperbarui bersama.

### P1 — kualitas AI yang terukur

**Selesai pada audit ini:** 12 kueri adversarial ditambah (natural, slang, typo, ambigu, off-topic, prompt injection); CI menghitung baseline top-1/top-3 dan adversarial top-1/top-3, uji tautan sitasi struktural, serta tool fail-closed. Provider Ollama/Gemini menormalisasi timeout, rate-limit/kuota, auth, model tidak ditemukan, HTTP server error, dan malformed response menjadi error stabil. Jalankan `python tools/evaluate_live_ai.py --provider ollama` di mesin dengan model lokal; Gemini memerlukan `GEMINI_API_KEY`. Script itu menilai klarifikasi/refusal secara heuristik per kasus, tetapi belum dijalankan untuk provider live dalam audit ini.

**Berikutnya:** ukur unsupported claims dan refusal pada provider/model/perangkat spesifik; review jawaban kasus yang gagal dan jangan menganggap heuristic pass sebagai bukti keamanan atau akurasi umum.

### P2 — integrasi Supabase opsional

**Selesai pada audit ini:** use case catatan proyek pribadi dipilih; dua migration versioned diterapkan ke `vcvejjpzklpvknxmymgy`; RLS owner-only diuji positif/negatif pada dua identitas; grants publik/anon diperiksa; keamanan dan performance advisors kembali zero lints. Tidak ada secret privileged di repo.

**Belum selesai:** REST/Auth smoke test melalui klien aplikasi dengan user sungguhan, adapter sinkronisasi SQLite↔Supabase, dan uji konflik/retensi/penghapusan. Sampai gate itu lewat, runtime tetap offline-first dan jangan klaim sync aktif.

### P3 — layanan AI publik (hanya bila memang diperlukan)

- Tambahkan autentikasi per pengguna, kuota/rate limiting, TLS, deadline/cancellation, monitoring, alerting, incident response, backup/restore, serta rollout/rollback.
- Tentukan batas privasi dan retensi; Gemini secara eksplisit mengirimkan konten prompt ke pihak ketiga.
- Uji keamanan runtime dan model provider sebelum menerima kode atau tindakan yang berasal dari pengguna internet.

## 7. Gates rilis

Audit ini tidak menyatakan bahasa stabil atau AI akurat secara umum. Database Supabase dan RLS sudah diuji langsung melalui SQL; aplikasi belum tersambung ke REST/Auth. Jangan menyebut API produksi atau Android teruji pada perangkat fisik tanpa bukti masing-masing.

1. CI utama, evaluasi retrieval offline, dan build paket lulus pada commit yang dirilis.
2. Matriks konformansi mencerminkan fixture yang benar-benar lulus.
3. Benchmark AI mempunyai fixture, metrik, serta hasil yang dapat ditinjau.
4. Secret scan dan review keamanan selesai untuk perubahan yang menyentuh provider, memori, database, dan tool.
5. Supabase hanya dinyatakan terhubung setelah smoke test aplikasi nyata sukses; status project `ACTIVE_HEALTHY` saja tidak cukup.
6. Uji perangkat Android fisik dipisahkan dari hasil build/tes Ubuntu.
7. Evaluasi refusal live harus menyebut provider, model, waktu, dan heuristic rubric; bila tidak dijalankan, catat sebagai belum terukur.

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
