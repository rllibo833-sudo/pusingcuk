# PusingCuk Community Website

The static introduction site lives in `site/index.html`. It requires no framework, bundler, npm dependencies, or backend.

## Preview locally

Open `index.html` directly in a browser, or start a static server from the repository root:

```sh
python -m http.server 8000 --directory site
```

Then open `http://localhost:8000` on the same device.

## GitHub Pages

The `.github/workflows/pages.yml` workflow publishes the `site/` directory through GitHub Pages when changes reach `main`. If Pages is not enabled for this repository, open **Settings → Pages** and select **GitHub Actions** as the build and deployment source.

## Notes

- The main page is static HTML/CSS. The compiler does not yet provide a general-purpose templating backend for building arbitrary designs directly from PusingCuk source.
- The publishing workflow compiles `examples/halo.pusingcuk` into a standalone HTML target named `demo.html`. A link to it appears on the main page.
- The introduction website and compiled demo are separate artifacts. The entire landing page is not written in PusingCuk.
- Feature status is described conservatively and linked to the main technical documentation.
