# PusingCuk Community Website

The static introduction site lives in `site/index.html`; the interactive playground is `site/playground.html`. The site requires no npm dependencies, CDN, or backend service.

## Preview locally

From the repository root:

```sh
python -m http.server 8000 --directory site
```

Open `http://localhost:8000` on the same device. The browser runtime runs .cuk locally; curated examples load from `site/examples/playground/`.

## Browser runtime

The playground uses `site/runtime.js`, a bounded JavaScript AST interpreter for the supported .cuk subset. It does not use `eval`, Pyodide, a remote execution API, filesystem access, or network built-ins. Input statements, filesystem operations, and network operations are intentionally unavailable in this browser target. Runtime support is separate from the reference interpreter and other compiler backends.

Run the browser-runtime fixture suite with:

```sh
node tests/test_browser_runtime.js
python tools/check_playground_examples.py
```

## GitHub Pages

The `.github/workflows/pages.yml` workflow validates the reference examples and browser runtime, then publishes the `site/` directory through GitHub Pages when changes reach `main`. If Pages is not enabled for this repository, select **GitHub Actions** in **Settings → Pages**.
