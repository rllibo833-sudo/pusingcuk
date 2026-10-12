# Pusingcuk Community Website

The static introduction site is located at `site/index.html`. It does not require a framework, bundler, npm dependencies, or a backend.

## Preview locally

Open `index.html` directly in a browser, or start a static server from the repository root:

```sh
python -m http.server 8000 --directory site
```

Then open `http://localhost:8000` on the same device.

## GitHub Pages

The `.github/workflows/pages.yml` workflow publishes the `site/` directory through GitHub Pages when changes reach `main`. If Pages has not been enabled for this repository, open **Settings → Pages** and select **GitHub Actions** as the build and deployment source.

## Notes

- The main page is static HTML/CSS; the compiler does not yet provide a general-purpose templating backend for building arbitrary designs directly from Pusingcuk source.
- The publishing workflow compiles `examples/halo.pusingcuk` to a standalone HTML target named `demo.html`. The resulting link is included on the main page.
- The introduction website and the compiled demo are separate artifacts. Do not claim that the entire landing page is written in Pusingcuk.
- Feature status is described conservatively and links to the main technical documentation.
