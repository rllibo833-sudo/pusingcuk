# Editor support: VS Code and Acode

The repository ships a TextMate grammar and a minimal VS Code extension manifest under `editors/vscode/`. The grammar highlights core keywords, block terminators, booleans, comments, built-in calls, numbers, and strings in `.cuk` and legacy `.pusingcuk` files. This is editor highlighting only; it does not provide diagnostics, execution, or language-server features.

## Try the VS Code extension locally

1. Open this repository in VS Code.
2. Open the `editors/vscode` folder as an extension development folder, or copy that directory into your VS Code extensions directory.
3. Reload the editor and open an `.cuk` file.

The extension manifest intentionally has no build dependencies. The TextMate grammar is also a portable syntax-definition source for editors that accept TextMate grammars. Acode support depends on the installed Acode version and syntax-highlighting plugin; the repository does not claim that every Acode build can import the VS Code extension directly.

To verify the metadata, parse `editors/vscode/package.json` and `editors/vscode/syntaxes/pusingcuk.tmLanguage.json` as JSON. Syntax highlighting does not change the language contract and does not make unsupported runtime features portable.
