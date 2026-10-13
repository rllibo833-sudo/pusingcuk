# Pusingcuk Language Reference

This page is the map for the complete human-readable language reference. Use it to find the meaning of a keyword, the canonical spelling, its alias, its runtime support, and the rule that must remain consistent.

## Which document answers which question?

| Need | Source |
|---|---|
| What syntax and behavior does the language define? | [`SPEC.md`](../../SPEC.md) |
| What behavior must implementations preserve? | [Semantic contract](../SEMANTIC_CONTRACT.md) |
| What does each technical term mean in English? | [English dictionary](../DICTIONARY.md) |
| What does a term mean in everyday Indonesian? | [Kamus Pusingcuk](../KAMUS_PUSINGCUK.md) |
| What is the cultural context of slang and aliases? | [Slang/alias guide](../KOSAKATA_GENZ.md) and [language style guide](../GAYA_BAHASA.md) |
| Which keywords and aliases are recorded as machine-readable metadata? | [`library/kosakata.json`](../../library/kosakata.json) |
| Which built-ins, argument counts, and target support states are recorded? | [`library/builtin_contract.json`](../../library/builtin_contract.json) |
| Which runtime has actually been tested for a feature? | [Compatibility matrix](../COMPATIBILITY.md), [native runtime guide](../NATIVE_RUNTIME.md), and [conformance fixtures](../CONFORMANCE_FIXTURES.md) |
| How do I start from zero? | [Beginner guide](../PEMULA.md) and [Termux guide](../termux/README.md) |

## Authority and support labels

The language specification is the normative description of syntax and intended behavior. The semantic contract explains how that behavior is tested. The JSON registries help keep vocabulary and built-in metadata aligned with the implementation; they do not override the specification and do not prove runtime support by themselves.

- **Reference (Python):** supported by the modular interpreter, tests, and documentation.
- **Native C tested:** tested in the standalone C runtime for the subset in [the native matrix](../NATIVE_RUNTIME.md).
- **Cross-runtime:** only use this label when a conformance fixture requires both Python (`reference`) and C (`native`) and both pass.
- **Reference-only:** Python supports the feature, but native C support is not claimed.
- **Experimental/deferred:** a prototype exists but is not part of the maintained compatibility baseline.

## Source extension

Use `.cuk` for new programs. The historical `.pusingcuk` extension remains accepted for compatibility. File extension compatibility does not imply that every feature within the file works on every runtime.

## Rules for changing language vocabulary

When changing a keyword or official alias, update the specification and the actual implementations that claim support. Keep these sources aligned:

1. `lexer.py` and its `KEYWORD_ALIASES` table.
2. `native/pusingcuk.c` alias mapping for the official alias set that the C runtime claims.
3. `library/kosakata.json`, including honest per-runtime support status.
4. Positive and negative tests; add a manifest fixture when the result must match between Python and C.
5. This reference and any affected examples.

The current syntax is in maintenance mode: do not add a keyword, alias, or change its meaning without the language owner's explicit approval. See [the full specification](../../SPEC.md) for the official alias list and syntax rules.
