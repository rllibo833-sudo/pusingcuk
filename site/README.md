# Situs komunitas PusingCuk

Situs perkenalan statis berada di `site/index.html`. Tidak memerlukan framework, bundler, dependensi npm, atau backend.

## Pratinjau lokal

Buka `index.html` langsung di browser, atau jalankan server statis dari root repo:

```sh
python -m http.server 8000 --directory site
```

Kemudian buka `http://localhost:8000`.

## GitHub Pages

Workflow `.github/workflows/pages.yml` memublikasikan folder `site/` melalui GitHub Pages ketika perubahan masuk ke `main`. Jika Pages belum pernah diaktifkan untuk repo, buka **Settings → Pages** dan pilih **GitHub Actions** sebagai build and deployment source.

## Catatan

- Halaman ini adalah situs pengenalan proyek; bukan compiler yang berjalan di browser.
- Contoh `examples/halo.pusingcuk` adalah kode sumber PusingCuk yang ditampilkan di halaman.
- Status fitur ditulis konservatif dan mengarah ke dokumentasi utama untuk detail teknis.
