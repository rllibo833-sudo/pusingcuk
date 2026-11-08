# scripts/

Skrip bantu pengembangan, generator dokumen, dan utilitas instalasi untuk PusingCuk.

Skrip di sini adalah alat bantu (helper), bukan bagian dari runtime bahasa. Untuk
runner dan gate berbasis bukti, lihat `tools/`.

## Isi

| Skrip | Kegunaan |
|---|---|
| `check_alias_sync.py` | Memverifikasi tabel alias di `lexer.py`, `pusingcuk/lexer.py`, `native/pusingcuk.c`, dan `library/kosakata.json` tetap sinkron dengan `SPEC.md`. |
| `gen_docs_from_spec.py` | Menghasilkan bagian dokumen yang dikelola generator dari `SPEC.md` (jangan mengedit manual bagian di dalam marker generator). |
| `build-android.sh` | Membangun artefak Android Studio. |
| `install-termux.sh` | Instalasi cepat di Termux. |
| `test-termux-device.sh` | Uji perangkat Termux nyata; klaim Android memerlukan hasil dari perangkat asli, bukan hanya CI Ubuntu. |

## Menjalankan

```sh
python scripts/check_alias_sync.py
python scripts/gen_docs_from_spec.py
```

## Catatan

- Skrip harus tetap offline-first: jangan menambahkan panggilan jaringan otomatis
  ke runtime inti (lihat `CONTRIBUTING.md`).
- Materi historis dari proyek lain yang sebelumnya salah tempat di direktori ini
  telah dipindahkan ke `archive/legacy/mnemos/`.
