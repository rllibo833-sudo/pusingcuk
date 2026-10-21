# Backend Go Eksperimental

Backend ini menghasilkan program Go mandiri dari IR PusingCuk melalui:

```sh
python -m compiler program.cuk --target go -o program.go
go build -o program program.go
./program
```

## Status dukungan

Backend Go adalah **eksperimental dan bertahap**. Daftar sumber kebenaran untuk fixture yang diwajibkan ada di `tests/conformance/go_manifest.json`. Saat ini backend menargetkan subset yang diuji: variabel dan assignment, output, aritmetika dan perbandingan, boolean short-circuit, list, kamus, indexing/mutasi, rentang, kondisi, loop, fungsi dan nilai balik, serta built-in numerik/statistik yang tercakup pada daftar tersebut.

- Fixture yang tercantum harus lulus terhadap expected output/error dan dibandingkan langsung dengan interpreter referensi Python oleh `tools/differential_runner.py`.
- Fixture yang tidak tercantum dilaporkan unsupported untuk Go. Ini bukan PASS dan tidak menjadi klaim kompatibilitas.
- `Input`, penanganan exception `coba`, namespace/atribut, modul/import runtime, JSON/HTML/CSV, file, jaringan, dan kemampuan host belum diklaim didukung kecuali nanti ditambahkan ke daftar fixture setelah implementasi serta pengujian.
- Runtime Go memakai batas langkah, koleksi, dan integer aman; eksekusi program tetap bukan sandbox OS.

## CI

`tools/ci_fixture_matrix.py` membangun program Go terpilih, menjalankannya, dan membandingkan exit code, stdout, kelas error, serta nomor baris terhadap kontrak fixture. `tools/differential_runner.py` juga menghasilkan pasangan perbandingan reference-versus-Go. Menambahkan fixture ke manifest Go hanya boleh dilakukan setelah backend dan test target benar-benar lulus; jangan menambahkan semua fixture hanya untuk memperbesar angka dukungan.
