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

- Halaman utama adalah HTML/CSS statis; compiler belum memiliki backend templating untuk membangun halaman desain bebas langsung dari source PusingCuk.
- Workflow publikasi benar-benar mengompilasi `examples/halo.pusingcuk` ke target HTML mandiri sebagai `demo.html`. Link hasil kompilasi ada di halaman utama.
- Situs perkenalan dan contoh hasil compile adalah dua hal terpisah; jangan mengklaim bahwa seluruh landing page telah ditulis dalam bahasa PusingCuk.
- Status fitur ditulis konservatif dan mengarah ke dokumentasi utama untuk detail teknis.
