# Compatibility examples

This directory holds small source files retained to document backward-compatible source formats. New Pusingcuk programs should use the canonical `.cuk` extension; `.pusingcuk` remains supported for older projects.

- `halo.pusingcuk`: legacy-extension equivalent of the root `halo.cuk` example.

Run either from the repository root:

```sh
python pusingcuk_new.py halo.cuk
python pusingcuk_new.py examples/compat/halo.pusingcuk
```
